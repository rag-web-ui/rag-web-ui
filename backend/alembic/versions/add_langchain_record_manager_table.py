"""add_langchain_record_manager_table

Revision ID: add_langchain_record_manager
Create Date: 2024-03-14 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_langchain_record_manager'
down_revision: Union[str, None] = 'add_file_hash_to_documents'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'langchain_record_manager',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('namespace', sa.String(255), nullable=False),
        sa.Column('doc_id', sa.String(255), nullable=False),
        sa.Column('data', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.Index('idx_namespace_doc_id', 'namespace', 'doc_id')
    )


def downgrade() -> None:
    op.drop_table('langchain_record_manager') 