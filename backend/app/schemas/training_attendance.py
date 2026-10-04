from datetime import time
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.attendance_status import AttendanceStatus


class TrainingAttendanceBase(BaseModel):
    training_session_id: int
    player_id: int
    status: AttendanceStatus
    arrival_time: Optional[time] = None
    notes: Optional[str] = None


class TrainingAttendanceCreate(TrainingAttendanceBase):
    pass


class TrainingAttendanceUpdate(BaseModel):
    status: Optional[AttendanceStatus] = None
    arrival_time: Optional[time] = None
    notes: Optional[str] = None


class TrainingAttendanceResponse(TrainingAttendanceBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True,
    )