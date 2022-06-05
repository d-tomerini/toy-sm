import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app
from params import budget, initial_player_value, team_size

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture()
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_check_team(test_db):
    """
    check that the team is created according to the specs
    """
    user = {"username": "user@example.com", "password": "password"}
    response = client.post(
        "/auth/register",
        json=user
    )
    response = client.post(
        "/auth/login",
        data=user
    )
    json = response.json()
    token = json['token']
    response = client.get(
        "/team/user",
        headers={"Authorization": f"Bearer {token}"}
    )

    data = response.json()
    number_of_players = sum([n for n in team_size.values()])
    assert response.status_code == 200
    assert data['name'] == 'Team of user@example.com'
    assert data['country']
    assert data['budget'] == budget
    assert data['value'] == initial_player_value * number_of_players


def test_update_team_name(test_db):
    """
    update team name
    """
    user = {"username": "user@example.com", "password": "password"}
    response = client.post(
        "/auth/register",
        json=user
    )
    response = client.post(
        "/auth/login",
        data=user
    )
    token = response.json()['token']
    response = client.get(
        "/team/update?team_name=new name",
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.json()
    assert response.status_code == 200
    assert data['name'] == 'new name'


def test_update_team_country(test_db):
    """
    update team country
    """
    user = {"username": "user@example.com", "password": "password"}
    response = client.post(
        "/auth/register",
        json=user
    )
    response = client.post(
        "/auth/login",
        data=user
    )
    token = response.json()['token']
    response = client.get(
        "/team/update?team_country=new name",
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.json()
    assert response.status_code == 200
    assert data['country'] == 'new name'


def test_update_team_name_and_country(test_db):
    """
    update team stats
    """
    user = {"username": "user@example.com", "password": "password"}
    response = client.post(
        "/auth/register",
        json=user
    )
    response = client.post(
        "/auth/login",
        data=user
    )
    token = response.json()['token']
    response = client.get(
        "/team/update?team_name=new name&team_country=another name",
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.json()
    assert response.status_code == 200
    assert data['name'] == 'new name'
    assert data['country'] == 'another name'
