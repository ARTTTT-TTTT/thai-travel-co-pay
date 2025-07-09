import re
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.schemas.user_schema import UserCreate, UserOut
from app.crud import user_crud as crud
from app.database.session import get_db
from app.security import (
    get_password_hash,
    verify_password,
    create_access_token,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserOut)
async def register(user_create: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user_by_username = await crud.get_user_by_username(db, user_create.username)
    if existing_user_by_username:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")

    if user_create.email:
        existing_user_by_email = await crud.get_user_by_email(db, user_create.email)
        if existing_user_by_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
            )

    if user_create.phone_number:
        existing_user_by_phone = await crud.get_user_by_phone_number(db, user_create.phone_number)
        if existing_user_by_phone:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Phone number already registered"
            )

    hashed_password = get_password_hash(user_create.password)
    user = await crud.create_user(db, user_create, hashed_password)
    return user


@router.post("/login")
async def login(
    # * username = หมายเลขโทรศัพท์ / Email / ชื่อผู้ใช้
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user: User | None = None
    input_identifier = form_data.username.strip().lower()

    # * 1. Email
    if re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", input_identifier):
        user = await crud.get_user_by_email(db, input_identifier)

    # * 2. Phone Number
    elif input_identifier.isdigit():
        user = await crud.get_user_by_phone_number(db, input_identifier)

    # * 3. Username
    else:
        user = await crud.get_user_by_username(db, input_identifier)

    if not user or not verify_password(form_data.password, str(user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username, email, phone number, or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token}
