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
async def sell_player(
        player_id: int,
        asking_price: int,
        username: str = Depends(authorizations.get_username_from_token),
        db: Session = Depends(get_db)
        ):
    """
    API call to put a player on the market list.
    The player is available for exchange at the requested price
    Subsequent call of this function on the same player update the price
    :param player_id: integer id of the player in the database
    :param asking_price: integer price, greater than 0
    :param username: username extracted from the JWT
    :param db: database session
    :return: details of the player put on the market
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
    if asking_price <= 0:
        raise exceptions.invalid_price()
    if player.on_market:
        msg = 'player already on the market, updated price'
    else:
        msg = 'player put on the market'
    db_player = crud.put_player_for_sale(db, player, asking_price)
    return {'msg': msg, 'player': schemas.MarketPlayer.from_orm(db_player)}


@router.get("/withdraw")
async def withdraw_player(
        player_id: int,
        username: str = Depends(authorizations.get_username_from_token),
        db: Session = Depends(get_db)
        ):
    """
    Withdraws the player on market list, and returns it to the player.
    The player would not be available for sale
    :param player_id: player id on the database
    :param username: current user identified by JWT token
    :param db: database session
    :return: player details
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
    if not player.on_market:
        raise exceptions.player_not_on_sale()
    db_player = crud.remove_player_for_sale(db, player)
    msg = 'player withdrawn from market listing'
    return {'msg': msg, 'player': schemas.MarketPlayer.from_orm(db_player)}


@router.get("/buy")
async def buy_player(
        player_id: int,
        username: str = Depends(authorizations.get_username_from_token),
        db: Session = Depends(get_db)
        ):
    """
    Acquire the player from the market at the requested price.
    The transaction happens if the user has enough money to buy it, and gets it on its team
    The player is not on the market anymore, and its value is updated
    :param player_id: exchanged player id
    :param username: the user identified by the JWT token
    :param db: database session
    :return: player details
    """
    user = crud.get_user_by_username(db, username)
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
async def market_list(db: Session = Depends(get_db)):
    """
    List of all the players available on the market, with stats, team and price
    :param db: database session
    :return: list of the players
    """
    db_market_players = crud.get_players_on_market(db)
    market_players = [schemas.DBPlayer.from_orm(player) for player in db_market_players]
    return market_players
