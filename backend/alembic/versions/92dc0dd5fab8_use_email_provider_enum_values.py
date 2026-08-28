"""use email provider enum values

Revision ID: 92dc0dd5fab8
Revises: 7d0f72213f05
Create Date: 2026-08-23 10:50:42.931516

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '92dc0dd5fab8'
down_revision: Union[str, Sequence[str], None] = '7d0f72213f05'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE emails ALTER COLUMN provider DROP DEFAULT")

    op.execute("""
        ALTER TABLE emails
        ALTER COLUMN provider TYPE text
        USING provider::text
    """)

    op.execute("DROP TYPE emailprovider")

    op.execute("""
        CREATE TYPE emailprovider AS ENUM (
            'apple_mail',
            'gmail',
            'icloud',
            'outlook',
            'yahoo',
            'other'
        )
    """)

    op.execute("""
        ALTER TABLE emails
        ALTER COLUMN provider TYPE emailprovider
        USING provider::emailprovider
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE emails
        ALTER COLUMN provider TYPE text
        USING provider::text
    """)

    op.execute("DROP TYPE emailprovider")

    op.execute("""
        CREATE TYPE emailprovider AS ENUM (
            'APPLE',
            'GMAIL',
            'ICLOUD',
            'OUTLOOK',
            'YAHOO',
            'OTHER'
        )
    """)

    op.execute("""
        ALTER TABLE emails
        ALTER COLUMN provider TYPE emailprovider
        USING (
            CASE provider
                WHEN 'apple_mail' THEN 'APPLE'
                WHEN 'gmail'      THEN 'GMAIL'
                WHEN 'icloud'     THEN 'ICLOUD'
                WHEN 'outlook'    THEN 'OUTLOOK'
                WHEN 'yahoo'      THEN 'YAHOO'
                WHEN 'other'      THEN 'OTHER'
                ELSE upper(provider)
            END
        )::emailprovider
    """)