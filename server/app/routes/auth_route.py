# routes/auth_route.py
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
    existing_user_by_email = await crud.get_user_by_email(db, user_create.email)
    if existing_user_by_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    existing_user_by_phone = await crud.get_user_by_phone_number(db, user_create.phone_number)
    if existing_user_by_phone:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Phone number already registered",
        )

    existing_user_by_citizen_id = await crud.get_user_by_citizen_id(db, user_create.citizen_id)
    if existing_user_by_citizen_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Citizen id already registered"
        )

    password_hash = get_password_hash(user_create.password)
    user = await crud.create_user(db, user_create, password_hash)
    return user


@router.post("/login")
async def login(
    # * username = Email/ หมายเลขโทรศัพท์ / รหัสบัตรประชาชน
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user: User | None = None
    input_identifier = form_data.username.strip().lower()

    # * 1. Email
    if re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", input_identifier):
        user = await crud.get_user_by_email(db, input_identifier)

    # * 2. Citizen Id
    elif input_identifier.isdigit() and len(input_identifier) == 13:
        user = await crud.get_user_by_citizen_id(db, input_identifier)

    # * 3. Phone Number
    elif input_identifier.isdigit():
        user = await crud.get_user_by_phone_number(db, input_identifier)

    if not user or not verify_password(form_data.password, str(user.password_hash)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email, phone number, citizen id or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token}
