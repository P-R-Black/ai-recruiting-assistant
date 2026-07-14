"""initial setup

Revision ID: 7dee6c6c7d30
Revises: 
Create Date: 2026-07-11 23:16:54.538418

"""
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = '7dee6c6c7d30'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
