# crud/user_crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import User
from app.schemas.user_schema import UserCreate


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).filter(User.username == username.lower()))
    return result.scalars().first()


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).filter(User.email == email.lower()))
    return result.scalars().first()


async def get_user_by_phone_number(db: AsyncSession, phone_number: str) -> User | None:
    result = await db.execute(select(User).filter(User.phone_number == phone_number))
    return result.scalars().first()


async def create_user(db: AsyncSession, user: UserCreate, hashed_password: str):
    db_user = User(
        username=user.username,
        email=user.email,
        phone_number=user.phone_number,
        full_name=user.full_name,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
