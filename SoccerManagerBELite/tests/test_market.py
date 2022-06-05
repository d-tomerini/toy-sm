import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app
from params import budget, initial_player_value, markup

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


def test_empty_market(test_db):
    response = client.get("/market")
    assert response.status_code == 200
    assert response.json() == []


def test_put_player_on_market(test_db):
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
        "/market/sell?player_id=10&asking_price=1100000",
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.json()
    assert response.status_code == 200
    assert data['msg'] == 'player put on the market'
    assert data['player']['on_market']
    assert data['player']['requested_value'] == 1100000


def test_withdraw_player_from_market(test_db):
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
        "/market/sell?player_id=10&asking_price=1100000",
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.get(
        "/market/withdraw?player_id=10&asking_price=1100000",
        headers={"Authorization": f"Bearer {token}"},
    )
    data = response.json()
    assert response.status_code == 200
    assert data['msg'] == 'player withdrawn from market listing'
    assert not data['player']['on_market']
    assert data['player']['requested_value'] is None


def test_put_player_on_market_not_yours(test_db):
    user1 = {"username": "user@example.com", "password": "password"}
    user2 = {"username": "user2@example.com", "password": "password"}
    for user in (user1, user2):
        response = client.post(
            "/auth/register",
            json=user
        )
    response = client.post(
        "/auth/login",
        data=user1
    )
    token = response.json()['token']
    response = client.get(
        "/market/sell?player_id=30&asking_price=1100000",
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.json()
    assert response.status_code == 400
    assert data['detail'] == "player with the given id does not belong to user"


def test_exchange_player_on_market(test_db):
    user1 = {"username": "user@example.com", "password": "password"}
    user2 = {"username": "user2@example.com", "password": "password"}
    price = 1100000
    for user in (user1, user2):
        response = client.post(
            "/auth/register",
            json=user
        )
    response = client.post(
        "/auth/login",
        data=user1
    )
    token1 = response.json()['token']
    response = client.get(
        f"/market/sell?player_id=10&asking_price={price}",
        headers={"Authorization": f"Bearer {token1}"},
    )

    response = client.post(
        "/auth/login",
        data=user2
    )
    token2 = response.json()['token']
    response = client.get(
        "/market/buy?player_id=10",
        headers={"Authorization": f"Bearer {token2}"},
    )

    data = response.json()
    assert response.status_code == 200
    assert data['msg'] == 'player acquired'
    assert data['player']['team_id'] == '2'
    assert initial_player_value < data['player']['value'] < initial_player_value * (1 + markup['max'] / 100)

    response = client.get(
        "/team/user",
        headers={"Authorization": f"Bearer {token1}"},
    )

    new_budget1 = response.json()['budget']
    assert new_budget1 == budget + price

    response = client.get(
        "/team/user",
        headers={"Authorization": f"Bearer {token2}"},
    )

    new_budget2 = response.json()['budget']
    assert new_budget2 == budget - price


def test_exchange_player_on_market_price_too_high(test_db):
    user1 = {"username": "user@example.com", "password": "password"}
    user2 = {"username": "user2@example.com", "password": "password"}
    price = budget * 2
    for user in (user1, user2):
        response = client.post(
            "/auth/register",
            json=user
        )
    response = client.post(
        "/auth/login",
        data=user1
    )
    token1 = response.json()['token']
    response = client.get(
        f"/market/sell?player_id=10&asking_price={price}",
        headers={"Authorization": f"Bearer {token1}"},
    )

    response = client.post(
        "/auth/login",
        data=user2
    )
    token2 = response.json()['token']
    response = client.get(
        "/market/buy?player_id=10",
        headers={"Authorization": f"Bearer {token2}"},
    )

    assert response.status_code == 400
