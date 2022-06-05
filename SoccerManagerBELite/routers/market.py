import sys
sys.path.append('..')

from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter
import exceptions
import authorizations
import crud
import schemas
from database import get_db


router = APIRouter(
    prefix='/market',
    tags=['market']
)


@router.get("/sell")
def sell_player(
        player_id: int,
        asking_price: int,
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
    if asking_price <= 0:
        raise exceptions.invalid_price()
    if player.on_market:
        msg = 'player already on the market, updated price'
    else:
        msg = 'player put on the market'
    db_player = crud.put_player_for_sale(db, player, asking_price)
    return {'msg': msg, 'player': schemas.MarketPlayer.from_orm(db_player)}


@router.get("/withdraw")
def withdraw_player(
        player_id: int,
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
    if not player.on_market:
        raise exceptions.player_not_on_sale()
    db_player = crud.remove_player_for_sale(db, player)
    msg = 'player withdrawn from market listing'
    return {'msg': msg, 'player': schemas.MarketPlayer.from_orm(db_player)}


@router.get("/buy")
def buy_player(
        player_id: int,
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
    if player.team_id == user_team.id:
        raise exceptions.player_already_yours()
    if player.requested_value > user_team.budget:
        raise exceptions.insufficient_funds()
    db_player = crud.acquire_player(db, player, user_team)
    msg = 'player acquired'
    return {'msg': msg, 'player': schemas.MarketPlayer.from_orm(db_player)}


@router.get("/")
def market_list(db: Session = Depends(get_db)):
    db_market_players = crud.get_players_on_market(db)
    market_players = [schemas.MarketPlayer.from_orm(player) for player in db_market_players]
    return db_market_players

