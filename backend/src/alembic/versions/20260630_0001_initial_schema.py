"""initial schema

Revision ID: 20260630_0001
Revises: 
Create Date: 2026-06-30 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260630_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "github_profiles",
        sa.Column("username", sa.String(length=39), nullable=False),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("public_repos", sa.Integer(), nullable=True),
        sa.Column("followers", sa.Integer(), nullable=True),
        sa.Column("following", sa.Integer(), nullable=True),
        sa.Column("profile_url", sa.String(length=255), nullable=True),
        sa.Column("avatar_url", sa.String(length=500), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("company", sa.String(length=255), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("blog", sa.String(length=500), nullable=True),
        sa.Column("twitter_username", sa.String(length=15), nullable=True),
        sa.Column("hireable", sa.Boolean(), nullable=True),
        sa.Column("last_fetched_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("username"),
    )
    op.create_index("idx_github_followers", "github_profiles", ["followers"])
    op.create_index("idx_github_last_fetched", "github_profiles", ["last_fetched_at"])
    op.create_index("idx_github_public_repos", "github_profiles", ["public_repos"])
    op.create_index(op.f("ix_github_profiles_username"), "github_profiles", ["username"])

    op.create_table(
        "api_usage_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("api_provider", sa.String(length=50), nullable=False),
        sa.Column("endpoint", sa.String(length=255), nullable=True),
        sa.Column("method", sa.String(length=10), nullable=True),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("response_time_ms", sa.Integer(), nullable=True),
        sa.Column("tokens_used", sa.Integer(), nullable=True),
        sa.Column("cost_usd", sa.Float(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("request_metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_api_cost", "api_usage_logs", ["cost_usd"])
    op.create_index("idx_api_provider_created", "api_usage_logs", ["api_provider", "created_at"])
    op.create_index("idx_api_status", "api_usage_logs", ["status_code"])

    op.create_table(
        "chat_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.String(length=255), nullable=False),
        sa.Column("message_type", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("msg_metadata", sa.JSON(), nullable=True),
        sa.Column("response_time_ms", sa.Integer(), nullable=True),
        sa.Column("tokens_used", sa.Integer(), nullable=True),
        sa.Column("model_used", sa.String(length=100), nullable=True),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_chat_rating", "chat_history", ["rating"])
    op.create_index("idx_chat_session_created", "chat_history", ["session_id", "created_at"])
    op.create_index("idx_chat_type", "chat_history", ["message_type"])
    op.create_index(op.f("ix_chat_history_session_id"), "chat_history", ["session_id"])

    op.create_table(
        "cv_metadata",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("filepath", sa.String(length=500), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("file_type", sa.String(length=50), nullable=True),
        sa.Column("version", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("download_count", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_cv_active", "cv_metadata", ["is_active"])
    op.create_index("idx_cv_filename", "cv_metadata", ["filename"])
    op.create_index("idx_cv_version", "cv_metadata", ["version"])

    op.create_table(
        "cvs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(length=100), nullable=True),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column("mime_type", sa.String(length=100), nullable=True),
        sa.Column("full_text", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("skills", sa.JSON(), nullable=True),
        sa.Column("experience", sa.JSON(), nullable=True),
        sa.Column("education", sa.JSON(), nullable=True),
        sa.Column("certifications", sa.JSON(), nullable=True),
        sa.Column("languages_spoken", sa.JSON(), nullable=True),
        sa.Column("parsing_status", sa.String(length=20), nullable=True),
        sa.Column("parsing_error", sa.Text(), nullable=True),
        sa.Column("ai_model_used", sa.String(length=50), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("parsed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_cv_user_active", "cvs", ["user_id", "is_active"])
    op.create_index(op.f("ix_cvs_user_id"), "cvs", ["user_id"])

    op.create_table(
        "linkedin_profiles",
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("headline", sa.String(length=500), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("profile_url", sa.String(length=500), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("industry", sa.String(length=255), nullable=True),
        sa.Column("connections_count", sa.String(length=50), nullable=True),
        sa.Column("profile_image_url", sa.String(length=500), nullable=True),
        sa.Column("last_scraped_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("scraping_successful", sa.Boolean(), nullable=True),
        sa.Column("scraping_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("username"),
    )
    op.create_index("idx_linkedin_last_scraped", "linkedin_profiles", ["last_scraped_at"])
    op.create_index("idx_linkedin_successful", "linkedin_profiles", ["scraping_successful"])
    op.create_index(op.f("ix_linkedin_profiles_username"), "linkedin_profiles", ["username"])

    op.create_table(
        "github_repositories",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("github_id", sa.BigInteger(), nullable=False),
        sa.Column("owner_username", sa.String(length=39), nullable=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("full_name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("html_url", sa.String(length=500), nullable=False),
        sa.Column("language", sa.String(length=50), nullable=True),
        sa.Column("languages_data", sa.JSON(), nullable=True),
        sa.Column("topics", sa.JSON(), nullable=True),
        sa.Column("stargazers_count", sa.Integer(), nullable=True),
        sa.Column("watchers_count", sa.Integer(), nullable=True),
        sa.Column("forks_count", sa.Integer(), nullable=True),
        sa.Column("open_issues_count", sa.Integer(), nullable=True),
        sa.Column("size_kb", sa.Integer(), nullable=True),
        sa.Column("is_fork", sa.Boolean(), nullable=True),
        sa.Column("is_archived", sa.Boolean(), nullable=True),
        sa.Column("is_private", sa.Boolean(), nullable=True),
        sa.Column("default_branch", sa.String(length=100), nullable=True),
        sa.Column("github_created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("github_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("github_pushed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("is_featured", sa.Boolean(), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["owner_username"], ["github_profiles.username"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_repo_featured", "github_repositories", ["is_featured", "display_order"])
    op.create_index("idx_repo_owner_name", "github_repositories", ["owner_username", "name"])
    op.create_index("idx_repo_stars", "github_repositories", ["stargazers_count"])
    op.create_index(op.f("ix_github_repositories_github_id"), "github_repositories", ["github_id"], unique=True)
    op.create_index(op.f("ix_github_repositories_name"), "github_repositories", ["name"])
    op.create_index(op.f("ix_github_repositories_owner_username"), "github_repositories", ["owner_username"])


def downgrade() -> None:
    op.drop_index(op.f("ix_github_repositories_owner_username"), table_name="github_repositories")
    op.drop_index(op.f("ix_github_repositories_name"), table_name="github_repositories")
    op.drop_index(op.f("ix_github_repositories_github_id"), table_name="github_repositories")
    op.drop_index("idx_repo_stars", table_name="github_repositories")
    op.drop_index("idx_repo_owner_name", table_name="github_repositories")
    op.drop_index("idx_repo_featured", table_name="github_repositories")
    op.drop_table("github_repositories")
    op.drop_index(op.f("ix_linkedin_profiles_username"), table_name="linkedin_profiles")
    op.drop_index("idx_linkedin_successful", table_name="linkedin_profiles")
    op.drop_index("idx_linkedin_last_scraped", table_name="linkedin_profiles")
    op.drop_table("linkedin_profiles")
    op.drop_index(op.f("ix_cvs_user_id"), table_name="cvs")
    op.drop_index("idx_cv_user_active", table_name="cvs")
    op.drop_table("cvs")
    op.drop_index("idx_cv_version", table_name="cv_metadata")
    op.drop_index("idx_cv_filename", table_name="cv_metadata")
    op.drop_index("idx_cv_active", table_name="cv_metadata")
    op.drop_table("cv_metadata")
    op.drop_index(op.f("ix_chat_history_session_id"), table_name="chat_history")
    op.drop_index("idx_chat_type", table_name="chat_history")
    op.drop_index("idx_chat_session_created", table_name="chat_history")
    op.drop_index("idx_chat_rating", table_name="chat_history")
    op.drop_table("chat_history")
    op.drop_index("idx_api_status", table_name="api_usage_logs")
    op.drop_index("idx_api_provider_created", table_name="api_usage_logs")
    op.drop_index("idx_api_cost", table_name="api_usage_logs")
    op.drop_table("api_usage_logs")
    op.drop_index(op.f("ix_github_profiles_username"), table_name="github_profiles")
    op.drop_index("idx_github_public_repos", table_name="github_profiles")
    op.drop_index("idx_github_last_fetched", table_name="github_profiles")
    op.drop_index("idx_github_followers", table_name="github_profiles")
    op.drop_table("github_profiles")
