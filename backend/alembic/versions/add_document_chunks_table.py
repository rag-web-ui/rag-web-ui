"""add_document_chunks_table

Revision ID: add_document_chunks
Create Date: 2024-03-14 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import JSON


# revision identifiers, used by Alembic.
revision: str = 'add_document_chunks'
down_revision: Union[str, None] = 'add_langchain_record_manager'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'document_chunks',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('kb_id', sa.Integer, nullable=False),
        sa.Column('file_path', sa.String(255), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('metadata', JSON, nullable=True),
        sa.Column('hash', sa.String(64), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.Index('idx_kb_file', 'kb_id', 'file_path'),
        sa.Index('idx_hash', 'hash')
    )


def downgrade() -> None:
    op.drop_table('document_chunks') 