from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.pagination import Pagination
from app.core.roles import MANAGEMENT_ROLES
from app.database.dependencies import get_db
from app.dependencies.auth import get_current_user, require_roles

from app.models.match import Match
from app.models.team import Team
from app.models.user import User

from app.repositories.match_repository import MatchRepository

from app.schemas.common import Page
from app.schemas.match import (
    MatchCreate,
    MatchUpdate,
    MatchResponse,
)

router = APIRouter()


@router.get(
    "/",
    response_model=Page[MatchResponse],
)
def get_matches(
    db: Session = Depends(get_db),
    pagination: Pagination = Depends(),
    team_id: int | None = Query(
        None,
        description="Filter by team (home or away)",
    ),
    status_filter: str | None = Query(
        None,
        alias="status",
        description="Filter by status",
    ),
    competition: str | None = Query(
        None,
        description="Filter by competition",
    ),
    upcoming_only: bool = Query(
        False,
        description="Only return scheduled matches",
    ),
    current_user: User = Depends(get_current_user),
):
    """
    List matches with pagination and filters.
    """

    items, total = MatchRepository.get_all(
        db,
        skip=pagination.skip,
        limit=pagination.limit,
        team_id=team_id,
        status=status_filter,
        competition=competition,
        upcoming_only=upcoming_only,
    )

    return Page(
        items=items,
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.post(
    "/",
    response_model=MatchResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_match(
    match: MatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(*MANAGEMENT_ROLES)
    ),
):
    """
    Create a new match.
    """

    home_team = db.get(
        Team,
        match.home_team_id,
    )

    if home_team is None:
        raise HTTPException(
            status_code=404,
            detail="Home team not found",
        )

    away_team = db.get(
        Team,
        match.away_team_id,
    )

    if away_team is None:
        raise HTTPException(
            status_code=404,
            detail="Away team not found",
        )

    if match.home_team_id == match.away_team_id:
        raise HTTPException(
            status_code=400,
            detail="Home team and away team cannot be the same.",
        )

    db_match = Match(
        match_date=match.match_date,
        venue=match.venue,
        competition=match.competition,
        home_team_id=match.home_team_id,
        away_team_id=match.away_team_id,
        home_score=match.home_score,
        away_score=match.away_score,
        status=match.status,
    )

    return MatchRepository.create(
        db,
        db_match,
    )


@router.get(
    "/{match_id}",
    response_model=MatchResponse,
)
def get_match(
    match_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a match by ID.
    """

    match = MatchRepository.get_by_id(
        db,
        match_id,
    )

    if match is None:
        raise HTTPException(
            status_code=404,
            detail="Match not found",
        )

    return match


@router.put(
    "/{match_id}",
    response_model=MatchResponse,
)
def update_match(
    match_id: int,
    updated_match: MatchUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(*MANAGEMENT_ROLES)
    ),
):
    """
    Update a match.
    """

    match = MatchRepository.get_by_id(
        db,
        match_id,
    )

    if match is None:
        raise HTTPException(
            status_code=404,
            detail="Match not found",
        )

    update_data = updated_match.model_dump(
        exclude_unset=True,
    )

    home_team_id = update_data.get(
        "home_team_id",
        match.home_team_id,
    )

    away_team_id = update_data.get(
        "away_team_id",
        match.away_team_id,
    )

    if home_team_id == away_team_id:
        raise HTTPException(
            status_code=400,
            detail="Home team and away team cannot be the same.",
        )

    if "home_team_id" in update_data:
        if db.get(Team, home_team_id) is None:
            raise HTTPException(
                status_code=404,
                detail="Home team not found",
            )

    if "away_team_id" in update_data:
        if db.get(Team, away_team_id) is None:
            raise HTTPException(
                status_code=404,
                detail="Away team not found",
            )

    for key, value in update_data.items():
        setattr(
            match,
            key,
            value,
        )

    return MatchRepository.update(
        db,
        match,
    )


@router.delete(
    "/{match_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_match(
    match_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*MANAGEMENT_ROLES)),
):
    """
    Delete a match.
    """

    match = MatchRepository.get_by_id(
        db,
        match_id,
    )

    if match is None:
        raise HTTPException(
            status_code=404,
            detail="Match not found",
        )

    MatchRepository.delete(
        db,
        match,
    )
