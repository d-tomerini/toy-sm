import sys
sys.path.append('..')

from database import get_db
from sqlalchemy.orm import Session
from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
import exceptions
import crud
import schemas
from utils import generate_team, generate_players
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends
from jose import jwt
from authorizations import SECRET_KEY, ALGORITHM

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


@router.post("/login")
def login_token(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, data.username, data.password)
    if not user:
        raise exceptions.user_exception()
    token = create_access_token(user.email, timedelta(minutes=30))
    return {'msg': f'User {data.username} validated', 'token': token}


@router.post("/register")
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


def create_access_token(username: str, expires_by: Optional[timedelta] = None):
    if expires_by:
        expire = datetime.utcnow() + expires_by
    else:
        expire = datetime.utcnow() + timedelta(minutes=15 )
    encode = {
        'sub': username,
        'exp': expire
    }
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
