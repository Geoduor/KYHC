from typing import Optional

from pydantic import BaseModel, ConfigDict


class PlayerStatisticBase(BaseModel):
    player_id: int
    match_id: int
    goals: int = 0
    assists: int = 0
    shots: int = 0
    shots_on_target: int = 0
    passes: int = 0
    successful_passes: int = 0
    interceptions: int = 0
    tackles: int = 0
    green_cards: int = 0
    yellow_cards: int = 0
    red_cards: int = 0
    minutes_played: int = 0
    rating: float = 0.0
    mvp: bool = False


class PlayerStatisticCreate(PlayerStatisticBase):
    pass


class PlayerStatisticUpdate(BaseModel):
    goals: Optional[int] = None
    assists: Optional[int] = None
    shots: Optional[int] = None
    shots_on_target: Optional[int] = None
    passes: Optional[int] = None
    successful_passes: Optional[int] = None
    interceptions: Optional[int] = None
    tackles: Optional[int] = None
    green_cards: Optional[int] = None
    yellow_cards: Optional[int] = None
    red_cards: Optional[int] = None
    minutes_played: Optional[int] = None
    rating: Optional[float] = None
    mvp: Optional[bool] = None


class PlayerStatisticResponse(PlayerStatisticBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True,
    )