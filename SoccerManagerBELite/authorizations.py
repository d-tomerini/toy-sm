from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
import exceptions

SECRET_KEY = 'testing'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(
    schemes=['bcrypt'],
    deprecated='auto'
)


def get_password_hash(password):
    return bcrypt_context.hash(password)


def verify_password(password, hashed_password):
    return bcrypt_context.verify(password, hashed_password)


oauth2_bearer = OAuth2PasswordBearer(tokenUrl='token')


async def get_username_from_token(token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise exceptions.token_exception()
    except JWTError:
        raise exceptions.token_exception()
    return username
