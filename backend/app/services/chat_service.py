import json
import base64
from typing import List, AsyncGenerator, Optional
from sqlalchemy.orm import Session
from langchain.chains import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from app.core.config import settings
from app.models.chat import Message
from app.models.knowledge import KnowledgeBase, Document
from langchain.globals import set_verbose, set_debug
from app.services.vector_store import VectorStoreFactory
from app.services.embedding.embedding_factory import EmbeddingsFactory
from app.services.llm.llm_factory import LLMFactory
from app.services.feedback import build_feedback_prompt_block, retrieve_similar_feedback

set_verbose(False)
set_debug(False)


def _text_frame(text: str) -> str:
    """Encode a Vercel AI data-stream text part."""
    return f"0:{json.dumps(text)}\n"


def _context_payload(docs: list) -> str:
    """Encode retrieved docs as the citation prefix stored with the assistant message."""
    serializable_context = [
        {
            "page_content": doc.page_content.replace('"', '\\"'),
            "metadata": getattr(doc, "metadata", {}) or {},
        }
        for doc in docs
    ]
    encoded = base64.b64encode(
        json.dumps({"context": serializable_context}).encode()
    ).decode()
    return f"{encoded}__LLM_RESPONSE__"


def _answer_text(answer_chunk: object) -> str:
    """Normalize a streamed RAG chunk to plain text."""
    if answer_chunk is None:
        return ""
    if isinstance(answer_chunk, str):
        return answer_chunk
    content = getattr(answer_chunk, "content", None)
    if isinstance(content, str) and content:
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and item.get("type") == "text":
                parts.append(str(item.get("text", "")))
        joined = "".join(parts)
        if joined:
            return joined
    extra = getattr(answer_chunk, "additional_kwargs", None) or {}
    for key in ("reasoning_content", "thinking", "reasoning"):
        value = extra.get(key)
        if isinstance(value, str) and value:
            return value
    return ""


