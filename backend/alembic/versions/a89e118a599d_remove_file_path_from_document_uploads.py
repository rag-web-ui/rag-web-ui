"""remove_file_path_from_document_uploads

Revision ID: a89e118a599d
Revises: add_embeddings_service
Create Date: 2024-01-28 23:54:44.398635

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a89e118a599d'
down_revision: Union[str, None] = 'add_embeddings_service'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
   
    pass


def downgrade() -> None:

    pass
