"""remove linkedin and add github statistics snapshot
Revision ID: 20260803_0002
Revises: 20260630_0001
"""

from alembic import op
import sqlalchemy as sa

revision = "20260803_0002"
down_revision = "20260630_0001"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table("linkedin_profiles")
    op.create_table(
        "github_stats_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(39), nullable=False, unique=True),
        sa.Column("profile_json", sa.JSON(), nullable=False),
        sa.Column("total_stars", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_forks", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_watchers", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "total_open_issues", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "total_repository_size_kb",
            sa.BigInteger(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "total_contributions", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "commit_contributions", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "pull_request_contributions",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "issue_contributions", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "pull_request_review_contributions",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column("contribution_period_start", sa.String(10)),
        sa.Column("contribution_period_end", sa.String(10)),
        sa.Column("language_stats_json", sa.JSON(), nullable=False),
        sa.Column("recent_repositories_json", sa.JSON(), nullable=False),
        sa.Column(
            "synced_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_github_stats_snapshots_username",
        "github_stats_snapshots",
        ["username"],
        unique=True,
    )


def downgrade():
    op.drop_table("github_stats_snapshots")
    op.create_table(
        "linkedin_profiles",
        sa.Column("username", sa.String(100), primary_key=True),
        sa.Column("profile_url", sa.String(500), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
