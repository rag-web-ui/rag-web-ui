"""remove langchain record manager table

Revision ID: remove_langchain_record_manager
Revises: merge_heads
Create Date: 2024-03-14 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'remove_langchain_record_manager'
down_revision: Union[str, None] = 'merge_heads'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Drop the langchain_record_manager table
    op.drop_table('langchain_record_manager')

def downgrade() -> None:
    # Recreate the langchain_record_manager table
    op.create_table('langchain_record_manager',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('namespace', sa.String(255), nullable=False),
        sa.Column('doc_id', sa.String(255), nullable=False),
        sa.Column('data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    # Recreate the index
    op.create_index('idx_namespace_doc_id', 'langchain_record_manager', ['namespace', 'doc_id']) 