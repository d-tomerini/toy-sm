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
def get_team_details(username: str = Depends(authorizations.get_username_from_token), db: Session = Depends(get_db)):
    """
    lists the team stats, team of the user logged in
    :param username: team's owner, identified by the JWT token
    :param db: database session
    :return: team details from database
    """
    user = crud.get_user_by_username(db, username)
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
        username: str = Depends(authorizations.get_username_from_token),
        db: Session = Depends(get_db)
        ):
    """
    Updates the team variable available for update: its name and country.
    Only the owner can update its team
    :param team_name: the desired name
    :param team_country: the desired country
    :param username: logged user identified by JWT
    :param db: database session
    """
    user = crud.get_user_by_username(db, username)
    if not user:
        raise exceptions.user_exception()
    team = crud.get_team_by_user_id(db, user.id)
    db_updated_team = crud.update_team(db, team, team_name, team_country)
    team_value = crud.get_team_value(db, db_updated_team)
    team_dict = schemas.Team.from_orm(team).dict()
    team_dict.update({'value': team_value})
    return team_dict
