from sqlalchemy.orm import Session
import models
import schemas
import utils
from auth import get_password_hash, verify_password
from typing import List
from sqlalchemy import func


def get_user_by_id(db: Session, user_id: int) -> models.User:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> models.User:
    return db.query(models.User).filter(models.User.email == email).first()


def get_team_by_user_id(db: Session, user_id: int) -> models.Team:
    return db.query(models.Team).filter(models.Team.user_id == user_id).first()


def get_team_by_team_id(db: Session, team_id: int) -> models.Team:
    return db.query(models.Team).filter(models.Team.id == team_id).first()


def get_players_by_team_id(db: Session, team_id: int) -> List[models.Player]:
    return db.query(models.Player).filter(models.Player.team_id == team_id).all()


def get_player_by_player_id(db: Session, player_id: int) -> models.Player:
    return db.query(models.Player).filter(models.Player.id == player_id).first()


def get_players_on_market(db: Session) -> List[models.Player]:
    return db.query(models.Player).where(models.Player.on_market).all()


def create_user(db: Session, user: schemas.User) -> models.User:
    db_user = models.User(
        email=user.email,
        hashed_password=get_password_hash(user.password))
    db.add(db_user)
    db.commit()
    return db_user


def create_team(db: Session, team: schemas.Team):
    db_team = models.Team(
        name=team.name,
        user_id=team.user_id,
        budget=team.budget,
        country=team.country
    )
    db.add(db_team)
    db.commit()
    return db_team


def create_players(db: Session, players: List[schemas.MarketPlayer]):
    for player in players:
        db_player = models.Player(
            name=player.name,
            surname=player.surname,
            country=player.country,
            role=player.role,
            age=player.age,
            team_id=player.team_id,
            value=player.value,
            on_market=player.on_market,
            requested_value=player.requested_value
        )
        db.add(db_player)
    db.commit()
    return


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def update_team(db:Session, team: models.Team, team_name, country):
    if team_name:
        team.name = team_name
    if country:
        team.country = country
    db.commit()
    return team


def update_player(db, player: models.Player, player_name, player_surname, player_country):
    if player_name:
        player.name = player_name
    if player_surname:
        player.surname = player_surname
    if player_country:
        player.country = player_country
    db.commit()
    return player



def add_team_value(db: Session, team: models.Team):
    # augmented_team = db.query(models.Team, models.Player.team_id, func.sum(models.Player.value).label('value'))\
    #    .filter(models.Player.team_id == models.Team.id).all()
    # augmented_team = db.query(models.Player).join(models.Team).all()
    # return augmented_team
    return team


def put_player_for_sale(db: Session, player: models.Player, price: int):
    player.on_market = True
    player.requested_value = price
    db.commit()
    return player


def acquire_player(db: Session, player: models.Player, user_team: models.Team):
    seller_team = get_team_by_team_id(db, player.team_id)
    user_team.budget -= player.requested_value
    seller_team.budget += player.requested_value
    player.team_id = user_team.id
    player.value = utils.random_markup(player.value)
    player.on_market = False
    player.requested_value = None
    db.commit()
    return player
