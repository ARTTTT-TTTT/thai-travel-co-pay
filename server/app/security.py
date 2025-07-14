# security.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

from app.database.session import get_db
from app.models import User
from app.configs.app_config import app_config


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


refresh_token_scheme = OAuth2PasswordBearer(tokenUrl="/auth/refresh")
access_token_scheme = OAuth2PasswordBearer(tokenUrl="/auth/access")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_pin_hash(pin: str) -> str:
    return pwd_context.hash(pin)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def verify_pin(plain_pin: str, pin_hash: str) -> bool:
    return pwd_context.verify(plain_pin, pin_hash)


def create_refresh_token(
    data: dict, expires_delta: timedelta = timedelta(days=app_config.REFRESH_TOKEN_EXPIRE)
) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, app_config.REFRESH_SECRET_KEY, algorithm=app_config.ALGORITHM)


def create_access_token(
    data: dict,
    expires_delta: timedelta = timedelta(minutes=app_config.ACCESS_TOKEN_EXPIRE),
) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, app_config.ACCESS_SECRET_KEY, algorithm=app_config.ALGORITHM)


async def get_current_user_with_refresh_token(
    refresh_token: str = Depends(refresh_token_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            refresh_token,
            app_config.REFRESH_SECRET_KEY,
            algorithms=[app_config.ALGORITHM],
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        int(user_id)
    except (JWTError, ValueError):
        raise credentials_exception

    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()

    if user is None:
        raise credentials_exception
    return user


async def get_current_user_with_access_token(
    access_token: str = Depends(access_token_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            access_token, app_config.ACCESS_SECRET_KEY, algorithms=[app_config.ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        int(user_id)
    except (JWTError, ValueError):
        raise credentials_exception

    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()

    if user is None:
        raise credentials_exception
    return user
