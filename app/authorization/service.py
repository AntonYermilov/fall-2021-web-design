import bcrypt
from dependency_injector.wiring import inject, Provide
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from context import Context, Secrets, Service
from app.users import models as user_models
from app.users import db as user_db
from app.users.service import get_user_by_username


token_bearer = OAuth2PasswordBearer(tokenUrl='auth/login')


def hash_password(password: str):
    return bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt()).decode('utf8')


def check_password(password: str, hashed_password: str):
    return bcrypt.checkpw(password.encode('utf8'), hashed_password.encode('utf8'))


@inject
def create_token(username: str, secrets: Secrets = Provide[Context.secrets]):
    token = jwt.encode(
        {'username': username},
        key=secrets.jwt_secret,
        algorithm=secrets.jwt_algo
    )
    return token


@inject
async def current_user(token: str = Depends(token_bearer),
                       service: Service = Depends(Provide[Context.service]),
                       secrets: Secrets = Depends(Provide[Context.secrets])) -> user_db.User:
    auth_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Invalid token'
    )

    try:
        payload = jwt.decode(
            token,
            key=secrets.jwt_secret,
            algorithms=[secrets.jwt_algo]
        )
    except JWTError:
        raise auth_exception

    if 'username' not in payload:
        raise auth_exception

    db_user: user_db.User = get_user_by_username(username=payload['username'], db=next(service.db()))
    if db_user is None:
        raise auth_exception

    return db_user


def register_user(user: user_models.User, db: Session) -> None:
    db_user = user_db.User(
        username=user.username,
        password_hash=hash_password(user.password)
    )
    db.add(db_user)
    try:
        db.commit()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'User "{user.username}" already exists'
        )


def login_user(user: user_models.User, db: Session) -> str:
    db_user: user_db.User = get_user_by_username(username=user.username, db=db)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User {user.username} does not exist'
        )
    if not check_password(password=user.password, hashed_password=db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Invalid password'
        )
    return create_token(username=user.username)
