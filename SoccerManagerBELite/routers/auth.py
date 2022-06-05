from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
import exceptions
import crud
import schemas
from authorizations import SECRET_KEY, ALGORITHM
from database import get_db
from utils import generate_team, generate_players


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


@router.post("/login")
async def login_token(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    The function verify the user and password, and it returns a JWT token valid 30 minutes
    for authentication across the API
    :param data: username and password submitted as form
    :param db: the database session
    :return: json with 'msg' confirming validation and a 'token' object
    """
    user = crud.authenticate_user(db, data.username, data.password)
    if not user:
        raise exceptions.user_exception()
    token = create_access_token(user.username, timedelta(minutes=30))
    return {'msg': f'User {data.username} validated', 'token': token}


@router.post("/register")
async def create_user(user: schemas.User, db: Session = Depends(get_db)):
    """
    endpoint to register users in the database
    team is created, along with a standard set of players according to params
    :param user: username and password
    :param db: database session
    """
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise exceptions.user_exists()
    new_user = crud.create_user(db, user)
    team = generate_team(user=new_user)
    new_team = crud.create_team(db, team)
    players = generate_players(new_team)
    crud.create_players(db, players)
    return {'msg': 'User and team successfully created'}


def create_access_token(username: str, expires_by: Optional[timedelta] = None):
    """
    convenience function to create a JWT token from the username
    :param username: database user email
    :param expires_by: validity of the token
    :return: JWT token
    """
    if expires_by:
        expire = datetime.utcnow() + expires_by
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode = {
        'sub': username,
        'exp': expire
    }
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

