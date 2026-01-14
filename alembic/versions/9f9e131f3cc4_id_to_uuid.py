"""id to uuid

Revision ID: 9f9e131f3cc4
Revises: 3bc312bb2c27
Create Date: 2025-12-17 13:59:06.310390

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f9e131f3cc4'
down_revision: Union[str, Sequence[str], None] = '3bc312bb2c27'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
