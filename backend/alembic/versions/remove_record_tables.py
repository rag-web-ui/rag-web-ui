"""remove record tables

Revision ID: remove_record_tables
Revises: final_merge
Create Date: 2024-03-14 13:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'remove_record_tables'
down_revision: Union[str, None] = 'final_merge'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Drop the record_manager and upsertion_record tables
    op.drop_table('record_manager')
    op.drop_table('upsertion_record')

def downgrade() -> None:
    # Recreate the record_manager table
    op.create_table('record_manager',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('namespace', sa.String(255), nullable=False),
        sa.Column('doc_id', sa.String(255), nullable=False),
        sa.Column('data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    # Recreate the upsertion_record table
    op.create_table('upsertion_record',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('namespace', sa.String(255), nullable=False),
        sa.Column('doc_id', sa.String(255), nullable=False),
        sa.Column('data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    # Recreate the indexes
    op.create_index('idx_namespace_doc_id', 'record_manager', ['namespace', 'doc_id'])
    op.create_index('idx_namespace_doc_id', 'upsertion_record', ['namespace', 'doc_id']) 