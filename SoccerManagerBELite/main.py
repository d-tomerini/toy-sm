import sqlalchemy
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordRequestForm
import exceptions
from core.config import settings
import auth
import crud
import models
import schemas
from utils import generate_team, generate_players
from datetime import timedelta


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION)

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.post("/login")
def login_token(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, data.username, data.password)
    if not user:
        raise exceptions.user_exception()
    token = auth.create_access_token(user.email, timedelta(minutes=30))
    return {'msg': f'User {data.username} validated', 'token': token}


@app.post("/register")
def create_user(user: schemas.User, db: Session = Depends(get_db)):
    """
    endpoint to register users in the database
    team is created, along with a standard set of players according to params
    :param user: email and password
    :param db: database session
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise exceptions.user_exists()
    new_user = crud.create_user(db, user)
    team = generate_team(user=new_user)
    new_team = crud.create_team(db, team)
    players = generate_players(new_team)
    crud.create_players(db, players)
    return {'msg': 'User and team successfully created'}


@app.get("/team/user")
def get_team_details(email: str = Depends(auth.get_email_from_token), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email)
    if not user:
        raise exceptions.user_exception()
    team = crud.get_team_by_user_id(db, user.id)
    team_value = crud.get_team_value(db, team)
    team_dict = schemas.Team.from_orm(team).dict()
    team_dict.update({'value': team_value})
    return team_dict


@app.get("/team/update")
def get_team_details(
        team_name: str = None, country: str = None,
        email: str = Depends(auth.get_email_from_token),
        db: Session = Depends(get_db)
        ):
    user = crud.get_user_by_email(db, email)
    if not user:
        raise exceptions.user_exception()
    team = crud.get_team_by_user_id(db, user.id)
    db_updated_team = crud.update_team(db, team, team_name, country)
    db_updated_team = crud.add_team_value(db, db_updated_team)
    updated_team = schemas.Team.from_orm(db_updated_team)
    return updated_team


@app.get("/players/update")
def get_team_details(
        player_id: int,
        player_name: str = None, player_surname: str = None, player_country: str = None,
        email: str = Depends(auth.get_email_from_token),
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


@app.get("/players/user")
def get_players_details(email: str = Depends(auth.get_email_from_token), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email)
    if not user:
        raise exceptions.user_exception()
    team = crud.get_team_by_user_id(db, user.id)
    db_players = crud.get_players_by_team_id(db, team.id)
    players = [schemas.Db_Player.from_orm(player) for player in db_players]
    return players


@app.get("/market/sell")
def sell_player(
        player_id: int,
        asking_price: int,
        email: str = Depends(auth.get_email_from_token),
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
    if asking_price < 0:
        raise exceptions.invalid_price()
    if player.on_market:
        msg = 'player already on the market, updated price'
    else:
        msg = 'player put on the market'
    db_player = crud.put_player_for_sale(db, player, asking_price)
    sold_player = schemas.Db_Player.from_orm(db_player)
    return msg, db_player


@app.get("/market/withdraw")
def sell_player(
        player_id: int,
        email: str = Depends(auth.get_email_from_token),
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
    return db_player

@app.get("/market/buy")
def buy_player(
        player_id: int,
        email: str = Depends(auth.get_email_from_token),
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
    return db_player


@app.get("/market")
def market_list(db: Session = Depends(get_db)):
    db_market_players = crud.get_players_on_market(db)
    market_players = [schemas.MarketPlayer.from_orm(player) for player in db_market_players]
    return db_market_players

