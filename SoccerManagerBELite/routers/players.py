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
        username: str = Depends(authorizations.get_username_from_token),
        db: Session = Depends(get_db)
        ):
    """
    API to update the updatable values of a player: name, surname and country, accessible as
    query with the stated keyword. ALl optional
    Nothing happens if no query is present, all other keys are ignored
    Player can be updated only by its user
    :param player_id: player id as from players database
    :param player_name: query key for the new name
    :param player_surname: query key for the new surname
    :param player_country: query key for the new country
    :param username: user that owns the player, identify by JWT token
    :param db: database session
    :return: updated player stats
    """
    user = crud.get_user_by_username(db, username)
    if not user:
        raise exceptions.user_exception()
    player = crud.get_player_by_player_id(db, player_id)
    if not player:
        raise exceptions.player_does_not_exist()
    user_team = crud.get_team_by_user_id(db, user.id)
    if player.team_id != user_team.id:
        raise exceptions.player_unavailable()
    updated_player = crud.update_player(db, player, player_name, player_surname, player_country)
    return schemas.DBPlayer.from_orm(updated_player)


@router.get("/user")
def get_players_list(username: str = Depends(authorizations.get_username_from_token), db: Session = Depends(get_db)):
    """
    Lists all the player that belong to the logged user, identified by JWT
    :param username: user identified
    :param db: database session
    :return: list of players that belong to the user team
    """
    user = crud.get_user_by_username(db, username)
    if not user:
        raise exceptions.user_exception()
    team = crud.get_team_by_user_id(db, user.id)
    db_players = crud.get_players_by_team_id(db, team.id)
    players = [schemas.DBPlayer.from_orm(player) for player in db_players]
    return players
