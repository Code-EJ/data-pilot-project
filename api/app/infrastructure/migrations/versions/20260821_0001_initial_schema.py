"""Cria o schema inicial da plataforma.

Revision ID: 20260821_0001
Revises:
Create Date: 2026-08-21 00:00:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260821_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

timestamp = postgresql.TIMESTAMP(timezone=True)


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("created_at", timestamp, nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )

    op.create_table(
        "organizations",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("tax_id", sa.Text(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_by", sa.BigInteger(), nullable=False),
        sa.Column("created_at", timestamp, nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], name="fk_organizations_created_by_users"),
    )

    op.create_table(
        "memberships",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("organization_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("created_by", sa.BigInteger(), nullable=False),
        sa.Column("created_at", timestamp, nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("role IN ('admin', 'usuario')", name="ck_memberships_role"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], name="fk_memberships_organization"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_memberships_user"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], name="fk_memberships_created_by_users"),
        sa.UniqueConstraint("organization_id", "user_id", name="uq_memberships_organization_user"),
    )
    op.create_index("ix_memberships_user_id", "memberships", ["user_id"])

    op.create_table(
        "business_units",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("organization_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], name="fk_business_units_organization"),
        sa.UniqueConstraint("organization_id", "name", name="uq_business_units_organization_name"),
    )

    op.create_table(
        "product_categories",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("organization_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], name="fk_product_categories_organization"),
        sa.UniqueConstraint("organization_id", "name", name="uq_product_categories_organization_name"),
    )

    op.create_table(
        "import_batches",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("organization_id", sa.BigInteger(), nullable=False),
        sa.Column("file_name", sa.Text(), nullable=False),
        sa.Column("uploaded_by", sa.BigInteger(), nullable=False),
        sa.Column("uploaded_at", timestamp, nullable=False, server_default=sa.text("now()")),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("total_records", sa.Integer(), nullable=False),
        sa.Column("valid_records", sa.Integer(), nullable=False),
        sa.Column("error_records", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("duplicate_records", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.CheckConstraint(
            "status IN ('processing', 'completed', 'completed_with_errors', 'failed')",
            name="ck_import_batches_status",
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], name="fk_import_batches_organization"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"], name="fk_import_batches_uploaded_by_users"),
    )
    op.create_index(
        "ix_import_batches_organization_uploaded_at",
        "import_batches",
        ["organization_id", sa.text("uploaded_at DESC")],
    )

    op.create_table(
        "import_errors",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("organization_id", sa.BigInteger(), nullable=False),
        sa.Column("import_batch_id", sa.BigInteger(), nullable=False),
        sa.Column("kind", sa.Text(), nullable=False),
        sa.Column("row_number", sa.Integer(), nullable=False),
        sa.Column("column_name", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=False),
        sa.Column("raw_value", sa.Text(), nullable=True),
        sa.CheckConstraint("kind IN ('error', 'duplicate')", name="ck_import_errors_kind"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], name="fk_import_errors_organization"),
        sa.ForeignKeyConstraint(
            ["import_batch_id"],
            ["import_batches.id"],
            name="fk_import_errors_import_batch",
            ondelete="CASCADE",
        ),
    )

    op.create_table(
        "sales_records",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("organization_id", sa.BigInteger(), nullable=False),
        sa.Column("sale_date", sa.Date(), nullable=False),
        sa.Column("value", sa.Numeric(12, 2), nullable=False),
        sa.Column("category_id", sa.BigInteger(), nullable=False),
        sa.Column("business_unit_id", sa.BigInteger(), nullable=False),
        sa.Column("client_name", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("origin", sa.Text(), nullable=False),
        sa.Column("import_batch_id", sa.BigInteger(), nullable=True),
        sa.Column("created_by", sa.BigInteger(), nullable=False),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        sa.Column("created_at", timestamp, nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", timestamp, nullable=False, server_default=sa.text("now()")),
        sa.Column("deleted_at", timestamp, nullable=True),
        sa.CheckConstraint("origin IN ('import', 'manual')", name="ck_sales_records_origin"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], name="fk_sales_records_organization"),
        sa.ForeignKeyConstraint(["category_id"], ["product_categories.id"], name="fk_sales_records_category"),
        sa.ForeignKeyConstraint(["business_unit_id"], ["business_units.id"], name="fk_sales_records_business_unit"),
        sa.ForeignKeyConstraint(["import_batch_id"], ["import_batches.id"], name="fk_sales_records_import_batch"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], name="fk_sales_records_created_by_users"),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"], name="fk_sales_records_updated_by_users"),
    )
    op.create_index(
        "ix_sales_records_organization_sale_date_active",
        "sales_records",
        ["organization_id", "sale_date"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index(
        "ix_sales_records_organization_unit_category_active",
        "sales_records",
        ["organization_id", "business_unit_id", "category_id"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_table(
        "sales_goals",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("organization_id", sa.BigInteger(), nullable=False),
        sa.Column("business_unit_id", sa.BigInteger(), nullable=False),
        sa.Column("category_id", sa.BigInteger(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("target_value", sa.Numeric(12, 2), nullable=False),
        sa.Column("updated_by", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", timestamp, nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("month BETWEEN 1 AND 12", name="ck_sales_goals_month"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], name="fk_sales_goals_organization"),
        sa.ForeignKeyConstraint(["business_unit_id"], ["business_units.id"], name="fk_sales_goals_business_unit"),
        sa.ForeignKeyConstraint(["category_id"], ["product_categories.id"], name="fk_sales_goals_category"),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"], name="fk_sales_goals_updated_by_users"),
        sa.UniqueConstraint(
            "organization_id",
            "business_unit_id",
            "category_id",
            "year",
            "month",
            name="uq_sales_goals_organization_unit_category_period",
        ),
    )


def downgrade() -> None:
    op.drop_table("sales_goals")
    op.drop_index("ix_sales_records_organization_unit_category_active", table_name="sales_records")
    op.drop_index("ix_sales_records_organization_sale_date_active", table_name="sales_records")
    op.drop_table("sales_records")
    op.drop_table("import_errors")
    op.drop_index("ix_import_batches_organization_uploaded_at", table_name="import_batches")
    op.drop_table("import_batches")
    op.drop_table("product_categories")
    op.drop_table("business_units")
    op.drop_index("ix_memberships_user_id", table_name="memberships")
    op.drop_table("memberships")
    op.drop_table("organizations")
    op.drop_table("users")
