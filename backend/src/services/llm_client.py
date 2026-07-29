import logging
import os
from datetime import datetime, timezone
from enum import Enum
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AsyncOpenAI,
    AuthenticationError,
    BadRequestError,
    NotFoundError,
    RateLimitError,
)
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import APIUsageLog, ChatHistory
from schemas import MessageType

logger = logging.getLogger(__name__)


class ModelProvider(str, Enum):
    """Supported model providers."""

    OPENAI = "openai"


class LLMClientError(Exception):
    """A safe, user-readable LLM client error."""


class OpenAIProvider:
    """OpenAI Responses API provider."""

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-5-mini")
        self.max_tokens = int(
            os.getenv("OPENAI_MAX_OUTPUT_TOKENS", os.getenv("MAX_TOKENS", "800"))
        )
        self.reasoning_effort = os.getenv("OPENAI_REASONING_EFFORT", "low")
        self.timeout_seconds = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "60"))
        self.context_message_limit = int(
            os.getenv("OPENAI_CONTEXT_MESSAGE_LIMIT", "10")
        )
        self.client = (
            AsyncOpenAI(api_key=self.api_key, timeout=self.timeout_seconds)
            if self.api_key
            else None
        )
        if not self.api_key:
            logger.warning(
                "OpenAI provider is disabled: OPENAI_API_KEY is not configured"
            )

    def _require_client(self) -> AsyncOpenAI:
        if self.client is None:
            raise LLMClientError("OPENAI_API_KEY is not configured")
        return self.client

    def _build_input_messages(
        self, message: str, context: Optional[List[Dict[str, str]]]
    ) -> List[Dict[str, str]]:
        messages: List[Dict[str, str]] = []
        recent_context = (
            (context or [])[-self.context_message_limit :]
            if self.context_message_limit > 0
            else []
        )
        for item in recent_context:
            role = str(item.get("role", "")).lower()
            if role in {"user", "human"}:
                mapped_role = "user"
            elif role in {"assistant", "model", "ai"}:
                mapped_role = "assistant"
            else:
                continue
            messages.append(
                {"role": mapped_role, "content": str(item.get("content", ""))}
            )
        messages.append({"role": "user", "content": message})
        return messages

    @staticmethod
    def _supports_temperature(model: str) -> bool:
        return not model.lower().startswith("gpt-5")

    def _build_request_options(
        self,
        message: str,
        model: Optional[str],
        context: Optional[List[Dict[str, str]]],
        system_instruction: Optional[str],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        model_name = model or self.model
        options: Dict[str, Any] = {
            "model": model_name,
            "input": self._build_input_messages(message, context),
            "max_output_tokens": kwargs.get("max_tokens", self.max_tokens),
        }
        if system_instruction:
            options["instructions"] = system_instruction
        if model_name.lower().startswith("gpt-5") and self.reasoning_effort:
            options["reasoning"] = {"effort": self.reasoning_effort}
        temperature = kwargs.get("temperature")
        if temperature is not None and self._supports_temperature(model_name):
            options["temperature"] = temperature
        return options

    @staticmethod
    def _extract_usage(response: Any) -> Tuple[int, int, int]:
        usage = getattr(response, "usage", None)
        input_tokens = getattr(usage, "input_tokens", 0) or 0
        output_tokens = getattr(usage, "output_tokens", 0) or 0
        total_tokens = getattr(usage, "total_tokens", 0) or 0
        return input_tokens, output_tokens, total_tokens

    def _convert_error(self, error: Exception, model: str) -> LLMClientError:
        status = getattr(error, "status_code", None)
        request_id = getattr(error, "request_id", None)
        category = type(error).__name__
        logger.error(
            "OpenAI request failed provider=openai model=%s category=%s status=%s request_id=%s",
            model,
            category,
            status,
            request_id,
        )
        if isinstance(error, AuthenticationError):
            message = "OpenAI authentication failed; verify OPENAI_API_KEY"
        elif isinstance(error, RateLimitError):
            code = getattr(error, "code", None)
            if code == "insufficient_quota" or "quota" in str(error).lower():
                message = "OpenAI quota or billing limit has been reached"
            else:
                message = "OpenAI rate limit reached; please try again shortly"
        elif isinstance(error, NotFoundError):
            message = f"OpenAI model '{model}' was not found or is unavailable"
        elif isinstance(error, BadRequestError):
            message = (
                "OpenAI rejected the model request; verify the model and parameters"
            )
        elif isinstance(error, APITimeoutError):
            message = "OpenAI request timed out; please try again"
        elif isinstance(error, APIConnectionError):
            message = "Unable to connect to OpenAI; please try again"
        elif isinstance(error, APIStatusError):
            message = (
                f"OpenAI API request failed with HTTP status {status or 'unknown'}"
            )
        else:
            message = "Unexpected OpenAI API error"
        if request_id:
            message += f" (request ID: {request_id})"
        return LLMClientError(message)

    async def generate_response(
        self,
        message: str,
        model: Optional[str] = None,
        context: Optional[List[Dict[str, str]]] = None,
        system_instruction: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        client = self._require_client()
        options = self._build_request_options(
            message, model, context, system_instruction, **kwargs
        )
        try:
            response = await client.responses.create(**options)
        except LLMClientError:
            raise
        except Exception as error:
            raise self._convert_error(error, options["model"]) from error

        generated_text = (getattr(response, "output_text", None) or "").strip()
        if not generated_text:
            raise LLMClientError("OpenAI returned an empty response")
        input_tokens, output_tokens, total_tokens = self._extract_usage(response)
        actual_model = getattr(response, "model", None) or options["model"]
        return {
            "content": generated_text,
            "model": actual_model,
            "tokens_used": total_tokens,
            "metadata": {
                "provider": "openai",
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "response_id": getattr(response, "id", None),
            },
        }

    async def stream_response(
        self,
        message: str,
        model: Optional[str] = None,
        context: Optional[List[Dict[str, str]]] = None,
        system_instruction: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        client = self._require_client()
        options = self._build_request_options(
            message, model, context, system_instruction, **kwargs
        )
        options["stream"] = True
        try:
            stream = await client.responses.create(**options)
            async for event in stream:
                if getattr(event, "type", None) == "response.output_text.delta":
                    delta = getattr(event, "delta", None)
                    if delta:
                        yield delta
        except LLMClientError:
            raise
        except Exception as error:
            raise self._convert_error(error, options["model"]) from error


class LLMClient:
    """Unified client preserving the application's existing LLM interface."""

    def __init__(self) -> None:
        self.provider_client = OpenAIProvider()
        self.max_tokens = int(
            os.getenv("OPENAI_MAX_OUTPUT_TOKENS", os.getenv("MAX_TOKENS", "800"))
        )
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        logger.info("LLM client initialized with provider=openai")

    async def chat(
        self,
        message: str,
        session_id: Optional[str] = None,
        model: Optional[str] = None,
        provider: Optional[ModelProvider] = None,
        context: Optional[List[Dict[str, str]]] = None,
        system_instruction: Optional[str] = None,
        db_session: Optional[AsyncSession] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Send a chat message and return the established response contract."""
        start_time = datetime.now(timezone.utc)
        try:
            conversation_history = []
            if session_id and db_session:
                conversation_history = await self._get_conversation_history(
                    db_session, session_id
                )
            response_data = await self.provider_client.generate_response(
                message=message,
                model=model,
                context=context or conversation_history,
                system_instruction=system_instruction,
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                temperature=kwargs.get("temperature", self.temperature),
            )
            response_time_ms = int(
                (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            )
            response_content = (response_data.get("content") or "").strip()
            if not response_content:
                raise LLMClientError("OpenAI returned an empty response")
            if session_id and db_session:
                await self._save_chat_messages(
                    db_session,
                    session_id,
                    message,
                    response_content,
                    response_time_ms,
                    response_data.get("model"),
                    response_data.get("tokens_used"),
                    response_data.get("metadata", {}),
                )
            if db_session:
                await self._log_api_usage(
                    db_session,
                    response_data.get("model"),
                    response_data.get("tokens_used"),
                    response_time_ms,
                    success=True,
                )
            return {
                "response": response_content,
                "session_id": session_id,
                "model": response_data.get("model"),
                "tokens_used": response_data.get("tokens_used"),
                "response_time_ms": response_time_ms,
                "metadata": response_data.get("metadata", {}),
            }
        except Exception as error:
            if db_session:
                await self._log_api_usage(
                    db_session,
                    model=model,
                    response_time_ms=int(
                        (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                    ),
                    error_message=str(error),
                    success=False,
                )
            logger.error(
                "LLM chat failed provider=openai model=%s category=%s",
                model or self.provider_client.model,
                type(error).__name__,
            )
            if isinstance(error, LLMClientError):
                raise
            raise LLMClientError(
                "Unexpected error while getting an OpenAI response"
            ) from error

    async def stream_chat(
        self,
        message: str,
        session_id: Optional[str] = None,
        model: Optional[str] = None,
        provider: Optional[ModelProvider] = None,
        context: Optional[List[Dict[str, str]]] = None,
        system_instruction: Optional[str] = None,
        db_session: Optional[AsyncSession] = None,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        """Stream plain text chunks from the configured provider."""
        conversation_history = context
        if conversation_history is None and session_id and db_session:
            conversation_history = await self._get_conversation_history(
                db_session, session_id
            )
        async for chunk in self.provider_client.stream_response(
            message=message,
            model=model,
            context=conversation_history,
            system_instruction=system_instruction,
            **kwargs,
        ):
            yield chunk

    async def _get_conversation_history(
        self, session: AsyncSession, session_id: str, limit: int = 10
    ) -> List[Dict[str, str]]:
        try:
            from sqlalchemy import desc, select

            stmt = (
                select(ChatHistory)
                .where(ChatHistory.session_id == session_id)
                .order_by(desc(ChatHistory.created_at))
                .limit(limit * 2)
            )
            result = await session.execute(stmt)
            messages = result.scalars().all()
            conversation = [
                {
                    "role": (
                        "user" if msg.message_type == MessageType.USER else "assistant"
                    ),
                    "content": msg.content,
                }
                for msg in reversed(messages)
            ]
            return conversation[-limit:]
        except Exception as error:
            logger.warning("Failed to get conversation history: %s", error)
            return []

    async def _save_chat_messages(
        self,
        db_session: AsyncSession,
        session_id: str,
        user_message: str,
        assistant_message: str,
        response_time_ms: int,
        model_used: Optional[str] = None,
        tokens_used: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        try:
            db_session.add(
                ChatHistory(
                    session_id=session_id,
                    message_type=MessageType.USER,
                    content=user_message,
                    msg_metadata=metadata or {},
                )
            )
            db_session.add(
                ChatHistory(
                    session_id=session_id,
                    message_type=MessageType.ASSISTANT,
                    content=assistant_message,
                    response_time_ms=response_time_ms,
                    tokens_used=tokens_used,
                    model_used=model_used,
                    msg_metadata=metadata or {},
                )
            )
            await db_session.commit()
        except Exception as error:
            await db_session.rollback()
            logger.error("Failed to save chat messages: %s", error)

    async def _log_api_usage(
        self,
        db_session: AsyncSession,
        model: Optional[str] = None,
        tokens_used: Optional[int] = None,
        response_time_ms: int = 0,
        error_message: Optional[str] = None,
        success: bool = True,
    ) -> None:
        try:
            db_session.add(
                APIUsageLog(
                    api_provider="openai",
                    endpoint=model,
                    method="POST",
                    status_code=200 if success else 500,
                    response_time_ms=response_time_ms,
                    tokens_used=tokens_used,
                    error_message=error_message,
                    request_metadata={"model": model, "provider": "openai"},
                )
            )
            await db_session.commit()
        except Exception as error:
            logger.warning("Failed to log API usage: %s", error)


_llm_client_instance: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    global _llm_client_instance
    if _llm_client_instance is None:
        _llm_client_instance = LLMClient()
    return _llm_client_instance
