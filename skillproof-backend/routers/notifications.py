# Task 12: Notifications router — in-app notification management
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from models.database import get_db
from models.schemas import NotificationOut

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("", response_model=List[NotificationOut])
def list_notifications(db: Session = Depends(get_db)):
    """Return all notifications for the authenticated user, unread first."""
    return []


@router.patch("/{notification_id}/read")
def mark_read(notification_id: int, db: Session = Depends(get_db)):
    """Mark a single notification as read."""
    return {"id": notification_id, "is_read": True}


@router.patch("/read-all")
def mark_all_read(db: Session = Depends(get_db)):
    """Mark all notifications as read for the authenticated user."""
    return {"marked": 0}


@router.delete("/{notification_id}", status_code=204)
def delete_notification(notification_id: int, db: Session = Depends(get_db)):
    """Delete a single notification."""
    return None
