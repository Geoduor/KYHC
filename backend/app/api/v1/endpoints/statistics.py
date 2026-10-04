from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.dependencies.auth import get_current_user

from app.models.player import Player

from app.services.statistics_service import StatisticsService

router = APIRouter()


@router.get("/player/{player_id}")
def get_player_statistics(
    player_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Return statistics for a single player.
    """

    player = db.get(Player, player_id)

    if player is None:
        raise HTTPException(
            status_code=404,
            detail="Player not found",
        )

    return {
        "player_id": player.id,
        "player_name": f"{player.first_name} {player.last_name}",
        "goals": StatisticsService.player_goals(
            db,
            player.id,
        ),
        "assists": StatisticsService.player_assists(
            db,
            player.id,
        ),
        "cards": StatisticsService.player_cards(
            db,
            player.id,
        ),
    }