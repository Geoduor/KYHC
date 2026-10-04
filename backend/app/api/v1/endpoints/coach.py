from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.pagination import Pagination
from app.core.roles import MANAGEMENT_ROLES
from app.database.dependencies import get_db
from app.dependencies.auth import get_current_user, require_roles
from app.models.coach import Coach
from app.models.user import User
from app.repositories.coach_repository import CoachRepository
from app.repositories.team_repository import TeamRepository
from app.schemas.common import Page
from app.schemas.coach import CoachCreate, CoachResponse, CoachUpdate

router = APIRouter()


@router.get(
    "/",
    response_model=Page[CoachResponse],
)
def get_coaches(
    db: Session = Depends(get_db),
    pagination: Pagination = Depends(),
    search: str | None = Query(
        None,
        description="Search by name or email",
    ),
    team_id: int | None = Query(
        None,
        description="Filter by team",
    ),
    is_active: bool | None = Query(
        None,
        description="Filter by active status",
    ),
    current_user: User = Depends(get_current_user),
):
    """
    List coaches with pagination and filters.
    """

    items, total = CoachRepository.get_all(
        db,
        skip=pagination.skip,
        limit=pagination.limit,
        search=search,
        team_id=team_id,
        is_active=is_active,
    )

    return Page(
        items=items,
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.post(
    "/",
    response_model=CoachResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_coach(
    coach: CoachCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(*MANAGEMENT_ROLES)
    ),
):
    """
    Create a new coach.
    """

    team = TeamRepository.get_by_id(
        db,
        coach.team_id,
    )

    if team is None:
        raise HTTPException(
            status_code=404,
            detail="Team not found",
        )

    existing_coach = CoachRepository.get_by_email(
        db,
        coach.email,
    )

    if existing_coach:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coach email already registered",
        )

    db_coach = Coach(**coach.model_dump())

    return CoachRepository.create(
        db,
        db_coach,
    )


@router.get(
    "/{coach_id}",
    response_model=CoachResponse,
)
def get_coach(
    coach_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get one coach.
    """

    coach = CoachRepository.get_by_id(
        db,
        coach_id,
    )

    if coach is None:
        raise HTTPException(
            status_code=404,
            detail="Coach not found",
        )

    return coach


@router.put(
    "/{coach_id}",
    response_model=CoachResponse,
)
def update_coach(
    coach_id: int,
    coach_update: CoachUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(*MANAGEMENT_ROLES)
    ),
):
    """
    Update a coach.
    """

    coach = CoachRepository.get_by_id(
        db,
        coach_id,
    )

    if coach is None:
        raise HTTPException(
            status_code=404,
            detail="Coach not found",
        )

    update_data = coach_update.model_dump(exclude_unset=True)

    new_team_id = update_data.get("team_id")

    if new_team_id is not None:
        team = TeamRepository.get_by_id(
            db,
            new_team_id,
        )

        if team is None:
            raise HTTPException(
                status_code=404,
                detail="Team not found",
            )

    new_email = update_data.get("email")

    if new_email and new_email != coach.email:
        existing_coach = CoachRepository.get_by_email(
            db,
            new_email,
        )

        if existing_coach:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Coach email already registered",
            )

    for key, value in update_data.items():
        setattr(coach, key, value)

    return CoachRepository.update(
        db,
        coach,
    )


@router.delete(
    "/{coach_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_coach(
    coach_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*MANAGEMENT_ROLES)),
):
    """
    Delete a coach.
    """

    coach = CoachRepository.get_by_id(
        db,
        coach_id,
    )

    if coach is None:
        raise HTTPException(
            status_code=404,
            detail="Coach not found",
        )

    CoachRepository.delete(
        db,
        coach,
    )
