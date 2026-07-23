"""add_status_enums

Revision ID: 5b2557b000ae
Revises: ccce14ac0b1c
Create Date: 2026-07-23 17:31:37.306818

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5b2557b000ae'
down_revision: Union[str, Sequence[str], None] = 'ccce14ac0b1c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
