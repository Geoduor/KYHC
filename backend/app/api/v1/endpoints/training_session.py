from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.database.dependencies import get_db
from app.models.user import User
from app.repositories.training_session_repository import (
    TrainingSessionRepository,
)
from app.schemas.training_session import (
    TrainingSessionCreate,
    TrainingSessionResponse,
    TrainingSessionUpdate,
)

router = APIRouter()


@router.get(
    "/",
    response_model=list[TrainingSessionResponse],
)
def get_training_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TrainingSessionRepository.get_all(db)


@router.post(
    "/",
    response_model=TrainingSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_training_session(
    session: TrainingSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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
    current_user: User = Depends(get_current_user),
):
    db_session = TrainingSessionRepository.get_by_id(
        db,
        session_id,
    )

    if not db_session:
        raise HTTPException(
            status_code=404,
            detail="Training session not found",
        )

    return TrainingSessionRepository.update(
        db,
        db_session,
        session,
    )


@router.delete(
    "/{session_id}",
)
def delete_training_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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

    return {
        "message": "Training session deleted successfully"
    }