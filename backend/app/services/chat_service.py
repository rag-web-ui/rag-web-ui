import json
import base64
from typing import List, AsyncGenerator
from sqlalchemy.orm import Session
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from app.core.config import settings
from app.models.chat import Message
from app.models.knowledge import KnowledgeBase, Document

async def generate_response(
    query: str,
    messages: dict,
    knowledge_base_ids: List[int],
    chat_id: int,
    db: Session
) -> AsyncGenerator[str, None]:
    try:
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
        embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_API_BASE
        )
        
        # Create a vector store for each knowledge base
        vector_stores = []
        for kb in knowledge_bases:
            documents = db.query(Document).filter(Document.knowledge_base_id == kb.id).all()
            if documents:
                vector_store = Chroma(
                    collection_name=f"kb_{kb.id}",
                    embedding_function=embeddings,
                    persist_directory="./chroma_db"
                )
                print(f"Collection {f'kb_{kb.id}'} count:", vector_store._collection.count())
                vector_stores.append(vector_store)
        
        if not vector_stores:
            error_msg = "I don't have any knowledge base to help answer your question."
            yield f'0:"{error_msg}"\n'
            yield 'd:{"finishReason":"stop","usage":{"promptTokens":0,"completionTokens":0}}\n'
            bot_message.content = error_msg
            db.commit()
            return
        
        # Use first vector store for now
        retriever = vector_stores[0].as_retriever()
        
        # Initialize the language model
        llm = ChatOpenAI(
            temperature=0,
            streaming=True,
            model="gpt-4o",
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_API_BASE
        )

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
        
        # Create history aware retriever
        history_aware_retriever = create_history_aware_retriever(
            llm, 
            retriever,
            contextualize_q_prompt
        )

        # Create QA prompt
        qa_system_prompt = (
            "You are given a user question, and please write clean, concise and accurate answer to the question. "
            "You will be given a set of related contexts to the question, **each starting with a reference number "
            "like [[citation:x]], where x is a number.** Please use the context and cite the context at the end of "
            "each sentence if applicable. Your answer must be correct, accurate and written by an expert using an "
            "unbiased and professional tone. Please limit to 1024 tokens. Do not give any information that is not "
            "related to the question, and do not repeat. Say 'information is missing on' followed by the related topic, "
            "if the given context do not provide sufficient information. **Please cite the contexts with the reference "
            "numbers, in the format [citation:x]. If a sentence comes from multiple contexts, please list all applicable "
            "citations, like [citation:3][citation:5].** Other than code and specific names and citations, your answer "
            "must be written in the same language as the question. concise.\n\nContext: {context} Remember, don't blindly "
            "repeat the contexts verbatim. "
        )
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ])

        # Create QA chain
        question_answer_chain = create_stuff_documents_chain(
            llm,
            qa_prompt
        )

        # Create retrieval chain
        rag_chain = create_retrieval_chain(
            history_aware_retriever,
            question_answer_chain,
        )

        # Generate response
        chat_history = []
        for message in messages["messages"]:
            if message["role"] == "user":
                chat_history.append(HumanMessage(content=message["content"]))
            elif message["role"] == "assistant":
                chat_history.append(AIMessage(content=message["content"]))

        full_response = ""
        async for chunk in rag_chain.astream({
            "input": query,
            "chat_history": chat_history
        }):
            if "context" in chunk:
                serializable_context = []
                for context in chunk["context"]:
                    serializable_doc = {
                        "page_content": context.page_content.replace('"', '\\"'),
                        "metadata": context.metadata,
                    }
                    serializable_context.append(serializable_doc)
                
                # 先替换引号，再序列化
                escaped_context = json.dumps({
                    "context": serializable_context
                })

                # print context
                print(escaped_context)

                # 转成 base64
                base64_context = base64.b64encode(escaped_context.encode()).decode()

                # 连接符号
                separator = "__LLM_RESPONSE__"
                
                yield f'0:"{base64_context}{separator}"\n'
                full_response += base64_context + separator

            if "answer" in chunk:
                answer_chunk = chunk["answer"]
                full_response += answer_chunk
                # Escape quotes and use json.dumps to properly handle special characters
                escaped_chunk = (answer_chunk
                    .replace('"', '\\"')
                    .replace('\n', '\\n'))
                yield f'0:"{escaped_chunk}"\n'
            
        # Update bot message content
        bot_message.content = full_response
        db.commit()
            
    except Exception as e:
        error_message = f"Error generating response: {str(e)}"
        print(error_message)
        yield '3:{text}\n'.format(text=error_message)
        
        # Update bot message with error
        if 'bot_message' in locals():
            bot_message.content = error_message
            db.commit()
    finally:
        db.close()