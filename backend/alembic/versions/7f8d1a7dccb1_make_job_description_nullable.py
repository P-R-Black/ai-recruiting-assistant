"""make job description nullable

Revision ID: 7f8d1a7dccb1
Revises: 45ec22829ec5
Create Date: 2026-10-31 22:47:16.443794

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7f8d1a7dccb1'
down_revision: Union[str, Sequence[str], None] = '45ec22829ec5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.alter_column(
        "jobs",
        "description",
        existing_type=sa.Text(),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "jobs",
        "description",
        existing_type=sa.Text(),
        nullable=False,
    )
    
# def upgrade() -> None:
#     """Upgrade schema."""
#     pass


# def downgrade() -> None:
#     """Downgrade schema."""
#     pass
