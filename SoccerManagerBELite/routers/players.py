import sys
sys.path.append('..')

from fastapi import APIRouter
from sqlalchemy.orm import Session
from database import get_db
from fastapi import Depends
import exceptions
import authorizations
import crud
import schemas


router = APIRouter(
    prefix='/players',
    tags=['players']
)

@router.get("/update")
def get_update_players(
        player_id: int,
        player_name: str = None, player_surname: str = None, player_country: str = None,
        email: str = Depends(authorizations.get_email_from_token),
        db: Session = Depends(get_db)
        ):
    user = crud.get_user_by_email(db, email)
    if not user:
        raise exceptions.user_exception()
    player = crud.get_player_by_player_id(db, player_id)
    if not player:
        raise exceptions.player_does_not_exist()
    user_team = crud.get_team_by_user_id(db, user.id)
    if player.team_id != user_team.id:
        raise exceptions.player_unavailable()
    updated_player = crud.update_player(db, player, player_name, player_surname, player_country)
    return schemas.Db_Player.from_orm(updated_player)


@router.get("/user")
def get_players_list(email: str = Depends(authorizations.get_email_from_token), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email)
    if not user:
        raise exceptions.user_exception()
    team = crud.get_team_by_user_id(db, user.id)
    db_players = crud.get_players_by_team_id(db, team.id)
    players = [schemas.Db_Player.from_orm(player) for player in db_players]
    return players
