from fastapi import HTTPException, status


def user_exception():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Credentials could not be validated',
        headers={'WWW-Authenticate': 'bearer'}
    )


def token_exception():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Incorrect username or password',
        headers={'WWW-Authenticate': 'bearer'}
    )


def user_exists():
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="User already exists"
    )


def player_does_not_exist():
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="player does not exist"
    )


def player_unavailable():
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="player with the given id does not belong to user"
    )


def invalid_price():
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="price requested for player not allowed"
    )


def player_already_yours():
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="player with the given already belongs to user"
    )


def player_not_on_sale():
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="player not on market list"
    )


def insufficient_funds():
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="user does not have enough money to buy player"
    )


