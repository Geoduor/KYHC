from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TrainingSessionBase(BaseModel):
    title: str
    description: Optional[str] = None
    venue: str
    session_date: datetime
    duration_minutes: int
    focus_area: str
    coach_id: int


class TrainingSessionCreate(TrainingSessionBase):
    pass


class TrainingSessionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    venue: Optional[str] = None
    session_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    focus_area: Optional[str] = None
    coach_id: Optional[int] = None
    is_completed: Optional[bool] = None


class TrainingSessionResponse(TrainingSessionBase):
    id: int
    is_completed: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )