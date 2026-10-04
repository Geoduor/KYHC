from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.core.pagination import Pagination
from app.core.roles import COACHING_ROLES
from app.database.dependencies import get_db
from app.dependencies.auth import get_current_user, require_roles
from app.models.match import Match
from app.models.player import Player
from app.models.user import User
from app.repositories.player_statistic_repository import (
    PlayerStatisticRepository,
)
from app.schemas.common import Page
from app.schemas.player_statistic import (
    PlayerStatisticCreate,
    PlayerStatisticResponse,
    PlayerStatisticUpdate,
)

router = APIRouter()


@router.get(
    "/",
    response_model=Page[PlayerStatisticResponse],
)
def get_statistics(
    db: Session = Depends(get_db),
    pagination: Pagination = Depends(),
    player_id: int | None = Query(
        None,
        description="Filter by player",
    ),
    match_id: int | None = Query(
        None,
        description="Filter by match",
    ),
    mvp_only: bool = Query(
        False,
        description="Only return MVP records",
    ),
    current_user: User = Depends(get_current_user),
):
    """
    List player match statistics with pagination and filters.
    """

    items, total = PlayerStatisticRepository.get_all(
        db,
        skip=pagination.skip,
        limit=pagination.limit,
        player_id=player_id,
        match_id=match_id,
        mvp_only=mvp_only,
    )

    return Page(
        items=items,
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.get(
    "/{statistic_id}",
    response_model=PlayerStatisticResponse,
)
def get_statistic(
    statistic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get one statistics record.
    """

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
    current_user: User = Depends(
        require_roles(*COACHING_ROLES)
    ),
):
    """
    Record match statistics for a player.
    """

    player = db.get(Player, statistic.player_id)

    if player is None:
        raise HTTPException(
            status_code=404,
            detail="Player not found",
        )

    match = db.get(Match, statistic.match_id)

    if match is None:
        raise HTTPException(
            status_code=404,
            detail="Match not found",
        )

    existing = PlayerStatisticRepository.get_by_player_and_match(
        db,
        statistic.player_id,
        statistic.match_id,
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Statistics already recorded for this player and match",
        )

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
    current_user: User = Depends(
        require_roles(*COACHING_ROLES)
    ),
):
    """
    Update a statistics record.
    """

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
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_statistic(
    statistic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*COACHING_ROLES)),
):
    """
    Delete a statistics record.
    """

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

    return None
