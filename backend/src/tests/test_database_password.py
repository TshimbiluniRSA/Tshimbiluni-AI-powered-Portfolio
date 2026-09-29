import json
import sys
import types

import asyncpg
import pytest

from sqlalchemy.ext.asyncio import create_async_engine

from db import database


class FakeSecretsManager:
    def __init__(self, passwords):
        self.passwords = list(passwords)
        self.calls = 0

    def get_secret_value(self, SecretId):
        self.calls += 1
        return {"SecretString": json.dumps({"username": "u", "password": self.passwords.pop(0)})}


def install_fake_boto3(monkeypatch, client):
    fake = types.SimpleNamespace(client=lambda service, region_name=None: client)
    monkeypatch.setitem(sys.modules, "boto3", fake)
    monkeypatch.setattr(database, "_cached_password", None)
    monkeypatch.setattr(database, "DATABASE_PASSWORD_SECRET_ID", "rds!db-test")


def test_password_is_cached_briefly(monkeypatch):
    client = FakeSecretsManager(["first", "second"])
    install_fake_boto3(monkeypatch, client)
    clock = [1000.0]
    monkeypatch.setattr(database.time, "monotonic", lambda: clock[0])

    assert database.fetch_database_password() == "first"
    assert database.fetch_database_password() == "first"
    assert client.calls == 1

    # After a rotation, the new password is picked up once the cache expires.
    clock[0] += database.PASSWORD_CACHE_SECONDS + 1
    assert database.fetch_database_password() == "second"
    assert client.calls == 2


@pytest.mark.asyncio
async def test_asyncpg_receives_the_password_callable(monkeypatch):
    """SQLAlchemy must hand asyncpg the callable, not the stale URL password."""
    received = {}

    class StopConnect(Exception):
        pass

    async def fake_connect(*args, **kwargs):
        received.update(kwargs)
        raise StopConnect

    monkeypatch.setattr(asyncpg, "connect", fake_connect)
    engine = create_async_engine(
        "postgresql+asyncpg://portfolio_admin:stale@db.example.com:5432/portfolio",
        connect_args={"password": database._fetch_database_password_async},
    )
    with pytest.raises(StopConnect):
        async with engine.connect():
            pass
    await engine.dispose()

    assert received["password"] is database._fetch_database_password_async
