import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_async_db
from schemas import ChatMessageResponse, ChatRequest
from services.llm_client import LLMClientError, ModelProvider, get_llm_client
from services.portfolio_context import build_system_prompt

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat"])


def _normalize_requested_model(model: Optional[str]) -> Optional[str]:
    if model is None:
        return None
    normalized = model.strip()
    return (
        None
        if not normalized or normalized.lower() in {"string", "default", "auto"}
        else normalized
    )


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_db),
) -> ChatMessageResponse:
    """Send one message to the portfolio assistant."""
    del background_tasks
    session_id = request.session_id or str(uuid.uuid4())
    try:
        response_data = await get_llm_client().chat(
            message=request.message,
            session_id=session_id,
            model=_normalize_requested_model(request.model),
            provider=ModelProvider.OPENAI,
            system_instruction=await build_system_prompt(db_session=session),
            db_session=session,
            **request.metadata or {},
        )
        now = datetime.now(timezone.utc)
        return ChatMessageResponse(
            id=0,
            session_id=session_id,
            message_type="assistant",
            content=response_data["response"],
            created_at=now,
            updated_at=now,
            response_time_ms=response_data.get("response_time_ms"),
            tokens_used=response_data.get("tokens_used"),
            model_used=response_data.get("model"),
            metadata=response_data.get("metadata", {}),
        )
    except LLMClientError as exc:
        logger.error("LLM client error: %s", exc)
        raise HTTPException(500, f"AI service error: {exc}") from None
    except Exception:
        logger.exception("Unexpected error in chat")
        raise HTTPException(500, "Internal server error") from None
