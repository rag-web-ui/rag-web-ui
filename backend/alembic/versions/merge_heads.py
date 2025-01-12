"""merge heads

Revision ID: merge_heads
Revises: add_document_chunks, remove_content_from_chunks
Create Date: 2024-03-14 11:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'merge_heads'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Update the revises to include both parent revisions
revises = ('add_document_chunks', 'remove_content_from_chunks')

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass 