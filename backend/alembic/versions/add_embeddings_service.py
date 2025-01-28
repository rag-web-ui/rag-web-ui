"""add embeddings service

Revision ID: add_embeddings_service
Revises: 3580c0dcd005
Create Date: 2024-01-28 13:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'add_embeddings_service'
down_revision = '3580c0dcd005'
branch_labels = None
depends_on = None

def upgrade():
    # 添加 embeddings_service 和 embeddings_config 列
    op.add_column('knowledge_bases', sa.Column('embeddings_service', 
        mysql.ENUM('OPENAI', 'OLLAMA', name='embeddingsservicetype'),
        nullable=False,
        server_default='OPENAI'
    ))
    op.add_column('knowledge_bases', sa.Column('embeddings_config', 
        sa.JSON,
        nullable=True
    ))

def downgrade():
    # 删除列
    op.drop_column('knowledge_bases', 'embeddings_config')
    op.drop_column('knowledge_bases', 'embeddings_service') 