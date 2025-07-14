# crud/user_crud.py
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import User
from app.schemas.user_schema import UserCreate


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).filter(User.email == email.lower()))
    return result.scalars().first()


async def get_user_by_phone_number(db: AsyncSession, phone_number: str) -> User | None:
    result = await db.execute(select(User).filter(User.phone_number == phone_number))
    return result.scalars().first()


async def get_user_by_citizen_id(db: AsyncSession, citizen_id: str) -> User | None:
    result = await db.execute(select(User).filter(User.citizen_id == citizen_id))
    return result.scalars().first()


async def create_user(db: AsyncSession, user: UserCreate, password_hash: str):
    db_user = User(
        email=user.email,
        phone_number=user.phone_number,
        citizen_id=user.citizen_id,
        password_hash=password_hash,
        first_name_th=user.first_name_th,
        last_name_th=user.last_name_th,
        user_type=user.user_type,
        agreed_to_terms=user.agreed_to_terms,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def pin_setup(db: AsyncSession, id: int, pin_hash: str):
    result = await db.execute(select(User).where(User.id == id))
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    setattr(db_user, "pin_hash", pin_hash)

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
