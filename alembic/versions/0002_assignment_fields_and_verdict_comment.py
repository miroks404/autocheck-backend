"""assignment fields and verdict comment

Revision ID: 0002_assignment_fields
Revises: 0001_initial
Create Date: 2026-05-31
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_assignment_fields"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    assignment_status = sa.Enum("draft", "published", name="assignmentstatus")
    assignment_status.create(op.get_bind(), checkfirst=True)
    op.add_column("assignments", sa.Column("technologies", sa.JSON(), nullable=False, server_default="[]"))
    op.add_column("assignments", sa.Column("candidate_instructions", sa.Text(), nullable=False, server_default=""))
    op.add_column(
        "assignments",
        sa.Column("status", assignment_status, nullable=False, server_default="published"),
    )
    op.add_column("submissions", sa.Column("verdict_comment", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("submissions", "verdict_comment")
    op.drop_column("assignments", "status")
    op.drop_column("assignments", "candidate_instructions")
    op.drop_column("assignments", "technologies")
    sa.Enum(name="assignmentstatus").drop(op.get_bind(), checkfirst=True)
