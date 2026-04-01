"""add message feedback columns

Revision ID: a1f4c5d8e9b0
Revises: 3580c0dcd005
Create Date: 2026-03-30 11:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision: str = "a1f4c5d8e9b0"
down_revision: Union[str, None] = "3580c0dcd005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("messages", sa.Column("feedback_type", sa.String(length=10), nullable=True))
    op.add_column("messages", sa.Column("feedback_note", mysql.LONGTEXT(), nullable=True))
    op.add_column("messages", sa.Column("corrected_answer", mysql.LONGTEXT(), nullable=True))
    op.add_column("messages", sa.Column("feedback_query", mysql.LONGTEXT(), nullable=True))
    op.create_index("ix_messages_feedback_type", "messages", ["feedback_type"])


def downgrade() -> None:
    op.drop_index("ix_messages_feedback_type", table_name="messages")
    op.drop_column("messages", "feedback_query")
    op.drop_column("messages", "corrected_answer")
    op.drop_column("messages", "feedback_note")
    op.drop_column("messages", "feedback_type")
