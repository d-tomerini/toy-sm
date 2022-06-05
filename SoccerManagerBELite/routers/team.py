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
    prefix='/team',
    tags=['team']
)


@router.get("/user")
def get_team_details(email: str = Depends(authorizations.get_email_from_token), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email)
    if not user:
        raise exceptions.user_exception()
    team = crud.get_team_by_user_id(db, user.id)
    team_value = crud.get_team_value(db, team)
    team_dict = schemas.Team.from_orm(team).dict()
    team_dict.update({'value': team_value})
    return team_dict


@router.get("/update")
def update_team_details(
        team_name: str = None, team_country: str = None,
        email: str = Depends(authorizations.get_email_from_token),
        db: Session = Depends(get_db)
        ):
    user = crud.get_user_by_email(db, email)
    if not user:
        raise exceptions.user_exception()
    team = crud.get_team_by_user_id(db, user.id)
    db_updated_team = crud.update_team(db, team, team_name, team_country)
    team_value = crud.get_team_value(db, db_updated_team)
    team_dict = schemas.Team.from_orm(team).dict()
    team_dict.update({'value': team_value})
    return team_dict
