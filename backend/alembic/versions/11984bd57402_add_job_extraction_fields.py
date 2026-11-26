"""add job extraction fields

Revision ID: 11984bd57402
Revises: 7f8d1a7dccb1
Create Date: 2026-11-18 15:09:29.129406

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '11984bd57402'
down_revision: Union[str, Sequence[str], None] = '7f8d1a7dccb1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    extraction_status_enum = sa.Enum(
        'not_attempted',
        'succeeded',
        'no_description',
        'failed',
        name='jobextractionstatus',
    )

    # Create the PostgreSQL enum type first.
    extraction_status_enum.create(op.get_bind(), checkfirst=True)

    # Add the extraction status column.
    op.add_column(
        'jobs',
        sa.Column(
            'extraction_status',
            extraction_status_enum,
            nullable=False,
            server_default='not_attempted',
        ),
    )

    # Add the extraction method column.
    op.add_column(
        'jobs',
        sa.Column(
            'extraction_method',
            sa.String(length=50),
            nullable=True,
        ),
    )

    # Remove the temporary database default.
    op.alter_column(
        'jobs',
        'extraction_status',
        existing_type=extraction_status_enum,
        server_default=None,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column('jobs', 'extraction_method')
    op.drop_column('jobs', 'extraction_status')

    sa.Enum(
        'not_attempted',
        'succeeded',
        'no_description',
        'failed',
        name='jobextractionstatus',
    ).drop(op.get_bind(), checkfirst=True)