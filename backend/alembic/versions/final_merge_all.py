"""final merge all

Revision ID: final_merge_all
Revises: add_document_chunks, remove_content_from_chunks, remove_langchain_record_manager, remove_record_tables
Create Date: 2024-03-14 13:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'final_merge_all'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Update the revises to include all parent revisions
revises = ('add_document_chunks', 'remove_content_from_chunks', 'remove_langchain_record_manager', 'remove_record_tables')

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass 