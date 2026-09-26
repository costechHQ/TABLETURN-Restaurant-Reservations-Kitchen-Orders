"""add payment tracking fields

Revision ID: d566cb2f1049
Revises: c9a971f21d97
Create Date: 2026-09-26 07:48:18.266309

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd566cb2f1049'
down_revision: Union[str, Sequence[str], None] = 'c9a971f21d97'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.alter_column(
        "orders",
        "status",
        existing_type=postgresql.ENUM(
            "placed",
            "preparing",
            "ready",
            "served",
            "paid",
            name="orderstatus",
        ),
        nullable=False,
    )

    op.add_column(
        "payments",
        sa.Column("recorded_by", sa.Integer(), nullable=True),
    )

    op.execute(
        "UPDATE payments SET recorded_by = 9 WHERE recorded_by IS NULL"
    )

    op.alter_column(
        "payments",
        "recorded_by",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.create_index(
        op.f("ix_payments_recorded_by"),
        "payments",
        ["recorded_by"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_payments_recorded_by_users",
        "payments",
        "users",
        ["recorded_by"],
        ["id"],
    )

    op.add_column(
        "processed_events",
        sa.Column(
            "reference",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=True,
        ),
    )

    op.execute(
        "UPDATE processed_events SET reference = 'legacy' "
        "WHERE reference IS NULL"
    )

    op.alter_column(
        "processed_events",
        "reference",
        existing_type=sqlmodel.sql.sqltypes.AutoString(),
        nullable=False,
    )

    op.create_index(
        op.f("ix_users_email"),
        "users",
        ["email"],
        unique=True,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_users_email"),
        table_name="users",
    )

    op.drop_column(
        "processed_events",
        "reference",
    )

    op.drop_constraint(
        "fk_payments_recorded_by_users",
        "payments",
        type_="foreignkey",
    )

    op.drop_index(
        op.f("ix_payments_recorded_by"),
        table_name="payments",
    )

    op.drop_column(
        "payments",
        "recorded_by",
    )

    op.alter_column(
        "orders",
        "status",
        existing_type=postgresql.ENUM(
            "placed",
            "preparing",
            "ready",
            "served",
            "paid",
            name="orderstatus",
        ),
        nullable=True,
    )
