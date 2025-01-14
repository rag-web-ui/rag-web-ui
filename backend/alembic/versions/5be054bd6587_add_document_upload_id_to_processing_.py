"""add_document_upload_id_to_processing_tasks

Revision ID: 5be054bd6587
Revises: fd73eebc87c1
Create Date: 2025-01-14 01:17:24.164593

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5be054bd6587'
down_revision: Union[str, None] = 'fd73eebc87c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. 添加 document_upload_id 字段
    op.execute("""
        ALTER TABLE processing_tasks 
        ADD COLUMN document_upload_id INT,
        ADD CONSTRAINT processing_tasks_document_upload_id_fkey 
        FOREIGN KEY (document_upload_id) REFERENCES document_uploads(id)
    """)


def downgrade() -> None:
    # 1. 删除外键约束和字段
    op.execute("""
        ALTER TABLE processing_tasks 
        DROP FOREIGN KEY processing_tasks_document_upload_id_fkey,
        DROP COLUMN document_upload_id
    """)
