import hashlib
import logging
from dataclasses import dataclass, field
from typing import Optional

from langchain_core.documents import Document
from sqlalchemy.orm import Session

from app.constants import (
    FEEDBACK_ANSWER_PROMPT_MAX_CHARS,
    FEEDBACK_BAD_LIMIT,
    FEEDBACK_COLLECTION_PREFIX,
    FEEDBACK_GOOD_LIMIT,
    FEEDBACK_MAX_DISTANCE,
    FEEDBACK_RETRIEVE_K,
    FeedbackRating,
)
from app.core.config import settings
from app.models.chat import Chat, Message
from app.models.feedback import MessageFeedback
from app.services.embedding.embedding_factory import EmbeddingsFactory
from app.services.vector_store import VectorStoreFactory

logger = logging.getLogger(__name__)


@dataclass
class FeedbackExample:
    question: str
    answer: str
    rating: FeedbackRating
    distance: Optional[float] = None


@dataclass
class FeedbackRetrieval:
    good: list[FeedbackExample] = field(default_factory=list)
    bad: list[FeedbackExample] = field(default_factory=list)


def normalize_question(text: str) -> str:
    """Collapse whitespace and lowercase a question for exact matching."""
    return " ".join(text.lower().split())


def question_fingerprint(text: str) -> str:
    """Stable hash used to detect the same question repeating."""
    return hashlib.sha256(normalize_question(text).encode("utf-8")).hexdigest()


def extract_answer_text(content: str) -> str:
    """Strip citation payload from a stored assistant message."""
    if "__LLM_RESPONSE__" in content:
        return content.split("__LLM_RESPONSE__")[-1].strip()
    return content.strip()


def _truncate(text: str, limit: int = FEEDBACK_ANSWER_PROMPT_MAX_CHARS) -> str:
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "..."


def _feedback_doc_id(feedback_id: int) -> str:
    return f"feedback-{feedback_id}"


def _get_feedback_store(user_id: int):
    embeddings = EmbeddingsFactory.create()
    return VectorStoreFactory.create(
        store_type=settings.VECTOR_STORE_TYPE,
        collection_name=f"{FEEDBACK_COLLECTION_PREFIX}{user_id}",
        embedding_function=embeddings,
    )


def _sync_feedback_vector(feedback: MessageFeedback) -> None:
    """Best-effort index of the rated question for later similarity search."""
    doc_id = _feedback_doc_id(feedback.id)
    try:
        store = _get_feedback_store(feedback.user_id)
        try:
            store.delete([doc_id])
        except Exception:
            pass
        store.add_documents(
            [
                Document(
                    id=doc_id,
                    page_content=feedback.question,
                    metadata={
                        "feedback_id": feedback.id,
                        "rating": feedback.rating,
                        "user_id": feedback.user_id,
                    },
                )
            ]
        )
    except Exception:
        logger.exception("Failed to index chat feedback %s in vector store", feedback.id)


def submit_message_feedback(
    db: Session,
    *,
    chat: Chat,
    message: Message,
    user_id: int,
    rating: FeedbackRating,
    comment: Optional[str] = None,
) -> MessageFeedback:
    """Create or update a rating for an assistant message."""
    if message.role != "assistant":
        raise ValueError("Feedback can only be submitted for assistant messages")

    previous_user_message = (
        db.query(Message)
        .filter(
            Message.chat_id == chat.id,
            Message.role == "user",
            Message.id < message.id,
        )
        .order_by(Message.id.desc())
        .first()
    )
    if not previous_user_message:
        raise ValueError("No user question found for this assistant message")

    question = previous_user_message.content.strip()
    answer = extract_answer_text(message.content)
    fingerprint = question_fingerprint(question)

    feedback = (
        db.query(MessageFeedback)
        .filter(MessageFeedback.message_id == message.id)
        .first()
    )
    if feedback:
        feedback.rating = rating.value
        feedback.comment = comment
        feedback.question = question
        feedback.answer = answer
        feedback.question_fingerprint = fingerprint
    else:
        feedback = MessageFeedback(
            message_id=message.id,
            chat_id=chat.id,
            user_id=user_id,
            rating=rating.value,
            question=question,
            answer=answer,
            question_fingerprint=fingerprint,
            comment=comment,
        )
        db.add(feedback)

    db.commit()
    db.refresh(feedback)
    _sync_feedback_vector(feedback)
    return feedback


