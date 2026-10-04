from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.database.dependencies import get_db
from app.models.user import User
from app.repositories.player_statistic_repository import (
    PlayerStatisticRepository,
)
from app.schemas.player_statistic import (
    PlayerStatisticCreate,
    PlayerStatisticResponse,
    PlayerStatisticUpdate,
)

router = APIRouter()


@router.get(
    "/",
    response_model=list[PlayerStatisticResponse],
)
def get_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return PlayerStatisticRepository.get_all(db)


@router.get(
    "/{statistic_id}",
    response_model=PlayerStatisticResponse,
)
def get_statistic(
    statistic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    statistic = PlayerStatisticRepository.get_by_id(
        db,
        statistic_id,
    )

    if not statistic:
        raise HTTPException(
            status_code=404,
            detail="Statistic not found",
        )

    return statistic


@router.post(
    "/",
    response_model=PlayerStatisticResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_statistic(
    statistic: PlayerStatisticCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return PlayerStatisticRepository.create(
        db,
        statistic,
    )


@router.put(
    "/{statistic_id}",
    response_model=PlayerStatisticResponse,
)
def update_statistic(
    statistic_id: int,
    statistic: PlayerStatisticUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_statistic = PlayerStatisticRepository.get_by_id(
        db,
        statistic_id,
    )

    if not db_statistic:
        raise HTTPException(
            status_code=404,
            detail="Statistic not found",
        )

    return PlayerStatisticRepository.update(
        db,
        db_statistic,
        statistic,
    )


@router.delete(
    "/{statistic_id}",
)
def delete_statistic(
    statistic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_statistic = PlayerStatisticRepository.get_by_id(
        db,
        statistic_id,
    )

    if not db_statistic:
        raise HTTPException(
            status_code=404,
            detail="Statistic not found",
        )

    PlayerStatisticRepository.delete(
        db,
        db_statistic,
    )

    return {
        "message": "Statistic deleted successfully"
    }