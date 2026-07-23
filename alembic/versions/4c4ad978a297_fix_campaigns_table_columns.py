"""fix campaigns table columns

Revision ID: 4c4ad978a297
Revises: 5907eb69e96d
Create Date: 2026-07-23 22:02:50.049203

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4c4ad978a297'
down_revision: Union[str, Sequence[str], None] = '5907eb69e96d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
