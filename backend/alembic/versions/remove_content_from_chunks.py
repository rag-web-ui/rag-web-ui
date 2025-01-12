"""remove content from chunks

Revision ID: remove_content_from_chunks
Revises: add_langchain_record_manager
Create Date: 2024-03-14 11:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'remove_content_from_chunks'
down_revision: Union[str, None] = 'add_langchain_record_manager'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Drop content column from document_chunks table
    op.drop_column('document_chunks', 'content')

def downgrade() -> None:
    # Add content column back to document_chunks table
    op.add_column('document_chunks', sa.Column('content', sa.Text(), nullable=True)) 