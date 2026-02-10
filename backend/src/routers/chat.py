import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, Body
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, func, text
from db.database import get_async_db, get_db
from db.models import ChatHistory
from schemas import (
    ChatRequest,
    ChatMessageResponse,
    ChatSessionResponse,
    ErrorResponse,
    PaginatedResponse,
    HealthCheckResponse
)
from services.llama_client import get_llm_client, LLMClientError, ModelProvider

# Configure logging
logger = logging.getLogger(__name__)

# Router configuration
router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    }
)


@router.post(
    "/message",
    response_model=ChatMessageResponse,
    summary="Send a chat message",
    description="Send a message to the AI assistant and get a response",
    responses={
        200: {"description": "Successful response from AI"},
        422: {"description": "Validation Error"},
        500: {"description": "AI service error"}
    }
)
async def send_message(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_db)
) -> ChatMessageResponse:
    """Send a message to the AI assistant."""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        logger.info(f"Processing chat message for session: {session_id[:8]}...")
        
        # Determine provider and model
        provider = ModelProvider.LLAMA  # Default provider
        if request.model:
            if "gpt" in request.model.lower():
                provider = ModelProvider.OPENAI
            elif "claude" in request.model.lower():
                provider = ModelProvider.ANTHROPIC
            elif "ollama" in request.model.lower() or "llama" in request.model.lower():
                provider = ModelProvider.OLLAMA
        
        # Send message to LLM
        llm_client = get_llm_client()
        response_data = await llm_client.chat(
            message=request.message,
            session_id=session_id,
            model=request.model,
            provider=provider,
            db_session=session,
            **request.metadata or {}
        )
        
        # Return response
        return ChatMessageResponse(
            id=0,  # This will be set by the database
            session_id=session_id,
            message_type="assistant",
            content=response_data["response"],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            response_time_ms=response_data.get("response_time_ms"),
            tokens_used=response_data.get("tokens_used"),
            model_used=response_data.get("model"),
            metadata=response_data.get("metadata", {})
        )
        
    except LLMClientError as e:
        logger.error(f"LLM client error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/stream",
    summary="Stream chat response",
    description="Send a message and receive a streaming response",
    responses={
        200: {"description": "Streaming response from AI"},
        422: {"description": "Validation Error"}
    }
)
async def stream_message(
    request: ChatRequest,
    session: AsyncSession = Depends(get_async_db)
):
    """Send a message and receive a streaming response."""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        logger.info(f"Starting streaming chat for session: {session_id[:8]}...")
        
        # Determine provider
        provider = ModelProvider.LLAMA
        if request.model:
            if "gpt" in request.model.lower():
                provider = ModelProvider.OPENAI
            elif "ollama" in request.model.lower():
                provider = ModelProvider.OLLAMA
        
        async def generate_stream():
            """Generate streaming response."""
            try:
                llm_client = get_llm_client()
                full_response = ""
                async for chunk in llm_client.stream_chat(
                    message=request.message,
                    session_id=session_id,
                    model=request.model,
                    provider=provider,
                    **request.metadata or {}
                ):
                    full_response += chunk
                    yield f"data: {chunk}\n\n"
                
                # Send completion signal
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                logger.error(f"Streaming error: {str(e)}")
                yield f"data: ERROR: {str(e)}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no" 
            }
        )
        
    except Exception as e:
        logger.error(f"Stream setup error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/sessions/{session_id}",
    response_model=ChatSessionResponse,
    summary="Get chat session",
    description="Retrieve a complete chat session with all messages"
)
async def get_chat_session(
    session_id: str,
    limit: int = Query(50, ge=1, le=100, description="Maximum number of messages"),
    session: AsyncSession = Depends(get_async_db)
) -> ChatSessionResponse:
    """Get a chat session with all its messages."""
    try:
        # Get messages for the session
        stmt = select(ChatHistory).where(
            ChatHistory.session_id == session_id
        ).order_by(desc(ChatHistory.created_at)).limit(limit)
        
        result = await session.execute(stmt)
        messages = result.scalars().all()
        
        if not messages:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Convert to response format
        message_responses = [
            ChatMessageResponse(
                id=msg.id,
                session_id=msg.session_id,
                message_type=msg.message_type,
                content=msg.content,
                created_at=msg.created_at,
                updated_at=msg.updated_at,
                response_time_ms=msg.response_time_ms,
                tokens_used=msg.tokens_used,
                model_used=msg.model_used,
                rating=msg.rating,
                metadata=msg.msg_metadata or {}
            )
            for msg in reversed(messages) 
        ]
        
        return ChatSessionResponse(
            session_id=session_id,
            messages=message_responses,
            message_count=len(message_responses),
            created_at=messages[-1].created_at,  
            last_activity=messages[0].created_at   
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve session")


@router.get(
    "/sessions",
    response_model=PaginatedResponse,
    summary="List chat sessions",
    description="Get a paginated list of chat sessions"
)
async def list_chat_sessions(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    session: AsyncSession = Depends(get_async_db)
) -> PaginatedResponse:
    """Get a paginated list of chat sessions."""
    try:
        offset = (page - 1) * size
        # Get unique sessions with their latest activity
        stmt = select(
            ChatHistory.session_id,
            func.max(ChatHistory.created_at).label('last_activity'),
            func.count(ChatHistory.id).label('message_count')
        ).group_by(ChatHistory.session_id).order_by(
            desc('last_activity')
        ).offset(offset).limit(size)
        
        result = await session.execute(stmt)
        sessions = result.all()
        
        # Get total count
        count_stmt = select(func.count(func.distinct(ChatHistory.session_id)))
        count_result = await session.execute(count_stmt)
        total = count_result.scalar() or 0
        
        # Format response
        session_items = [
            {
                "session_id": s.session_id,
                "last_activity": s.last_activity,
                "message_count": s.message_count
            }
            for s in sessions
        ]
        
        return PaginatedResponse(
            items=session_items,
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size,
            has_next=page * size < total,
            has_prev=page > 1
        )
        
    except Exception as e:
        logger.error(f"Error listing chat sessions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list sessions")


@router.post(
    "/sessions/{session_id}/rate",
    summary="Rate a message",
    description="Rate an assistant message in a conversation"
)
async def rate_message(
    session_id: str,
    message_id: int,
    rating: int = Body(..., ge=1, le=5, description="Rating from 1 to 5"),
    session: AsyncSession = Depends(get_async_db)
):
    """Rate an assistant message."""
    try:
        # Find the message
        stmt = select(ChatHistory).where(
            ChatHistory.session_id == session_id,
            ChatHistory.id == message_id,
            ChatHistory.message_type == "assistant"
        )
        
        result = await session.execute(stmt)
        message = result.scalar_one_or_none()
        
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        # Update rating
        message.rating = rating
        await session.commit()
        
        logger.info(f"Message {message_id} rated {rating} stars")
        
        return {"message": "Rating saved successfully", "rating": rating}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rating message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save rating")


@router.delete(
    "/sessions/{session_id}",
    summary="Delete chat session",
    description="Delete a chat session and all its messages"
)
async def delete_chat_session(
    session_id: str,
    session: AsyncSession = Depends(get_async_db)
):
    """Delete a chat session and all its messages."""
    try:
        # Delete all messages in the session
        from sqlalchemy import delete
        
        stmt = delete(ChatHistory).where(ChatHistory.session_id == session_id)
        result = await session.execute(stmt)
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Session not found")
        
        await session.commit()
        
        logger.info(f"Deleted chat session: {session_id}")
        
        return {"message": f"Session {session_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {str(e)}")
        await session.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete session")


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Chat service health check",
    description="Check the health of the chat service and LLM providers"
)
async def health_check(
    session: AsyncSession = Depends(get_async_db)
) -> HealthCheckResponse:
    """Check the health of the chat service."""
    try:
        # Check database connectivity
        await session.execute(text("SELECT 1"))
        db_healthy = True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_healthy = False
    
    # Check LLM providers (simplified)
    llm_client = get_llm_client()
    external_apis = {
        "llama": bool(llm_client.llama_endpoint),
        "openai": bool(llm_client.openai_api_key),
        "anthropic": bool(llm_client.anthropic_api_key),
        "ollama": True  # Assume local Ollama is available
    }
    
    return HealthCheckResponse(
        status="healthy" if db_healthy else "unhealthy",
        timestamp=datetime.now(timezone.utc),
        database=db_healthy,
        external_apis=external_apis
    )


# Backward compatibility endpoint
@router.get(
    "",
    summary="Simple chat (deprecated)",
    description="Simple chat endpoint for backward compatibility",
    deprecated=True
)
async def simple_chat(
    question: str = Query(..., description="Ask me anything"),
    session: AsyncSession = Depends(get_async_db)
):
    """Simple chat endpoint for backward compatibility."""
    try:
        logger.warning("Using deprecated chat endpoint")
        
        llm_client = get_llm_client()
        response_data = await llm_client.chat(
            message=question,
            provider=ModelProvider.LLAMA,
            db_session=session
        )
        
        return {
            "question": question,
            "answer": response_data["response"],
            "session_id": response_data.get("session_id"),
            "tokens_used": response_data.get("tokens_used")
        }
        
    except LLMClientError as e:
        logger.error(f"LLM error in simple chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error in simple chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Chat service error")