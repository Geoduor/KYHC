from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.users import router as users_router
from app.api.v1.endpoints.team import router as team_router
from app.api.v1.endpoints.player import router as player_router
from app.api.v1.endpoints.coach import router as coach_router
from app.api.v1.endpoints.match import router as match_router
from app.api.v1.endpoints.match_event import router as match_event_router
from app.api.v1.endpoints.statistics import router as statistics_router
from app.api.v1.endpoints.training_session import (
    router as training_session_router,
)
from app.api.v1.endpoints.training_attendance import (
    router as training_attendance_router,
)
from app.api.v1.endpoints.player_statistic import (
    router as player_statistic_router,
)

api_router = APIRouter()

api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"],
)

api_router.include_router(
    users_router,
    prefix="/users",
    tags=["Users"],
)

api_router.include_router(
    team_router,
    prefix="/teams",
    tags=["Teams"],
)

api_router.include_router(
    player_router,
    prefix="/players",
    tags=["Players"],
)

api_router.include_router(
    coach_router,
    prefix="/coaches",
    tags=["Coaches"],
)

api_router.include_router(
    match_router,
    prefix="/matches",
    tags=["Matches"],
)

api_router.include_router(
    match_event_router,
    prefix="/match-events",
    tags=["Match Events"],
)

api_router.include_router(
    statistics_router,
    prefix="/statistics",
    tags=["Statistics"],
)

api_router.include_router(
    training_session_router,
    prefix="/training-sessions",
    tags=["Training Sessions"],
)

api_router.include_router(
    training_attendance_router,
    prefix="/training-attendance",
    tags=["Training Attendance"],
)

api_router.include_router(
    player_statistic_router,
    prefix="/player-statistics",
    tags=["Player Statistics"],
)