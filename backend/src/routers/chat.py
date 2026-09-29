import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_async_db
from schemas import ChatMessageResponse, ChatRequest
from services.llm_client import LLMClientError, ModelProvider, get_llm_client
from services.portfolio_context import build_system_prompt
from services.rate_limit import enforce_chat_rate_limit

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat"])

# Shown to visitors instead of provider details (quota, request IDs, model
# names), which are logged server-side.
UNAVAILABLE_MESSAGE = (
    "The assistant is unavailable right now. Please try again in a few minutes."
)


@router.post(
    "/message",
    response_model=ChatMessageResponse,
    dependencies=[Depends(enforce_chat_rate_limit)],
)
async def send_message(
    request: ChatRequest,
    session: AsyncSession = Depends(get_async_db),
) -> ChatMessageResponse:
    """Send one message to the portfolio assistant."""
    session_id = request.session_id or str(uuid.uuid4())
    try:
        response_data = await get_llm_client().chat(
            message=request.message,
            session_id=session_id,
            provider=ModelProvider.OPENAI,
            system_instruction=await build_system_prompt(db_session=session),
            db_session=session,
        )
    except LLMClientError as exc:
        logger.error("LLM client error: %s", exc)
        raise HTTPException(503, UNAVAILABLE_MESSAGE) from None
    except Exception:
        logger.exception("Unexpected error in chat")
        raise HTTPException(500, UNAVAILABLE_MESSAGE) from None

    now = datetime.now(timezone.utc)
    return ChatMessageResponse(
        id=response_data.get("message_id") or 0,
        session_id=session_id,
        message_type="assistant",
        content=response_data["response"],
        created_at=now,
        updated_at=now,
        response_time_ms=response_data.get("response_time_ms"),
        model_used=response_data.get("model"),
    )
