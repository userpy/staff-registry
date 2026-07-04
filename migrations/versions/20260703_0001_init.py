"""init

Revision ID: 20260703_0001
Revises:
Create Date: 2026-07-03 19:31:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260703_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    gender_enum = postgresql.ENUM("male", "female", name="gender", create_type=False)
    gender_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "employees",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("middle_name", sa.String(length=100), nullable=True),
        sa.Column("phone", sa.String(length=12), nullable=False),
        sa.Column("birth_date", sa.Date(), nullable=False),
        sa.Column("gender", gender_enum, nullable=False),
        sa.Column("photo_path", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_employees_phone", "employees", ["phone"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_employees_phone", table_name="employees")
    op.drop_table("employees")

    gender_enum = postgresql.ENUM("male", "female", name="gender", create_type=False)
    gender_enum.drop(op.get_bind(), checkfirst=True)
