import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app

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


def test_create_user(test_db):
    """
    correct user creation
    """
    user = {"username": "user@example.com", "password": "password"}
    response = client.post(
        "/auth/register",
        json=user
    )
    assert response.status_code == 200


def test_bad_create_user(test_db):
    """
    user must be created by submitting a form where both 'username' and 'password'
    fields are present
    """
    # missing username key
    user1 = {"user": "user@example.com", "password": "password"}
    # missing password key
    user2 = {"username": "user@example.com", "pass": "password"}
    response = client.post(
        "/auth/register",
        json=user1
    )
    assert response.status_code == 422
    response = client.post(
        "/auth/register",
        json=user2
    )
    assert response.status_code == 422


def test_create_user_twice(test_db):
    """
    email should not be accepted if the user already exists in the system
    """
    user = {"username": "user@example.com", "password": "password"}
    response = client.post(
        "/auth/register",
        json=user
    )
    assert response.status_code == 200
    response2 = client.post(
        "/auth/register",
        json=user
    )
    assert response2.status_code == 400
    assert response2.json() == {'detail': 'User already exists'}


def test_get_token(test_db):
    user = {"username": "user@example.com", "password": "password"}
    client.post(
        "/auth/register",
        json=user
    )
    response = client.post(
        "/auth/login",
        data=user
    )
    assert response.status_code == 200
    json = response.json()
    assert json['msg'] == 'User user@example.com validated'
    assert json['token']
