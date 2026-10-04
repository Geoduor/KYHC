from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.pagination import Pagination
from app.core.roles import COACHING_ROLES
from app.database.dependencies import get_db
from app.dependencies.auth import get_current_user, require_roles
from app.models.user import User
from app.repositories.coach_repository import CoachRepository
from app.repositories.training_session_repository import (
    TrainingSessionRepository,
)
from app.schemas.common import Page
from app.schemas.training_session import (
    TrainingSessionCreate,
    TrainingSessionResponse,
    TrainingSessionUpdate,
)

router = APIRouter()


@router.get(
    "/",
    response_model=Page[TrainingSessionResponse],
)
def get_training_sessions(
    db: Session = Depends(get_db),
    pagination: Pagination = Depends(),
    coach_id: int | None = Query(
        None,
        description="Filter by coach",
    ),
    is_completed: bool | None = Query(
        None,
        description="Filter by completion status",
    ),
    current_user: User = Depends(get_current_user),
):
    """
    List training sessions with pagination and filters.
    """

    items, total = TrainingSessionRepository.get_all(
        db,
        skip=pagination.skip,
        limit=pagination.limit,
        coach_id=coach_id,
        is_completed=is_completed,
    )

    return Page(
        items=items,
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.post(
    "/",
    response_model=TrainingSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_training_session(
    session: TrainingSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(*COACHING_ROLES)
    ),
):
    """
    Create a training session.
    """

    coach = CoachRepository.get_by_id(
        db,
        session.coach_id,
    )

    if coach is None:
        raise HTTPException(
            status_code=404,
            detail="Coach not found",
        )

    return TrainingSessionRepository.create(
        db,
        session,
    )


@router.get(
    "/{session_id}",
    response_model=TrainingSessionResponse,
)
def get_training_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get one training session.
    """

    session = TrainingSessionRepository.get_by_id(
        db,
        session_id,
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Training session not found",
        )

    return session


@router.put(
    "/{session_id}",
    response_model=TrainingSessionResponse,
)
def update_training_session(
    session_id: int,
    session: TrainingSessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(*COACHING_ROLES)
    ),
):
    """
    Update a training session.
    """

    db_session = TrainingSessionRepository.get_by_id(
        db,
        session_id,
    )

    if not db_session:
        raise HTTPException(
            status_code=404,
            detail="Training session not found",
        )

    if session.coach_id is not None:
        coach = CoachRepository.get_by_id(
            db,
            session.coach_id,
        )

        if coach is None:
            raise HTTPException(
                status_code=404,
                detail="Coach not found",
            )

    return TrainingSessionRepository.update(
        db,
        db_session,
        session,
    )


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_training_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*COACHING_ROLES)),
):
    """
    Delete a training session.
    """

    db_session = TrainingSessionRepository.get_by_id(
        db,
        session_id,
    )

    if not db_session:
        raise HTTPException(
            status_code=404,
            detail="Training session not found",
        )

    TrainingSessionRepository.delete(
        db,
        db_session,
    )

    return None
