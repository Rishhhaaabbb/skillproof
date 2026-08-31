# Task 11: Chat router — complete implementation
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user, get_db
from models.database import ChatMessage, User
from models.schemas import ChatMessageOut, ChatRequest
from services.chat_service import ChatService

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatMessageOut)
def send_message(
    payload: ChatRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Send a message and receive an AI response grounded in the user's profile."""
    svc = ChatService()
    svc.send_message(
        db=db,
        user_id=user.id,
        message=payload.message,
        target_role_id=payload.target_role_id,
    )
    last_msg = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user.id, ChatMessage.role == "assistant")
        .order_by(ChatMessage.created_at.desc())
        .first()
    )
    if last_msg is None:
        raise HTTPException(status_code=500, detail="Chat response not saved correctly.")
    return last_msg


@router.get("", response_model=List[ChatMessageOut])
def get_history(
    target_role_id: Optional[int] = Query(default=None),
    limit: int = Query(default=50, le=200),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return chat message history, optionally filtered by target role."""
    return ChatService().get_history(db, user.id, target_role_id, limit=limit)


@router.delete("")
def clear_history(
    target_role_id: Optional[int] = Query(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Clear chat history for the authenticated user."""
    ChatService().clear_history(db, user.id, target_role_id)
    return {"cleared": True}
