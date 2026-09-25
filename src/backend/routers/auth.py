"""
Authentication endpoints for the High School Management System API
"""

from fastapi import APIRouter, Depends, Header, HTTPException
from typing import Dict, Any, Optional
import hashlib
import secrets

from ..database import teachers_collection, verify_password

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


def hash_session_token(session_token: str) -> str:
    return hashlib.sha256(session_token.encode("utf-8")).hexdigest()


def require_signed_in_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Resolve a valid bearer token to its teacher account."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")

    token_hash = hash_session_token(authorization.removeprefix("Bearer "))
    teacher = teachers_collection.find_one({"session_token_hash": token_hash})
    if not teacher:
        raise HTTPException(status_code=401, detail="Invalid session")
    return teacher


@router.post("/login")
def login(username: str, password: str) -> Dict[str, Any]:
    """Login a teacher account"""
    # Find the teacher in the database
    teacher = teachers_collection.find_one({"_id": username})

    # Verify password using Argon2 verifier from database.py
    if not teacher or not verify_password(teacher.get("password", ""), password):
        raise HTTPException(
            status_code=401, detail="Invalid username or password")

    session_token = secrets.token_urlsafe(32)
    teachers_collection.update_one(
        {"_id": username},
        {"$set": {"session_token_hash": hash_session_token(session_token)}}
    )

    # Return teacher information (excluding password)
    return {
        "username": teacher["username"],
        "display_name": teacher["display_name"],
        "role": teacher["role"],
        "session_token": session_token
    }


@router.get("/check-session")
def check_session(
    username: str,
    teacher: Dict[str, Any] = Depends(require_signed_in_user)
) -> Dict[str, Any]:
    """Check if a session is valid by username"""
    if teacher["_id"] != username:
        raise HTTPException(status_code=401, detail="Invalid session")

    return {
        "username": teacher["username"],
        "display_name": teacher["display_name"],
        "role": teacher["role"]
    }


@router.post("/logout")
def logout(teacher: Dict[str, Any] = Depends(require_signed_in_user)) -> Dict[str, str]:
    """Invalidate the current teacher session."""
    result = teachers_collection.update_one(
        {"_id": teacher["_id"]},
        {"$unset": {"session_token_hash": ""}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=401, detail="Invalid session")
    return {"message": "Logged out"}
