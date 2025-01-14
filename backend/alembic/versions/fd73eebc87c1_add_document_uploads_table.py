"""add document uploads table

Revision ID: fd73eebc87c1
Revises: 59cfa0f1361d
Create Date: 2024-01-13 16:24:07.182834

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fd73eebc87c1'
down_revision = '59cfa0f1361d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'document_uploads',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('knowledge_base_id', sa.Integer(), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_hash', sa.String(64), nullable=False),
        sa.Column('file_size', sa.BigInteger(), nullable=False),
        sa.Column('content_type', sa.String(100), nullable=False),
        sa.Column('temp_path', sa.String(255), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['knowledge_base_id'], ['knowledge_bases.id'], ondelete='CASCADE')
    )
    
    # 添加索引以加速查询
    op.create_index('ix_document_uploads_created_at', 'document_uploads', ['created_at'])
    op.create_index('ix_document_uploads_status', 'document_uploads', ['status'])


def downgrade() -> None:
    op.drop_index('ix_document_uploads_status')
    op.drop_index('ix_document_uploads_created_at')
    op.drop_table('document_uploads')
