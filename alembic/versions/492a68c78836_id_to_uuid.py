"""id to uuid

Revision ID: 492a68c78836
Revises: f35168771426
Create Date: 2025-12-17 13:45:08.344478

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '492a68c78836'
down_revision: Union[str, Sequence[str], None] = 'f35168771426'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