def retrieve_similar_feedback(
    db: Session,
    *,
    user_id: int,
    query: str,
) -> FeedbackRetrieval:
    """Find previously rated Q&A pairs for this question or similar ones."""
    result = FeedbackRetrieval()
    fingerprint = question_fingerprint(query)
    seen_ids: set[int] = set()

    exact_rows = (
        db.query(MessageFeedback)
        .filter(
            MessageFeedback.user_id == user_id,
            MessageFeedback.question_fingerprint == fingerprint,
        )
        .order_by(MessageFeedback.updated_at.desc())
        .all()
    )
    for row in exact_rows:
        example = FeedbackExample(
            question=row.question,
            answer=row.answer,
            rating=FeedbackRating(row.rating),
            distance=0.0,
        )
        seen_ids.add(row.id)
        if example.rating == FeedbackRating.GOOD and len(result.good) < FEEDBACK_GOOD_LIMIT:
            result.good.append(example)
        elif example.rating == FeedbackRating.BAD and len(result.bad) < FEEDBACK_BAD_LIMIT:
            result.bad.append(example)

    has_any = (
        db.query(MessageFeedback.id)
        .filter(MessageFeedback.user_id == user_id)
        .first()
    )
    if not has_any:
        return result

    try:
        store = _get_feedback_store(user_id)
        matches = store.similarity_search_with_score(query, k=FEEDBACK_RETRIEVE_K)
    except Exception:
        logger.exception("Failed to retrieve similar chat feedback for user %s", user_id)
        return result

    feedback_ids: list[int] = []
    distances: dict[int, float] = {}
    for item in matches:
        if isinstance(item, tuple):
            doc, score = item
        else:
            doc, score = item, 0.0
        if score is not None and float(score) > FEEDBACK_MAX_DISTANCE:
            continue
        raw_id = (doc.metadata or {}).get("feedback_id")
        if raw_id is None:
            continue
        feedback_id = int(raw_id)
        if feedback_id in seen_ids:
            continue
        feedback_ids.append(feedback_id)
        distances[feedback_id] = float(score)

    if not feedback_ids:
        return result

    rows = (
        db.query(MessageFeedback)
        .filter(
            MessageFeedback.id.in_(feedback_ids),
            MessageFeedback.user_id == user_id,
        )
        .all()
    )
    rows_by_id = {row.id: row for row in rows}
    for feedback_id in feedback_ids:
        row = rows_by_id.get(feedback_id)
        if not row:
            continue
        example = FeedbackExample(
            question=row.question,
            answer=row.answer,
            rating=FeedbackRating(row.rating),
            distance=distances.get(feedback_id),
        )
        if example.rating == FeedbackRating.GOOD and len(result.good) < FEEDBACK_GOOD_LIMIT:
            result.good.append(example)
        elif example.rating == FeedbackRating.BAD and len(result.bad) < FEEDBACK_BAD_LIMIT:
            result.bad.append(example)
        if len(result.good) >= FEEDBACK_GOOD_LIMIT and len(result.bad) >= FEEDBACK_BAD_LIMIT:
            break

    return result


def build_feedback_prompt_block(examples: FeedbackRetrieval) -> str:
    """Render retrieved ratings as prompt guidance for the LLM."""
    if not examples.good and not examples.bad:
        return ""

    parts = [
        "\n\nUser-rated answers to similar previous questions. "
        "Use them to improve quality for this turn."
    ]
    if examples.good:
        parts.append(
            "If the current question is the same or very similar, follow these "
            "highly rated answers closely. Only change them when retrieved "
            "context adds new or conflicting facts:"
        )
        for index, example in enumerate(examples.good, start=1):
            parts.append(
                f"[Preferred example {index}]\n"
                f"Question: {example.question}\n"
                f"Answer: {_truncate(example.answer)}"
            )
    if examples.bad:
        parts.append(
            "Do not repeat these poorly rated answers. Avoid the same mistakes, "
            "tone, or missing information:"
        )
        for index, example in enumerate(examples.bad, start=1):
            parts.append(
                f"[Avoid example {index}]\n"
                f"Question: {example.question}\n"
                f"Answer: {_truncate(example.answer)}"
            )
    return "\n".join(parts)
