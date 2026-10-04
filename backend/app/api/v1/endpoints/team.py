from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.dependencies.auth import get_current_user
from app.models.team import Team
from app.models.user import User
from app.repositories.team_repository import TeamRepository
from app.schemas.team import (
    TeamCreate,
    TeamResponse,
    TeamUpdate,
)

router = APIRouter()


@router.post(
    "/",
    response_model=TeamResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_team(
    team: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new team.
    """

    existing_team = TeamRepository.get_by_name(
        db,
        team.name,
    )

    if existing_team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team already exists",
        )

    db_team = Team(
        name=team.name,
        category=team.category,
        description=team.description,
        coach_name=team.coach_name,
    )

    return TeamRepository.create(
        db,
        db_team,
    )


@router.get(
    "/",
    response_model=list[TeamResponse],
)
def get_teams(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return all teams.
    """
    return TeamRepository.get_all(db)


@router.get(
    "/{team_id}",
    response_model=TeamResponse,
)
def get_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return a team by ID.
    """

    team = TeamRepository.get_by_id(
        db,
        team_id,
    )

    if team is None:
        raise HTTPException(
            status_code=404,
            detail="Team not found",
        )

    return team


@router.put(
    "/{team_id}",
    response_model=TeamResponse,
)
def update_team(
    team_id: int,
    team_data: TeamUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a team.
    """

    team = TeamRepository.get_by_id(
        db,
        team_id,
    )

    if team is None:
        raise HTTPException(
            status_code=404,
            detail="Team not found",
        )

    update_data = team_data.model_dump(
        exclude_unset=True,
    )

    for key, value in update_data.items():
        setattr(team, key, value)

    return TeamRepository.update(
        db,
        team,
    )


@router.delete(
    "/{team_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a team.
    """

    team = TeamRepository.get_by_id(
        db,
        team_id,
    )

    if team is None:
        raise HTTPException(
            status_code=404,
            detail="Team not found",
        )

    TeamRepository.delete(
        db,
        team,
    )

    return None