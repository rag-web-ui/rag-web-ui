from enum import Enum, unique


@unique
class FeedbackRating(str, Enum):
    """User rating for an assistant chat response."""

    GOOD = "good"
    BAD = "bad"


FEEDBACK_COLLECTION_PREFIX = "feedback_u_"
FEEDBACK_RETRIEVE_K = 4
FEEDBACK_MAX_DISTANCE = 0.85
FEEDBACK_GOOD_LIMIT = 2
FEEDBACK_BAD_LIMIT = 2
FEEDBACK_ANSWER_PROMPT_MAX_CHARS = 1500
