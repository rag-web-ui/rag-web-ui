"""add_message_feedback_table

Revision ID: a7c4e91b2d10
Revises: 3580c0dcd005
Create Date: 2026-08-17 18:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


revision: str = "a7c4e91b2d10"
down_revision: Union[str, None] = "3580c0dcd005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "message_feedback",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("message_id", sa.Integer(), nullable=False),
        sa.Column("chat_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("rating", sa.String(length=16), nullable=False),
        sa.Column("question", mysql.LONGTEXT(), nullable=False),
        sa.Column("answer", mysql.LONGTEXT(), nullable=False),
        sa.Column("question_fingerprint", sa.String(length=64), nullable=False),
        sa.Column("comment", sa.String(length=1000), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["chat_id"], ["chats.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["message_id"], ["messages.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("message_id", name="uq_message_feedback_message_id"),
    )
    op.create_index(op.f("ix_message_feedback_id"), "message_feedback", ["id"], unique=False)
    op.create_index(
        op.f("ix_message_feedback_message_id"),
        "message_feedback",
        ["message_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_message_feedback_user_id"),
        "message_feedback",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_message_feedback_user_fingerprint",
        "message_feedback",
        ["user_id", "question_fingerprint"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_message_feedback_user_fingerprint", table_name="message_feedback")
    op.drop_index(op.f("ix_message_feedback_user_id"), table_name="message_feedback")
    op.drop_index(op.f("ix_message_feedback_message_id"), table_name="message_feedback")
    op.drop_index(op.f("ix_message_feedback_id"), table_name="message_feedback")
    op.drop_table("message_feedback")
