"""add_status_enums

Revision ID: ccce14ac0b1c
Revises: 21ff1ae415e1
Create Date: 2026-07-23 17:31:17.089785

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ccce14ac0b1c'
down_revision: Union[str, Sequence[str], None] = '21ff1ae415e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