async def generate_response(
    query: str,
    messages: dict,
    knowledge_base_ids: List[int],
    chat_id: int,
    db: Session,
    user_id: Optional[int] = None,
) -> AsyncGenerator[str, None]:
    try:
        # Keep the nginx/proxy connection alive while Ollama warms up.
        yield '0:""\n'

        # Create user message
        user_message = Message(
            content=query,
            role="user",
            chat_id=chat_id
        )
        db.add(user_message)
        db.commit()
        
        # Create bot message placeholder
        bot_message = Message(
            content="",
            role="assistant",
            chat_id=chat_id
        )
        db.add(bot_message)
        db.commit()
        
        # Get knowledge bases and their documents
        knowledge_bases = (
            db.query(KnowledgeBase)
            .filter(KnowledgeBase.id.in_(knowledge_base_ids))
            .all()
        )
        
        # Initialize embeddings
        embeddings = EmbeddingsFactory.create()
        
        # Create a vector store for each knowledge base
        vector_stores = []
        for kb in knowledge_bases:
            documents = db.query(Document).filter(Document.knowledge_base_id == kb.id).all()
            if documents:
                # Use the factory to create the appropriate vector store
                vector_store = VectorStoreFactory.create(
                    store_type=settings.VECTOR_STORE_TYPE,  # 'chroma' or other supported types
                    collection_name=f"kb_{kb.id}",
                    embedding_function=embeddings,
                )
                print(f"Collection {f'kb_{kb.id}'} count:", vector_store._store._collection.count())
                vector_stores.append(vector_store)
        
        if not vector_stores:
            error_msg = "I don't have any knowledge base to help answer your question."
            yield _text_frame(error_msg)
            yield 'd:{"finishReason":"stop","usage":{"promptTokens":0,"completionTokens":0}}\n'
            bot_message.content = error_msg
            db.commit()
            return
        
        # Use first vector store for now
        retriever = vector_stores[0].as_retriever()
        
        # Initialize the language model
        llm = LLMFactory.create()

        chat_history = []
        for message in messages["messages"]:
            if message["role"] == "user":
                chat_history.append(HumanMessage(content=message["content"]))
            elif message["role"] == "assistant":
                # if include __LLM_RESPONSE__, only use the last part
                if "__LLM_RESPONSE__" in message["content"]:
                    message["content"] = message["content"].split("__LLM_RESPONSE__")[-1]
                chat_history.append(AIMessage(content=message["content"]))
        # Current question is passed as `input`; keep prior turns only.
        if chat_history and isinstance(chat_history[-1], HumanMessage):
            chat_history = chat_history[:-1]
        
        # Create contextualize question prompt
        contextualize_q_system_prompt = (
            "Given a chat history and the latest user question "
            "which might reference context in the chat history, "
            "formulate a standalone question which can be understood "
            "without the chat history. Do NOT answer the question, just "
            "reformulate it if needed and otherwise return it as is."
        )
        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ])
        
        # Skip the extra rewrite LLM call on the first turn so streaming starts faster.
        if chat_history:
            retrieval_source = create_history_aware_retriever(
                llm,
                retriever,
                contextualize_q_prompt
            )
            docs = await retrieval_source.ainvoke({
                "input": query,
                "chat_history": chat_history,
            })
        else:
            docs = await retriever.ainvoke(query)

        context_payload = _context_payload(docs)
        yield _text_frame(context_payload)
        full_response = context_payload

        # Create QA prompt
        qa_system_prompt = (
            "You are given a user question, and please write clean, concise and accurate answer to the question. "
            "You will be given a set of related contexts to the question, which are numbered sequentially starting from 1. "
            "Each context has an implicit reference number based on its position in the array (first context is 1, second is 2, etc.). "
            "Please use these contexts and cite them using the format [citation:x] at the end of each sentence where applicable. "
            "Your answer must be correct, accurate and written by an expert using an unbiased and professional tone. "
            "Please limit to 1024 tokens. Do not give any information that is not related to the question, and do not repeat. "
            "Say 'information is missing on' followed by the related topic, if the given context do not provide sufficient information. "
            "If a sentence draws from multiple contexts, please list all applicable citations, like [citation:1][citation:2]. "
            "Other than code and specific names and citations, your answer must be written in the same language as the question. "
            "Be concise.\n\nContext: {context}\n\n"
            "Remember: Cite contexts by their position number (1 for first context, 2 for second, etc.) and don't blindly "
            "repeat the contexts verbatim."
        )
        if user_id is not None:
            try:
                feedback_examples = retrieve_similar_feedback(
                    db, user_id=user_id, query=query
                )
                qa_system_prompt += build_feedback_prompt_block(feedback_examples)
            except Exception:
                print("Failed to retrieve chat feedback examples; continuing without them")
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ])

        # 修改 create_stuff_documents_chain 来自定义 context 格式
        document_prompt = PromptTemplate.from_template("\n\n- {page_content}\n\n")

        # Create QA chain
        question_answer_chain = create_stuff_documents_chain(
            llm,
            qa_prompt,
            document_variable_name="context",
            document_prompt=document_prompt
        )

        async for chunk in question_answer_chain.astream({
            "input": query,
            "chat_history": chat_history,
            "context": docs,
        }):
            answer_chunk = _answer_text(chunk)
            if not answer_chunk:
                continue
            full_response += answer_chunk
            yield _text_frame(answer_chunk)

        yield 'd:{"finishReason":"stop","usage":{"promptTokens":0,"completionTokens":0}}\n'
        bot_message.content = full_response
        db.commit()
            
    except Exception as e:
        error_message = f"Error generating response: {str(e)}"
        print(error_message)
        yield f'3:{json.dumps(error_message)}\n'
        yield 'd:{"finishReason":"error","usage":{"promptTokens":0,"completionTokens":0}}\n'
        
        # Update bot message with error
        if 'bot_message' in locals():
            bot_message.content = error_message
            db.commit()