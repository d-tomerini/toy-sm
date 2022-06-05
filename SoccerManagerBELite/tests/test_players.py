import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app
from params import initial_player_value, team_size

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


def test_check_players(test_db):
    """
    check that the team is created according to the specs'
    player age, value, role
    """
    user = {"username": "user@example.com", "password": "password"}
    client.post(
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
        "/players/user",
        headers={"Authorization": f"Bearer {token}"}
    )

    data = response.json()
    number_of_players = sum([n for n in team_size.values()])
    assert response.status_code == 200
    assert len(data) == number_of_players
    players = [player for player in data]
    players_age = [player['age'] for player in players]
    player_value = [player['value'] for player in players]
    player_role = [player['role'] for player in players]
    assert response.status_code == 200
    assert len(data) == number_of_players
    for age in players_age:
        assert 18 <= age <= 40
    for value in player_value:
        assert value == initial_player_value
    for role, n in team_size.items():
        roles = [r for r in player_role if r == role]
        assert len(roles) == n


def test_update_team_name(test_db):
    """
    update team name
    """
    user = {"username": "user@example.com", "password": "password"}
    client.post(
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
    client.post(
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
    client.post(
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


def test_update_players(test_db):
    """
    update player stats
    """
    user = {"username": "user@example.com", "password": "password"}
    client.post(
        "/auth/register",
        json=user
    )
    response = client.post(
        "/auth/login",
        data=user
    )
    token = response.json()['token']
    response = client.get(
        "/players/update?player_id=1&player_name=new name&player_surname=new surname&player_country=new_country",
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.json()
    assert response.status_code == 200
    assert data['name'] == 'new name'
    assert data['surname'] == 'new surname'
    assert data['country'] == 'new_country'


def test_player_id_invalid(test_db):
    """
    update player stats for an invalid player
    """
    user = {"username": "user@example.com", "password": "password"}
    client.post(
        "/auth/register",
        json=user
    )
    response = client.post(
        "/auth/login",
        data=user
    )
    token = response.json()['token']
    response = client.get(
        "/players/update?player_id=50&player_name=new name",
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.json()
    assert response.status_code == 400
    assert data == {"detail": "player does not exist"}


def test_player_not_yours(test_db):
    """
    update player stats for an invalid player
    """
    user1 = {"username": "user@example.com", "password": "password"}
    user2 = {"username": "user2@example.com", "password": "password"}
    for user in (user1, user2):
        client.post(
            "/auth/register",
            json=user
        )
    response = client.post(
        "/auth/login",
        data=user1
    )
    token = response.json()['token']
    response = client.get(
        "/players/update?player_id=25&player_name=new name",
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.json()
    assert response.status_code == 400
    assert data == {'detail': 'player with the given id does not belong to user'}
