"""add_file_hash_to_documents

Revision ID: add_file_hash_to_documents
Revises: add_processing_tasks
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_file_hash_to_documents'
down_revision = 'add_processing_tasks'
branch_labels = None
depends_on = None


def upgrade():
    # Add file_hash column to documents table
    op.add_column('documents', sa.Column('file_hash', sa.String(64), nullable=True))
    op.create_index(op.f('ix_documents_file_hash'), 'documents', ['file_hash'], unique=False)


def downgrade():
    # Remove file_hash column from documents table
    op.drop_index(op.f('ix_documents_file_hash'), table_name='documents')
    op.drop_column('documents', 'file_hash') 