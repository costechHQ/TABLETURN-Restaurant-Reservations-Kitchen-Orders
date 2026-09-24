"""add total amount to order items

Revision ID: 584c4cfb68c3
Revises: a0401b414c4e
Create Date: 2026-09-24 13:49:05.592874
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "584c4cfb68c3"
down_revision: Union[str, Sequence[str], None] = "a0401b414c4e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "order_items",
        sa.Column("total_amount", sa.Numeric(), nullable=True),
    )

    op.execute("""
        UPDATE order_items
        SET total_amount = qty * unit_price
    """)

    op.alter_column(
        "order_items",
        "total_amount",
        nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column("order_items", "total_amount")