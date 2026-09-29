import pytest
from fastapi.testclient import TestClient

from db.database import get_async_db
from main import app
from routers import chat
from services.llm_client import LLMClientError
from services.rate_limit import chat_limiter


class FakeLLMClient:
    def __init__(self, error=None):
        self.error = error
        self.calls = []

    async def chat(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return {
            "response": "Tshimbiluni works on document automation.",
            "message_id": 42,
            "model": "test-model",
            "response_time_ms": 12,
        }


@pytest.fixture
def llm(monkeypatch):
    fake = FakeLLMClient()

    async def no_db():
        yield None

    async def prompt(db_session=None):
        return "system prompt"

    chat_limiter.reset()
    monkeypatch.setattr(chat, "get_llm_client", lambda: fake)
    monkeypatch.setattr(chat, "build_system_prompt", prompt)
    app.dependency_overrides[get_async_db] = no_db
    yield fake
    app.dependency_overrides.pop(get_async_db, None)
    chat_limiter.reset()


def post(client, body, ip="203.0.113.10"):
    return client.post("/chat/message", json=body, headers={"X-Real-IP": ip})


def test_valid_message_returns_saved_reply(llm):
    response = post(TestClient(app), {"message": "What does he work on?"})
    assert response.status_code == 200
    body = response.json()
    assert body["content"].startswith("Tshimbiluni")
    assert body["id"] == 42
    # Generation settings come from the server, never from the request.
    assert set(llm.calls[0]) == {
        "message",
        "session_id",
        "provider",
        "system_instruction",
        "db_session",
    }


@pytest.mark.parametrize(
    "body",
    [
        {"message": "hi", "metadata": {"max_tokens": 100000}},
        {"message": "hi", "model": "gpt-5-pro"},
        {"message": "x" * 1001},
        {"message": "   "},
        {"message": "hi", "session_id": "../../etc"},
    ],
)
def test_rejects_cost_and_injection_controls(llm, body):
    assert post(TestClient(app), body).status_code == 422
    assert llm.calls == []


def test_provider_errors_are_not_exposed(llm):
    llm.error = LLMClientError("OpenAI quota or billing limit has been reached (request ID: req_123)")
    response = post(TestClient(app), {"message": "hi"})
    assert response.status_code == 503
    detail = response.json()["detail"]
    assert "quota" not in detail and "req_123" not in detail


def test_rate_limits_each_visitor(llm, monkeypatch):
    monkeypatch.setenv("CHAT_RATE_LIMIT_PER_MINUTE", "3")
    client = TestClient(app)
    for _ in range(3):
        assert post(client, {"message": "hi"}).status_code == 200

    limited = post(client, {"message": "hi"})
    assert limited.status_code == 429
    assert int(limited.headers["Retry-After"]) > 0
    # Another visitor is unaffected.
    assert post(client, {"message": "hi"}, ip="198.51.100.7").status_code == 200


def test_global_daily_cap_applies_across_visitors(llm, monkeypatch):
    monkeypatch.setenv("CHAT_RATE_LIMIT_GLOBAL_PER_DAY", "2")
    client = TestClient(app)
    assert post(client, {"message": "hi"}, ip="198.51.100.1").status_code == 200
    assert post(client, {"message": "hi"}, ip="198.51.100.2").status_code == 200
    assert post(client, {"message": "hi"}, ip="198.51.100.3").status_code == 429
