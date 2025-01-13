"""initial schema

Revision ID: initial_schema
Revises: 
Create Date: 2024-01-13 15:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('username', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_superuser', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )

    # Create knowledge_bases table
    op.create_table(
        'knowledge_bases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', mysql.LONGTEXT(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('file_path', sa.String(255), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('content_type', sa.String(100), nullable=True),
        sa.Column('file_hash', sa.String(64), nullable=True),
        sa.Column('knowledge_base_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['knowledge_base_id'], ['knowledge_bases.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('knowledge_base_id', 'file_name', name='uq_kb_file_name')
    )

    # Create document_chunks table
    op.create_table(
        'document_chunks',
        sa.Column('id', sa.String(64), nullable=False),
        sa.Column('kb_id', sa.Integer(), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('hash', sa.String(64), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )

    # Create chats table
    op.create_table(
        'chats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create chat_knowledge_bases table (association table)
    op.create_table(
        'chat_knowledge_bases',
        sa.Column('chat_id', sa.Integer(), nullable=False),
        sa.Column('knowledge_base_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['chat_id'], ['chats.id'], ),
        sa.ForeignKeyConstraint(['knowledge_base_id'], ['knowledge_bases.id'], ),
        sa.PrimaryKeyConstraint('chat_id', 'knowledge_base_id')
    )

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('chat_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('content', mysql.LONGTEXT(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['chat_id'], ['chats.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create processing_tasks table
    op.create_table(
        'processing_tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('knowledge_base_id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, default='pending'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
        sa.ForeignKeyConstraint(['knowledge_base_id'], ['knowledge_bases.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('idx_kb_file_name', 'document_chunks', ['kb_id', 'file_name'])
    op.create_index('idx_hash', 'document_chunks', ['hash'])
    op.create_index('idx_file_hash', 'documents', ['file_hash'])

def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_hash', table_name='document_chunks')
    op.drop_index('idx_kb_file_name', table_name='document_chunks')
    op.drop_index('idx_file_hash', table_name='documents')

    # Drop tables in reverse order
    op.drop_table('processing_tasks')
    op.drop_table('messages')
    op.drop_table('chat_knowledge_bases')
    op.drop_table('chats')
    op.drop_table('document_chunks')
    op.drop_table('documents')
    op.drop_table('knowledge_bases')
    op.drop_table('users') 