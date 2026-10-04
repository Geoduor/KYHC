from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.dependencies.auth import get_current_user
from app.models.coach import Coach
from app.repositories.coach_repository import CoachRepository
from app.schemas.coach import CoachCreate, CoachResponse, CoachUpdate

router = APIRouter()


@router.get(
    "/",
    response_model=list[CoachResponse],
)
def get_coaches(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get all coaches.
    """
    return CoachRepository.get_all(db)


@router.post(
    "/",
    response_model=CoachResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_coach(
    coach: CoachCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Create a new coach.
    """
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
    current_user=Depends(get_current_user),
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
    current_user=Depends(get_current_user),
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
    current_user=Depends(get_current_user),
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