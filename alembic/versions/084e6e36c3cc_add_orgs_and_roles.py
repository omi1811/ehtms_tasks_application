"""add task workflow columns

Revision ID: 084e6e36c3cc
Revises: manual_add_orgs_roles
Create Date: 2026-05-23 12:12:42.983023

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "084e6e36c3cc"
down_revision: Union[str, Sequence[str], None] = "manual_add_orgs_roles"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "organizations",
        sa.Column("created_by_super_admin_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_organizations_created_by_super_admin_id_users",
        "organizations",
        "users",
        ["created_by_super_admin_id"],
        ["id"],
    )

    op.add_column("tasks", sa.Column("due_date", sa.DateTime(), nullable=True))
    op.add_column("tasks", sa.Column("image_url", sa.String(length=500), nullable=True))
    op.add_column("tasks", sa.Column("author_id", sa.Integer(), nullable=True))
    op.add_column("tasks", sa.Column("completed_at", sa.DateTime(), nullable=True))
    op.add_column("tasks", sa.Column("assigned_to_id", sa.Integer(), nullable=True))
    op.add_column("tasks", sa.Column("assigned_by_id", sa.Integer(), nullable=True))

    op.execute("UPDATE tasks SET author_id = owner_id WHERE author_id IS NULL")

    op.create_foreign_key("fk_tasks_author_id_users", "tasks", "users", ["author_id"], ["id"])
    op.create_foreign_key(
        "fk_tasks_assigned_to_id_users",
        "tasks",
        "users",
        ["assigned_to_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_tasks_assigned_by_id_users",
        "tasks",
        "users",
        ["assigned_by_id"],
        ["id"],
    )

    op.drop_index(op.f("ix_tasks_owner_id"), table_name="tasks")
    op.drop_index(op.f("ix_tasks_title"), table_name="tasks")
    op.drop_constraint(op.f("tasks_owner_id_fkey"), "tasks", type_="foreignkey")
    op.drop_column("tasks", "updated_at")
    op.drop_column("tasks", "owner_id")


def downgrade() -> None:
    op.add_column("tasks", sa.Column("owner_id", sa.Integer(), nullable=True))
    op.add_column("tasks", sa.Column("updated_at", sa.DateTime(), nullable=True))
    op.execute("UPDATE tasks SET owner_id = author_id WHERE owner_id IS NULL")
    op.alter_column("tasks", "owner_id", nullable=False)
    op.alter_column("tasks", "updated_at", nullable=False)

    op.drop_constraint("fk_tasks_assigned_by_id_users", "tasks", type_="foreignkey")
    op.drop_constraint("fk_tasks_assigned_to_id_users", "tasks", type_="foreignkey")
    op.drop_constraint("fk_tasks_author_id_users", "tasks", type_="foreignkey")
    op.create_foreign_key("tasks_owner_id_fkey", "tasks", "users", ["owner_id"], ["id"])
    op.create_index(op.f("ix_tasks_title"), "tasks", ["title"], unique=False)
    op.create_index(op.f("ix_tasks_owner_id"), "tasks", ["owner_id"], unique=False)

    op.drop_column("tasks", "assigned_by_id")
    op.drop_column("tasks", "assigned_to_id")
    op.drop_column("tasks", "completed_at")
    op.drop_column("tasks", "author_id")
    op.drop_column("tasks", "image_url")
    op.drop_column("tasks", "due_date")

    op.drop_constraint(
        "fk_organizations_created_by_super_admin_id_users",
        "organizations",
        type_="foreignkey",
    )
    op.drop_column("organizations", "created_by_super_admin_id")
