import json
import logging
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union, AsyncGenerator
from enum import Enum

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import ChatHistory, APIUsageLog
from schemas import ChatMessageCreate, ChatMessageResponse, MessageType

# Configure logging
logger = logging.getLogger(__name__)


class ModelProvider(str, Enum):
    """Supported model providers."""
    LLAMA = "llama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    GEMINI = "gemini"
    LOCAL = "local"


class LLMClientError(Exception):
    """Custom exception for LLM client errors."""
    pass


class LLMClient:
    """Unified client for various LLM providers."""
    
    def __init__(self):
        self.providers = {
            ModelProvider.LLAMA: LlamaProvider(),
            ModelProvider.OPENAI: OpenAIProvider(),
            ModelProvider.ANTHROPIC: AnthropicProvider(),
            ModelProvider.OLLAMA: OllamaProvider(),
            ModelProvider.GEMINI: GeminiProvider(),
        }
        self.default_provider = ModelProvider.LLAMA
        
        # Load configuration
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from environment variables."""
        # LLaMA/Hugging Face
        self.llama_endpoint = os.getenv("LLAMA_API_URL")
        self.llama_token = os.getenv("HUGGINGFACE_TOKEN")
        
        # OpenAI
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        
        # Anthropic
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        
        # Gemini
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        # Ollama
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        # General settings
        self.default_model = os.getenv("DEFAULT_LLM_MODEL", "llama")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "2048"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        self.timeout = int(os.getenv("LLM_TIMEOUT", "60"))
    
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
        """
        Send a chat message to the LLM and get a response.
        
        Args:
            message: User message
            session_id: Optional session ID for conversation continuity
            model: Specific model to use
            provider: LLM provider to use
            context: Additional context messages
            db_session: Database session for logging
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Dictionary containing response and metadata
            
        Raises:
            LLMClientError: If the request fails
        """
        start_time = datetime.now(timezone.utc)
        provider = provider or self.default_provider
        
        try:
            # Get conversation history if session_id provided
            conversation_history = []
            if session_id and db_session:
                conversation_history = await self._get_conversation_history(db_session, session_id)
            
            # Prepare the provider
            llm_provider = self.providers.get(provider)
            if not llm_provider:
                raise LLMClientError(f"Unsupported provider: {provider}")
            
            # Make the request
            response_data = await llm_provider.generate_response(
                message=message,
                model=model,
                context=context or conversation_history,
                max_tokens=kwargs.get('max_tokens', self.max_tokens),
                temperature=kwargs.get('temperature', self.temperature),
                **kwargs
            )
            
            # Calculate metrics
            response_time_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
            
            # Save to database if session provided
            if session_id and db_session:
                await self._save_chat_messages(
                    db_session=db_session,
                    session_id=session_id,
                    user_message=message,
                    assistant_message=response_data["content"],
                    response_time_ms=response_time_ms,
                    model_used=response_data.get("model"),
                    tokens_used=response_data.get("tokens_used"),
                    metadata=response_data.get("metadata", {})
                )
            
            # Log API usage
            if db_session:
                await self._log_api_usage(
                    db_session=db_session,
                    provider=provider,
                    model=response_data.get("model"),
                    tokens_used=response_data.get("tokens_used"),
                    response_time_ms=response_time_ms,
                    cost_usd=response_data.get("cost_usd"),
                    success=True
                )
            
            logger.info(f"LLM chat completed successfully using {provider}")
            
            return {
                "response": response_data["content"],
                "session_id": session_id,
                "model": response_data.get("model"),
                "tokens_used": response_data.get("tokens_used"),
                "response_time_ms": response_time_ms,
                "metadata": response_data.get("metadata", {})
            }
            
        except Exception as e:
            # Log failed API usage
            if db_session:
                await self._log_api_usage(
                    db_session=db_session,
                    provider=provider,
                    error_message=str(e),
                    response_time_ms=int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000),
                    success=False
                )
            
            logger.error(f"LLM chat failed with {provider}: {str(e)}")
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
        """
        Stream chat response from LLM.
        
        Args:
            message: User message
            session_id: Optional session ID
            model: Specific model to use
            provider: LLM provider to use
            context: Additional context messages
            **kwargs: Additional parameters
            
        Yields:
            Chunks of the response as they arrive
        """
        provider = provider or self.default_provider
        llm_provider = self.providers.get(provider)
        
        if not llm_provider:
            raise LLMClientError(f"Unsupported provider: {provider}")
        
        if not hasattr(llm_provider, 'stream_response'):
            raise LLMClientError(f"Provider {provider} does not support streaming")
        
        async for chunk in llm_provider.stream_response(
            message=message,
            model=model,
            context=context,
            **kwargs
        ):
            yield chunk
    
    async def _get_conversation_history(
        self, 
        session: AsyncSession, 
        session_id: str,
        limit: int = 10
    ) -> List[Dict[str, str]]:
        """Get recent conversation history for context."""
        try:
            from sqlalchemy import select, desc
            
            stmt = select(ChatHistory).where(
                ChatHistory.session_id == session_id
            ).order_by(desc(ChatHistory.created_at)).limit(limit * 2)  # Get more to filter pairs
            
            result = await session.execute(stmt)
            messages = result.scalars().all()
            
            # Convert to conversation format
            conversation = []
            for msg in reversed(messages):  # Reverse to chronological order
                conversation.append({
                    "role": msg.message_type,
                    "content": msg.content
                })
            
            return conversation[-limit:]  # Keep only the most recent
            
        except Exception as e:
            logger.warning(f"Failed to get conversation history: {str(e)}")
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
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Save chat messages to database."""
        try:
            # Save user message
            user_msg = ChatHistory(
                session_id=session_id,
                message_type=MessageType.USER,
                content=user_message,
                metadata=metadata or {}
            )
            db_session.add(user_msg)
            
            # Save assistant message
            assistant_msg = ChatHistory(
                session_id=session_id,
                message_type=MessageType.ASSISTANT,
                content=assistant_message,
                response_time_ms=response_time_ms,
                tokens_used=tokens_used,
                model_used=model_used,
                metadata=metadata or {}
            )
            db_session.add(assistant_msg)
            
            await db_session.commit()
            
        except Exception as e:
            await db_session.rollback()
            logger.error(f"Failed to save chat messages: {str(e)}")
    
    async def _log_api_usage(
        self,
        db_session: AsyncSession,
        provider: ModelProvider,
        model: Optional[str] = None,
        tokens_used: Optional[int] = None,
        response_time_ms: int = 0,
        cost_usd: Optional[float] = None,
        error_message: Optional[str] = None,
        success: bool = True
    ) -> None:
        """Log API usage for monitoring."""
        try:
            log_entry = APIUsageLog(
                api_provider=provider.value,
                endpoint=model,
                method="POST",
                status_code=200 if success else 500,
                response_time_ms=response_time_ms,
                tokens_used=tokens_used,
                cost_usd=cost_usd,
                error_message=error_message,
                request_metadata={"model": model, "provider": provider.value}
            )
            
            db_session.add(log_entry)
            await db_session.commit()
            
        except Exception as e:
            logger.warning(f"Failed to log API usage: {str(e)}")


