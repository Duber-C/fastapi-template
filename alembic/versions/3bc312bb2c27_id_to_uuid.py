"""id to uuid

Revision ID: 3bc312bb2c27
Revises: 492a68c78836
Create Date: 2025-12-17 13:47:18.293846

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3bc312bb2c27'
down_revision: Union[str, Sequence[str], None] = '492a68c78836'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
