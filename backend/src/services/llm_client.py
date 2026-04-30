import json
import logging
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, AsyncGenerator
from enum import Enum

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import ChatHistory, APIUsageLog
from schemas import MessageType

# Configure logging
logger = logging.getLogger(__name__)

class ModelProvider(str, Enum):
    """Supported model providers."""
    GEMINI = "gemini"
    OPENAI = "openai"


class LLMClientError(Exception):
    """Custom exception for LLM client errors."""
    pass


class GeminiProvider:
    """Provider for Google Gemini models."""

    CONTEXT_WINDOW_SIZE = 10
    
    def __init__(self):
        """Initialize the Gemini provider."""
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not configured at startup")
            
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = "gemini-2.5-pro"
        self.backup_model = "gemini-2.5-flash"
    
    async def generate_response(
        self,
        message: str,
        model: Optional[str] = None,
        context: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response from Gemini model."""
        if not self.api_key:
            raise LLMClientError("GEMINI_API_KEY not configured")
        
        model_name = model or self.model
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens', 2048)
        
        contents = []
        if context:
            for msg in context[-self.CONTEXT_WINDOW_SIZE:]:
                role = "user" if msg.get("role") in ["user", "human"] else "model"
                contents.append({"role": role, "parts": [{"text": msg.get("content", "")}]})
        
        contents.append({"role": "user", "parts": [{"text": message}]})
        
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }
        
        models_to_try = [model_name]
        if model_name == self.model: # If default is used, add backup
            models_to_try.append(self.backup_model)
            
        last_error = None
        for current_model in models_to_try:
            url = f"{self.base_url}/models/{current_model}:generateContent"
            try:
                async with httpx.AsyncClient(timeout=60) as client:
                    response = await client.post(url, json=payload, headers=headers)
                    response.raise_for_status()
                    
                    result = response.json()
                    
                    generated_text = ""
                    if "candidates" in result and len(result["candidates"]) > 0:
                        candidate = result["candidates"][0]
                        parts = candidate.get("content", {}).get("parts", [])
                        generated_text = parts[0].get("text", "") if parts else ""
                    
                    usage_metadata = result.get("usageMetadata", {})
                    tokens_used = usage_metadata.get("totalTokenCount", 0)
                    
                    return {
                        "content": generated_text.strip(),
                        "model": current_model,
                        "tokens_used": tokens_used,
                        "metadata": {
                            "provider": "gemini",
                            "prompt_tokens": usage_metadata.get("promptTokenCount", 0),
                            "candidates_count": len(result.get("candidates", [])),
                        }
                    }
            except httpx.HTTPStatusError as e:
                try:
                    error_data = e.response.json()
                    error_details = error_data.get("error", {}).get("message", str(error_data.get("error")))
                except Exception:
                    error_details = e.response.text
                
                last_error = f"API error ({e.response.status_code}): {error_details}"
                logger.warning(f"Request failed with model {current_model}: {last_error}")
                
                # Only use backup model if we get a 503 (Service Unavailable) 
                if e.response.status_code == 503:
                    continue 
                else:
                    # Break out and fail immediately for issues like 429 (out of credits) / 401 (auth)
                    raise LLMClientError(f"Gemini API request failed. Last error: {last_error}")
                    
            except httpx.RequestError as e:
                last_error = f"Request failed: {str(e)}"
                logger.warning(f"Request failed with model {current_model}: {last_error}")
                continue 
                
        raise LLMClientError(f"Gemini API request failed. Last error: {last_error}")

    async def stream_response(
        self,
        message: str,
        model: Optional[str] = None,
        context: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream response from Gemini model."""
        if not self.api_key:
            raise LLMClientError("GEMINI_API_KEY not configured")
            
        model_name = model or self.model
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens', 2048)
        
        contents = []
        if context:
            for msg in context[-self.CONTEXT_WINDOW_SIZE:]:
                role = "user" if msg.get("role") in ["user", "human"] else "model"
                contents.append({"role": role, "parts": [{"text": msg.get("content", "")}]})
                
        contents.append({"role": "user", "parts": [{"text": message}]})
        
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }
        
        models_to_try = [model_name]
        if model_name == self.model:
            models_to_try.append(self.backup_model)
            
        last_error = None
        for current_model in models_to_try:
            url = f"{self.base_url}/models/{current_model}:streamGenerateContent?alt=sse"
            try:
                import json
                async with httpx.AsyncClient(timeout=120) as client:
                    async with client.stream("POST", url, json=payload, headers=headers) as response:
                        response.raise_for_status()
                        async for line in response.aiter_lines():
                            if line.startswith("data: "):
                                data_str = line[6:].strip()
                                if data_str and data_str != "[DONE]":
                                    try:
                                        data = json.loads(data_str)
                                        if "candidates" in data and len(data["candidates"]) > 0:
                                            parts = data["candidates"][0].get("content", {}).get("parts", [])
                                            if parts and parts[0].get("text"):
                                                yield parts[0].get("text")
                                    except json.JSONDecodeError:
                                        pass
                return 
            except httpx.HTTPStatusError as e:
                try:
                    error_data = e.response.json()
                    error_details = error_data.get("error", {}).get("message", str(error_data.get("error")))
                except Exception:
                    error_details = e.response.text
                last_error = f"API error ({e.response.status_code}): {error_details}"
                logger.warning(f"Streaming failed with model {current_model}: {last_error}")
                
                # Only use backup model if we get a 503 (Service Unavailable)
                if e.response.status_code == 503:
                    continue
                else:
                    # Break out and fail immediately for issues like 429 
                    raise LLMClientError(f"Gemini streaming failed. Last error: {last_error}")
                    
            except Exception as e:
                last_error = f"Streaming failed: {str(e)}"
                logger.warning(f"Streaming failed with model {current_model}: {last_error}")
                continue 
                
        raise LLMClientError(f"Gemini streaming failed. Last error: {last_error}")


