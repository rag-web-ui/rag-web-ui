"""final merge

Revision ID: final_merge
Revises: add_document_chunks, remove_content_from_chunks, remove_langchain_record_manager
Create Date: 2024-03-14 12:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'final_merge'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Update the revises to include all parent revisions
revises = ('add_document_chunks', 'remove_content_from_chunks', 'remove_langchain_record_manager')

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass 