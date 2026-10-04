from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.pagination import Pagination
from app.core.roles import MANAGEMENT_ROLES
from app.database.dependencies import get_db
from app.dependencies.auth import get_current_user, require_roles
from app.models.player import Player
from app.models.user import User
from app.repositories.player_repository import PlayerRepository
from app.repositories.team_repository import TeamRepository
from app.schemas.common import Page
from app.schemas.player import (
    PlayerCreate,
    PlayerResponse,
    PlayerUpdate,
)

router = APIRouter()


@router.post(
    "/",
    response_model=PlayerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_player(
    player: PlayerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(*MANAGEMENT_ROLES)
    ),
):
    """
    Create a new player.
    """

    team = TeamRepository.get_by_id(
        db,
        player.team_id,
    )

    if team is None:
        raise HTTPException(
            status_code=404,
            detail="Team not found",
        )

    db_player = Player(
        **player.model_dump()
    )

    return PlayerRepository.create(
        db,
        db_player,
    )


@router.get(
    "/",
    response_model=Page[PlayerResponse],
)
def get_players(
    db: Session = Depends(get_db),
    pagination: Pagination = Depends(),
    search: str | None = Query(
        None,
        description="Search by first or last name",
    ),
    team_id: int | None = Query(
        None,
        description="Filter by team",
    ),
    position: str | None = Query(
        None,
        description="Filter by position",
    ),
    is_active: bool | None = Query(
        None,
        description="Filter by active status",
    ),
    current_user: User = Depends(get_current_user),
):
    """
    List players with pagination and filters.
    """

    items, total = PlayerRepository.get_all(
        db,
        skip=pagination.skip,
        limit=pagination.limit,
        search=search,
        team_id=team_id,
        position=position,
        is_active=is_active,
    )

    return Page(
        items=items,
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.get(
    "/{player_id}",
    response_model=PlayerResponse,
)
def get_player(
    player_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get one player.
    """

    player = PlayerRepository.get_by_id(
        db,
        player_id,
    )

    if player is None:
        raise HTTPException(
            status_code=404,
            detail="Player not found",
        )

    return player


@router.put(
    "/{player_id}",
    response_model=PlayerResponse,
)
def update_player(
    player_id: int,
    player_data: PlayerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(*MANAGEMENT_ROLES)
    ),
):
    """
    Update a player.
    """

    player = PlayerRepository.get_by_id(
        db,
        player_id,
    )

    if player is None:
        raise HTTPException(
            status_code=404,
            detail="Player not found",
        )

    update_data = player_data.model_dump(
        exclude_unset=True,
    )

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

    for key, value in update_data.items():
        setattr(
            player,
            key,
            value,
        )

    return PlayerRepository.update(
        db,
        player,
    )


@router.delete(
    "/{player_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_player(
    player_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*MANAGEMENT_ROLES)),
):
    """
    Delete a player.
    """

    player = PlayerRepository.get_by_id(
        db,
        player_id,
    )

    if player is None:
        raise HTTPException(
            status_code=404,
            detail="Player not found",
        )

    PlayerRepository.delete(
        db,
        player,
    )