class OpenAIProvider:
    """Provider for OpenAI models."""

    CONTEXT_WINDOW_SIZE = 10

    def __init__(self):
        """Initialize the OpenAI provider."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not configured at startup")

        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = "gpt-4o"
        self.backup_model = "gpt-4o-mini"

    async def generate_response(
        self,
        message: str,
        model: Optional[str] = None,
        context: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response from OpenAI model."""
        if not self.api_key:
            raise LLMClientError("OPENAI_API_KEY not configured")

        from openai import AsyncOpenAI, APIStatusError, APIConnectionError

        model_name = model or self.model
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens', 2048)

        messages = []
        if context:
            for msg in context[-self.CONTEXT_WINDOW_SIZE:]:
                role = "user" if msg.get("role") in ["user", "human"] else "assistant"
                messages.append({"role": role, "content": msg.get("content", "")})
        messages.append({"role": "user", "content": message})

        client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)

        models_to_try = [model_name]
        if model_name == self.model:
            models_to_try.append(self.backup_model)

        last_error = None
        for current_model in models_to_try:
            try:
                response = await client.chat.completions.create(
                    model=current_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

                generated_text = response.choices[0].message.content or ""
                usage = response.usage
                tokens_used = usage.total_tokens if usage else 0

                return {
                    "content": generated_text.strip(),
                    "model": current_model,
                    "tokens_used": tokens_used,
                    "metadata": {
                        "provider": "openai",
                        "prompt_tokens": usage.prompt_tokens if usage else 0,
                        "completion_tokens": usage.completion_tokens if usage else 0,
                    }
                }
            except APIStatusError as e:
                last_error = f"API error ({e.status_code}): {e.message}"
                logger.warning(f"OpenAI request failed with model {current_model}: {last_error}")
                if e.status_code >= 500:
                    continue
                else:
                    raise LLMClientError(f"OpenAI API request failed: {last_error}")
            except APIConnectionError as e:
                last_error = f"Connection failed: {str(e)}"
                logger.warning(f"OpenAI connection failed with model {current_model}: {last_error}")
                continue

        raise LLMClientError(f"OpenAI API request failed. Last error: {last_error}")

    async def stream_response(
        self,
        message: str,
        model: Optional[str] = None,
        context: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream response from OpenAI model."""
        if not self.api_key:
            raise LLMClientError("OPENAI_API_KEY not configured")

        from openai import AsyncOpenAI, APIStatusError, APIConnectionError

        model_name = model or self.model
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens', 2048)

        messages = []
        if context:
            for msg in context[-self.CONTEXT_WINDOW_SIZE:]:
                role = "user" if msg.get("role") in ["user", "human"] else "assistant"
                messages.append({"role": role, "content": msg.get("content", "")})
        messages.append({"role": "user", "content": message})

        client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)

        try:
            stream = await client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except APIStatusError as e:
            last_error = f"API error ({e.status_code}): {e.message}"
            logger.warning(f"OpenAI streaming failed: {last_error}")
            raise LLMClientError(f"OpenAI streaming failed: {last_error}")
        except APIConnectionError as e:
            last_error = f"Connection failed: {str(e)}"
            logger.warning(f"OpenAI streaming connection failed: {last_error}")
            raise LLMClientError(f"OpenAI streaming failed: {last_error}")
        except Exception as e:
            logger.warning(f"OpenAI streaming failed: {str(e)}")
            raise LLMClientError(f"OpenAI streaming failed: {str(e)}")


class LLMClient:
    """Unified client for LLM interaction supporting Gemini and OpenAI."""

    def __init__(self):
        self.gemini_provider = GeminiProvider()
        self.openai_provider = OpenAIProvider()
        self.max_tokens = int(os.getenv("MAX_TOKENS", "2048"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))

        # Determine default provider from environment
        default_provider_env = os.getenv("DEFAULT_LLM_PROVIDER", "gemini").lower()
        try:
            self.default_provider = ModelProvider(default_provider_env)
        except ValueError:
            logger.warning(f"Unknown DEFAULT_LLM_PROVIDER '{default_provider_env}', falling back to gemini")
            self.default_provider = ModelProvider.GEMINI

        logger.info(f"LLM Client initialized. Default provider: {self.default_provider}")

    def _get_provider_client(self, provider: Optional[ModelProvider] = None):
        """Return (provider_client, provider_name) for the requested or default provider."""
        resolved = provider or self.default_provider
        if resolved == ModelProvider.OPENAI:
            return self.openai_provider, "openai"
        return self.gemini_provider, "gemini"

    async def chat(
        self,
        message: str,
        session_id: Optional[str] = None,
        model: Optional[str] = None,
        provider: Optional[ModelProvider] = None,
        context: Optional[List[Dict[str, str]]] = None,
        db_session: Optional[AsyncSession] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Send a chat message and get a response."""
        start_time = datetime.now(timezone.utc)
        provider_client, provider_name = self._get_provider_client(provider)

        try:
            conversation_history = []
            if session_id and db_session:
                conversation_history = await self._get_conversation_history(db_session, session_id)

            response_data = await provider_client.generate_response(
                message=message,
                model=model,
                context=context or conversation_history,
                max_tokens=kwargs.get('max_tokens', self.max_tokens),
                temperature=kwargs.get('temperature', self.temperature)
            )

            response_time_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
            response_content = (response_data.get("content") or "").strip()

            if not response_content:
                raise LLMClientError(f"{provider_name.capitalize()} returned an empty response. Please verify your API key and settings.")

            if session_id and db_session:
                await self._save_chat_messages(
                    db_session=db_session,
                    session_id=session_id,
                    user_message=message,
                    assistant_message=response_content,
                    response_time_ms=response_time_ms,
                    model_used=response_data.get("model"),
                    tokens_used=response_data.get("tokens_used"),
                    metadata=response_data.get("metadata", {})
                )

            if db_session:
                await self._log_api_usage(
                    db_session=db_session,
                    provider=provider_name,
                    model=response_data.get("model"),
                    tokens_used=response_data.get("tokens_used"),
                    response_time_ms=response_time_ms,
                    success=True
                )

            return {
                "response": response_content,
                "session_id": session_id,
                "model": response_data.get("model"),
                "provider": provider_name,
                "tokens_used": response_data.get("tokens_used"),
                "response_time_ms": response_time_ms,
                "metadata": response_data.get("metadata", {})
            }

        except Exception as e:
            if db_session:
                await self._log_api_usage(
                    db_session=db_session,
                    provider=provider_name,
                    error_message=str(e),
                    response_time_ms=int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000),
                    success=False
                )
            logger.error(f"LLM chat failed: {str(e)}")
            raise LLMClientError(f"Failed to get LLM response: {str(e)}")

    async def stream_chat(
        self,
        message: str,
        session_id: Optional[str] = None,
        model: Optional[str] = None,
        provider: Optional[ModelProvider] = None,
        context: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream chat response from the selected provider."""
        provider_client, _ = self._get_provider_client(provider)
        async for chunk in provider_client.stream_response(
            message=message,
            model=model,
            context=context,
            **kwargs
        ):
            yield chunk

    async def _get_conversation_history(self, session: AsyncSession, session_id: str, limit: int = 10) -> List[Dict[str, str]]:
        try:
            from sqlalchemy import select, desc
            stmt = select(ChatHistory).where(ChatHistory.session_id == session_id).order_by(desc(ChatHistory.created_at)).limit(limit * 2)
            result = await session.execute(stmt)
            messages = result.scalars().all()

            conversation = []
            for msg in reversed(messages):
                conversation.append({"role": "user" if msg.message_type == MessageType.USER else "model", "content": msg.content})
            return conversation[-limit:]
        except Exception as e:
            logger.warning(f"Failed to get conversation history: {str(e)}")
            return []

    async def _save_chat_messages(self, db_session: AsyncSession, session_id: str, user_message: str, assistant_message: str, response_time_ms: int, model_used: Optional[str] = None, tokens_used: Optional[int] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        try:
            user_msg = ChatHistory(session_id=session_id, message_type=MessageType.USER, content=user_message, msg_metadata=metadata or {})
            assistant_msg = ChatHistory(session_id=session_id, message_type=MessageType.ASSISTANT, content=assistant_message, response_time_ms=response_time_ms, tokens_used=tokens_used, model_used=model_used, msg_metadata=metadata or {})
            db_session.add(user_msg)
            db_session.add(assistant_msg)
            await db_session.commit()
        except Exception as e:
            await db_session.rollback()
            logger.error(f"Failed to save chat messages: {str(e)}")

    async def _log_api_usage(self, db_session: AsyncSession, provider: str = "gemini", model: Optional[str] = None, tokens_used: Optional[int] = None, response_time_ms: int = 0, error_message: Optional[str] = None, success: bool = True) -> None:
        try:
            log_entry = APIUsageLog(
                api_provider=provider,
                endpoint=model,
                method="POST",
                status_code=200 if success else 500,
                response_time_ms=response_time_ms,
                tokens_used=tokens_used,
                error_message=error_message,
                request_metadata={"model": model, "provider": provider}
            )
            db_session.add(log_entry)
            await db_session.commit()
        except Exception as e:
            logger.warning(f"Failed to log API usage: {str(e)}")

# Global lazy instance
_llm_client_instance: Optional[LLMClient] = None

def get_llm_client() -> LLMClient:
    global _llm_client_instance
    if _llm_client_instance is None:
        _llm_client_instance = LLMClient()
    return _llm_client_instance

