from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)

    team = relationship('Team', back_populates='user')


class Team(Base):
    __tablename__ = 'team'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    name = Column(String)
    country = Column(String)
    budget = Column(Integer)

    user = relationship('User', back_populates='team')
    players = relationship('Player', back_populates='team')


class Player(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    surname = Column(String)
    country = Column(String)
    role = Column(String)
    age = Column(Integer)
    team_id = Column(Integer, ForeignKey("team.id"))
    value = Column(Integer)
    on_market = Column(Boolean)
    requested_value = Column(Integer)

    team = relationship('Team', back_populates='players')
