# Task 11: Chat router — conversational AI endpoints
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

from models.database import get_db
from models.schemas import ChatRequest, ChatMessageOut

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatMessageOut)
def send_message(payload: ChatRequest, db: Session = Depends(get_db)):
    """Send a message and receive an AI response grounded in the user's profile."""
    return {}


@router.get("", response_model=List[ChatMessageOut])
def get_history(target_role_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Return chat message history, optionally filtered by target role."""
    return []


@router.delete("")
def clear_history(target_role_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Clear chat history for the authenticated user."""
    return {"cleared": True}
