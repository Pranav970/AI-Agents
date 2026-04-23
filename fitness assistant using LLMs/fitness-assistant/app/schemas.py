from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Literal, Optional


Gender = Literal["male", "female", "other"]


class UserProfile(BaseModel):
    age: Optional[int] = Field(default=None, ge=5, le=120)
    gender: Optional[Gender] = None
    weight_kg: Optional[float] = Field(default=None, gt=0, le=500)
    height_cm: Optional[float] = Field(default=None, gt=0, le=300)
    activity_level: Optional[str] = None
    goal: Optional[str] = None
    workouts_per_week: Optional[int] = Field(default=None, ge=0, le=14)
    equipment: Optional[str] = None
    diet_pref: Optional[str] = None


class ChatRequest(BaseModel):
    session_id: str = Field(default="default")
    message: str
    profile: Optional[UserProfile] = None


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    intent: str
    tool_used: Optional[str] = None
    tool_result: Optional[dict] = None