class BaseLLMProvider:
    """Base class for LLM providers."""
    
    async def generate_response(
        self,
        message: str,
        model: Optional[str] = None,
        context: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response from the LLM."""
        raise NotImplementedError
    
    async def stream_response(
        self,
        message: str,
        model: Optional[str] = None,
        context: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream response from the LLM."""
        raise NotImplementedError


class LlamaProvider(BaseLLMProvider):
    """Provider for LLaMA models via Hugging Face or local deployment."""
    
    async def generate_response(
        self,
        message: str,
        model: Optional[str] = None,
        context: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response from LLaMA model."""
        endpoint = os.getenv("LLAMA_API_URL")
        if not endpoint:
            raise LLMClientError("LLAMA_API_URL not configured")
        
        # Prepare the prompt with context
        full_prompt = self._prepare_prompt(message, context)
        
        payload = {
            "inputs": full_prompt,
            "parameters": {
                "max_new_tokens": kwargs.get("max_tokens", 2048),
                "temperature": kwargs.get("temperature", 0.7),
                "do_sample": True,
                "return_full_text": False
            }
        }
        
        headers = {}
        if token := os.getenv("HUGGINGFACE_TOKEN"):
            headers["Authorization"] = f"Bearer {token}"
        
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(endpoint, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            
            # Handle different response formats
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get("generated_text", "")
            elif isinstance(result, dict):
                generated_text = result.get("generated_text", "")
            else:
                generated_text = str(result)
            
            return {
                "content": generated_text.strip(),
                "model": model or "llama",
                "tokens_used": len(generated_text.split()) * 1.3,  # Rough estimation
                "metadata": {"provider": "llama", "endpoint": endpoint}
            }
    
    def _prepare_prompt(
        self, 
        message: str, 
        context: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Prepare the prompt with conversation context."""
        if not context:
            return message
        
        prompt_parts = []
        for msg in context[-5:]:  # Keep last 5 messages for context
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                prompt_parts.append(f"Human: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        prompt_parts.append(f"Human: {message}")
        prompt_parts.append("Assistant:")
        
        return "\n".join(prompt_parts)


class OpenAIProvider(BaseLLMProvider):
    """Provider for OpenAI models."""
    
    async def generate_response(
        self,
        message: str,
        model: Optional[str] = None,
        context: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response from OpenAI model."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise LLMClientError("OPENAI_API_KEY not configured")
        
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        model = model or "gpt-3.5-turbo"
        
        # Prepare messages
        messages = []
        if context:
            messages.extend([
                {"role": msg["role"], "content": msg["content"]} 
                for msg in context[-10:]  # Keep last 10 for context
            ])
        messages.append({"role": "user", "content": message})
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 2048),
            "temperature": kwargs.get("temperature", 0.7),
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
            result = response.json()
            choice = result["choices"][0]
            usage = result.get("usage", {})
            
            return {
                "content": choice["message"]["content"],
                "model": model,
                "tokens_used": usage.get("total_tokens"),
                "cost_usd": self._calculate_openai_cost(model, usage),
                "metadata": {"provider": "openai", "finish_reason": choice.get("finish_reason")}
            }
    
    def _calculate_openai_cost(self, model: str, usage: Dict[str, int]) -> Optional[float]:
        """Calculate approximate cost for OpenAI API usage."""
        # Simplified cost calculation - update with current pricing
        cost_per_1k = {
            "gpt-4": 0.03,
            "gpt-3.5-turbo": 0.002,
        }
        
        if model in cost_per_1k and "total_tokens" in usage:
            return (usage["total_tokens"] / 1000) * cost_per_1k[model]
        return None


class AnthropicProvider(BaseLLMProvider):
    """Provider for Anthropic Claude models."""
    
    async def generate_response(
        self,
        message: str,
        model: Optional[str] = None,
        context: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response from Anthropic model."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise LLMClientError("ANTHROPIC_API_KEY not configured")
        
        # Implementation would go here
        raise LLMClientError("Anthropic provider not yet implemented")


class OllamaProvider(BaseLLMProvider):
    """Provider for Ollama local models."""
    
    async def generate_response(
        self,
        message: str,
        model: Optional[str] = None,
        context: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response from Ollama model."""
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model = model or "llama2"
        
        # Prepare the prompt
        prompt = self._prepare_prompt(message, context)
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", 0.7),
                "num_predict": kwargs.get("max_tokens", 2048),
            }
        }
        
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(f"{base_url}/api/generate", json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            return {
                "content": result.get("response", ""),
                "model": model,
                "tokens_used": result.get("eval_count"),
                "metadata": {
                    "provider": "ollama",
                    "total_duration": result.get("total_duration"),
                    "load_duration": result.get("load_duration"),
                    "prompt_eval_count": result.get("prompt_eval_count"),
                    "eval_count": result.get("eval_count"),
                }
            }
    
    def _prepare_prompt(
        self, 
        message: str, 
        context: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Prepare prompt for Ollama."""
        if not context:
            return message
        
        prompt_parts = []
        for msg in context[-5:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            prompt_parts.append(f"{role}: {content}")
        
        prompt_parts.append(f"user: {message}")
        return "\n".join(prompt_parts)


class GeminiProvider(BaseLLMProvider):
    """Provider for Google Gemini models."""
    
    def __init__(self):
        """Initialize the Gemini provider."""
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
    
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
        
        model = model or "gemini-pro"
        
        # Prepare messages in Gemini format
        contents = []
        if context:
            for msg in context[-10:]:  # Keep last 10 for context
                role = "user" if msg.get("role") == "user" else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg.get("content", "")}]
                })
        
        contents.append({
            "role": "user",
            "parts": [{"text": message}]
        })
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": kwargs.get("temperature", 0.7),
                "maxOutputTokens": kwargs.get("max_tokens", 2048),
            }
        }
        
        # Use API key in header (more secure than query parameter)
        url = f"{self.base_url}/models/{model}:generateContent"
        headers = {
            "X-Goog-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                result = response.json()
                
                # Extract the generated text
                if "candidates" in result and len(result["candidates"]) > 0:
                    candidate = result["candidates"][0]
                    content = candidate.get("content", {})
                    parts = content.get("parts", [])
                    generated_text = parts[0].get("text", "") if parts else ""
                else:
                    generated_text = ""
                
                # Extract token usage if available
                usage_metadata = result.get("usageMetadata", {})
                tokens_used = usage_metadata.get("totalTokenCount", 0)
                
                return {
                    "content": generated_text.strip(),
                    "model": model,
                    "tokens_used": tokens_used,
                    "metadata": {
                        "provider": "gemini",
                        "prompt_tokens": usage_metadata.get("promptTokenCount", 0),
                        "candidates_count": len(result.get("candidates", [])),
                    }
                }
        except httpx.HTTPStatusError as e:
            # Extract detailed error information from Gemini API
            error_details = "Unknown error"
            try:
                error_data = e.response.json()
                if "error" in error_data:
                    error_details = error_data["error"].get("message", str(error_data["error"]))
            except Exception:
                error_details = e.response.text
            
            raise LLMClientError(
                f"Gemini API error (status {e.response.status_code}): {error_details}"
            )
        except httpx.RequestError as e:
            raise LLMClientError(f"Gemini API request failed: {str(e)}")


# Global service instance
llm_client = LLMClient()

# Backward compatibility function
async def ask_llama(question: str) -> str:
    """
    Backward compatibility function for asking LLaMA.
    
    Args:
        question: Question to ask
        
    Returns:
        LLaMA response
        
    Raises:
        RuntimeError: If the request fails
    """
    try:
        result = await llm_client.chat(message=question, provider=ModelProvider.LLAMA)
        return result["response"]
    except LLMClientError as e:
        raise RuntimeError(str(e))