"""Announcement endpoints for public display and authenticated management."""

from datetime import date
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..database import announcements_collection
from .auth import require_signed_in_user

router = APIRouter(prefix="/announcements", tags=["announcements"])


class AnnouncementInput(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    start_date: Optional[date] = None
    expires_at: date


def serialize_announcement(announcement: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": announcement["_id"],
        "message": announcement["message"],
        "start_date": announcement.get("start_date"),
        "expires_at": announcement["expires_at"]
    }


def validate_announcement(data: AnnouncementInput) -> Dict[str, Any]:
    message = data.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="Message cannot be empty")
    if data.start_date and data.start_date > data.expires_at:
        raise HTTPException(
            status_code=422,
            detail="Start date must be on or before the expiration date"
        )
    return {
        "message": message,
        "start_date": data.start_date.isoformat() if data.start_date else None,
        "expires_at": data.expires_at.isoformat()
    }


@router.get("")
def get_active_announcements() -> List[Dict[str, Any]]:
    """Return announcements currently within their display dates."""
    today = date.today().isoformat()
    query = {
        "expires_at": {"$gte": today},
        "$or": [{"start_date": None}, {"start_date": {"$lte": today}}]
    }
    return [serialize_announcement(item) for item in announcements_collection.find(query)]


@router.get("/manage")
def list_announcements(
    _teacher: Dict[str, Any] = Depends(require_signed_in_user)
) -> List[Dict[str, Any]]:
    """List all announcements for signed-in users."""
    return [
        serialize_announcement(item)
        for item in announcements_collection.find().sort("expires_at", 1)
    ]


@router.post("", status_code=201)
def create_announcement(
    data: AnnouncementInput,
    _teacher: Dict[str, Any] = Depends(require_signed_in_user)
) -> Dict[str, Any]:
    announcement = {"_id": str(uuid4()), **validate_announcement(data)}
    announcements_collection.insert_one(announcement)
    return serialize_announcement(announcement)


@router.put("/{announcement_id}")
def update_announcement(
    announcement_id: str,
    data: AnnouncementInput,
    _teacher: Dict[str, Any] = Depends(require_signed_in_user)
) -> Dict[str, Any]:
    announcement = validate_announcement(data)
    result = announcements_collection.update_one(
        {"_id": announcement_id}, {"$set": announcement}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return {"id": announcement_id, **announcement}


@router.delete("/{announcement_id}")
def delete_announcement(
    announcement_id: str,
    _teacher: Dict[str, Any] = Depends(require_signed_in_user)
) -> Dict[str, str]:
    result = announcements_collection.delete_one({"_id": announcement_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return {"message": "Announcement deleted"}