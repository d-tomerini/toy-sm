from pydantic import BaseModel, EmailStr
from typing import Optional
from params import Role


class User(BaseModel):
    email: EmailStr
    password: str

    class Config:
        orm_mode = True


class Team(BaseModel):
    user_id: str
    name: str
    country: str
    budget: int
    value: Optional[int]

    class Config:
        orm_mode = True


class Player(BaseModel):
    name: str
    surname: str
    country: str
    role: Role
    age: int
    value: int
    team_id: str


class Db_Player(BaseModel):
    id: int
    name: str
    surname: str
    country: str
    role: Role
    age: int
    value: int
    team_id: str

    class Config:
        orm_mode = True



class MarketPlayer(Player):
    on_market: bool
    requested_value: Optional[int]

    class Config:
        orm_mode = True
