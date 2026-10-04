from typing import Optional

from pydantic import BaseModel, ConfigDict
from app.models.enums import MatchEventType


class MatchEventBase(BaseModel):
    minute: int
    event_type: MatchEventType
    description: Optional[str] = None
    match_id: int
    player_id: int
    assisting_player_id: Optional[int] = None


class MatchEventCreate(MatchEventBase):
    pass


class MatchEventUpdate(BaseModel):
    minute: Optional[int] = None
    event_type: MatchEventType | None = None
    description: Optional[str] = None
    player_id: Optional[int] = None
    assisting_player_id: Optional[int] = None


class MatchEventResponse(MatchEventBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True,
    )