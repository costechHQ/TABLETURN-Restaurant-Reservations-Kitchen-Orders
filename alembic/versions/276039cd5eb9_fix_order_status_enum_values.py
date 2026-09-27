from typing import Sequence, Union

from alembic import op


revision: str = "276039cd5eb9"
down_revision: Union[str, Sequence[str], None] = "1016ce29460e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        ALTER TYPE orderstatus RENAME TO orderstatus_old
    """)

    op.execute("""
        CREATE TYPE orderstatus AS ENUM (
            'placed',
            'preparing',
            'ready',
            'served',
            'paid'
        )
    """)

    op.execute("""
        ALTER TABLE orders
        ALTER COLUMN status
        TYPE orderstatus
        USING LOWER(status::text)::orderstatus
    """)

    op.execute("""
        DROP TYPE orderstatus_old
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TYPE orderstatus RENAME TO orderstatus_old
    """)

    op.execute("""
        CREATE TYPE orderstatus AS ENUM (
            'PLACED',
            'PREPARING',
            'READY',
            'SERVED'
        )
    """)

    op.execute("""
        ALTER TABLE orders
        ALTER COLUMN status
        TYPE orderstatus
        USING UPPER(status::text)::orderstatus
    """)

    op.execute("""
        DROP TYPE orderstatus_old
    """)