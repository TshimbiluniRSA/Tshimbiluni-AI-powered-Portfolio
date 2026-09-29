import pytest

from db.database import make_sync_database_url


@pytest.mark.parametrize(
    ("async_url", "sync_url"),
    [
        (
            "postgresql+asyncpg://user@db.example.com:5432/portfolio?ssl=require",
            "postgresql+psycopg://user@db.example.com:5432/portfolio?sslmode=require",
        ),
        (
            "postgresql+asyncpg://user@db.example.com/portfolio?ssl=true&application_name=api",
            "postgresql+psycopg://user@db.example.com/portfolio?sslmode=require&application_name=api",
        ),
        (
            "postgresql+asyncpg://user@db.example.com/portfolio",
            "postgresql+psycopg://user@db.example.com/portfolio",
        ),
        ("sqlite+aiosqlite:///./data/portfolio.db", "sqlite:///./data/portfolio.db"),
    ],
)
def test_sync_url_uses_libpq_ssl_option(async_url, sync_url):
    assert make_sync_database_url(async_url) == sync_url


def test_encoded_password_is_left_untouched():
    url = "postgresql+asyncpg://user:p%40ss%2Fw%3Frd@db.example.com/portfolio?ssl=require"
    assert make_sync_database_url(url) == (
        "postgresql+psycopg://user:p%40ss%2Fw%3Frd@db.example.com/portfolio?sslmode=require"
    )
