from fastapi import APIRouter, Depends

from app.models import User
from app.schemas.user_schema import UserOut
from app.security import (
    get_current_user_with_access_token,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserOut)
async def read_me(current_user: User = Depends(get_current_user_with_access_token)):
    return current_user
