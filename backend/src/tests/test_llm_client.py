import importlib.util
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock

import pytest

# The production dependency is installed by backend CI. Provide a tiny SDK shape
# for this isolated test container when dependencies have not been installed.
if importlib.util.find_spec("openai") is None:
    openai = ModuleType("openai")

    class OpenAIError(Exception):
        pass

    class AsyncOpenAI:
        def __init__(self, **kwargs):
            self.responses = SimpleNamespace(create=AsyncMock())

    openai.AsyncOpenAI = AsyncOpenAI
    for name in (
        "APIConnectionError",
        "APIStatusError",
        "APITimeoutError",
        "AuthenticationError",
        "BadRequestError",
        "NotFoundError",
        "RateLimitError",
    ):
        setattr(openai, name, type(name, (OpenAIError,), {}))
    sys.modules["openai"] = openai

from services.llm_client import LLMClient, LLMClientError, OpenAIProvider


@pytest.fixture
def provider(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-not-real")
    monkeypatch.setenv("OPENAI_CONTEXT_MESSAGE_LIMIT", "2")
    instance = OpenAIProvider()
    instance.client.responses.create = AsyncMock()
    return instance


def response(text="Hello", model="gpt-5-mini", total=7):
    return SimpleNamespace(
        output_text=text,
        model=model,
        id="resp_test",
        usage=SimpleNamespace(input_tokens=4, output_tokens=3, total_tokens=total),
    )


def test_missing_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    instance = OpenAIProvider()
    with pytest.raises(LLMClientError, match="OPENAI_API_KEY"):
        instance._require_client()


@pytest.mark.asyncio
async def test_success_contract_usage_instruction_roles_limit_and_model_override(
    provider,
):
    provider.client.responses.create.return_value = response(model="gpt-4.1-mini")
    result = await provider.generate_response(
        "current",
        model="gpt-4.1-mini",
        system_instruction="portfolio persona",
        context=[
            {"role": "user", "content": "discarded"},
            {"role": "model", "content": "prior answer"},
            {"role": "human", "content": "prior question"},
        ],
        temperature=0.2,
    )

    options = provider.client.responses.create.await_args.kwargs
    assert options["model"] == "gpt-4.1-mini"
    assert options["instructions"] == "portfolio persona"
    assert options["input"] == [
        {"role": "assistant", "content": "prior answer"},
        {"role": "user", "content": "prior question"},
        {"role": "user", "content": "current"},
    ]
    assert options["temperature"] == 0.2
    assert result == {
        "content": "Hello",
        "model": "gpt-4.1-mini",
        "tokens_used": 7,
        "metadata": {
            "provider": "openai",
            "input_tokens": 4,
            "output_tokens": 3,
            "response_id": "resp_test",
        },
    }


@pytest.mark.asyncio
async def test_gpt5_uses_reasoning_but_not_temperature(provider):
    provider.client.responses.create.return_value = response()
    await provider.generate_response("hello", temperature=0.9)
    options = provider.client.responses.create.await_args.kwargs
    assert options["reasoning"] == {"effort": "low"}
    assert "temperature" not in options


@pytest.mark.asyncio
async def test_empty_response(provider):
    provider.client.responses.create.return_value = response(text="  ")
    with pytest.raises(LLMClientError, match="empty response"):
        await provider.generate_response("hello")


@pytest.mark.asyncio
async def test_api_failure_is_secret_safe(provider):
    provider.client.responses.create.side_effect = RuntimeError("internal details")
    with pytest.raises(LLMClientError, match="Unexpected OpenAI API error") as error:
        await provider.generate_response("sensitive user text")
    assert "test-key-not-real" not in str(error.value)
    assert "sensitive user text" not in str(error.value)


@pytest.mark.asyncio
async def test_stream_yields_only_text_deltas(provider):
    async def events():
        yield SimpleNamespace(type="response.created")
        yield SimpleNamespace(type="response.output_text.delta", delta="Hi")
        yield SimpleNamespace(type="response.output_text.done", text="Hi")
        yield SimpleNamespace(type="response.output_text.delta", delta=" there")

    provider.client.responses.create.return_value = events()
    chunks = [chunk async for chunk in provider.stream_response("hello")]
    assert chunks == ["Hi", " there"]
    assert provider.client.responses.create.await_args.kwargs["stream"] is True


@pytest.mark.asyncio
async def test_usage_log_provider(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-not-real")
    client = LLMClient()
    db = SimpleNamespace(add=AsyncMock(), commit=AsyncMock())
    db.add = lambda value: setattr(db, "entry", value)
    await client._log_api_usage(db, model="gpt-5-mini", tokens_used=5)
    assert db.entry.api_provider == "openai"
    assert db.entry.request_metadata == {
        "model": "gpt-5-mini",
        "provider": "openai",
    }


@pytest.mark.asyncio
async def test_llm_chat_response_contract(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-not-real")
    client = LLMClient()
    client.provider_client.generate_response = AsyncMock(
        return_value={
            "content": "answer",
            "model": "gpt-5-mini",
            "tokens_used": 9,
            "metadata": {"provider": "openai"},
        }
    )
    result = await client.chat("question", session_id="session")
    assert set(result) == {
        "response",
        "session_id",
        "model",
        "tokens_used",
        "response_time_ms",
        "metadata",
    }
    assert result["response"] == "answer"
    assert result["session_id"] == "session"
