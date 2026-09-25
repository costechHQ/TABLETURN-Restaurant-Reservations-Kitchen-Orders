"""add payment reference

Revision ID: c9a971f21d97
Revises: 584c4cfb68c3
Create Date: 2026-09-25 00:02:38.448625

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "c9a971f21d97"
down_revision: Union[str, Sequence[str], None] = "584c4cfb68c3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "payments",
        sa.Column(
            "reference",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=True,
        ),
    )

    op.execute(
        "UPDATE payments SET reference = 'legacy-' || id"
    )

    op.alter_column(
        "payments",
        "reference",
        existing_type=sqlmodel.sql.sqltypes.AutoString(),
        nullable=False,
    )

    op.create_index(
        op.f("ix_payments_reference"),
        "payments",
        ["reference"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_payments_reference"),
        table_name="payments",
    )

    op.drop_column(
        "payments",
        "reference",
    )