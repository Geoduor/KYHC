from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MatchBase(BaseModel):
    home_team_id: int
    away_team_id: int
    competition: str
    venue: str
    match_date: datetime
    status: str = "Scheduled"
    home_score: int = 0
    away_score: int = 0
    notes: str | None = None


class MatchCreate(MatchBase):
    pass


class MatchUpdate(BaseModel):
    home_team_id: int | None = None
    away_team_id: int | None = None
    competition: str | None = None
    venue: str | None = None
    match_date: datetime | None = None
    status: str | None = None
    home_score: int | None = None
    away_score: int | None = None
    notes: str | None = None


class MatchResponse(MatchBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True,
    )