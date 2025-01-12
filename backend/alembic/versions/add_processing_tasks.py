"""add processing tasks table

Revision ID: add_processing_tasks
Revises: initial_migration
Create Date: 2024-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'add_processing_tasks'
down_revision = 'initial_migration'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create processing_tasks table
    op.create_table(
        'processing_tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('knowledge_base_id', sa.Integer(), nullable=True),
        sa.Column('document_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
        sa.ForeignKeyConstraint(['knowledge_base_id'], ['knowledge_bases.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_processing_tasks_id'), 'processing_tasks', ['id'], unique=False)

def downgrade() -> None:
    # Drop processing_tasks table
    op.drop_index(op.f('ix_processing_tasks_id'), table_name='processing_tasks')
    op.drop_table('processing_tasks') 