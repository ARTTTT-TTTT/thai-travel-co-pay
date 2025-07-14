# schemas/user_schema.py
import re
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime

from app.models import UserTypeEnum


class UserBase(BaseModel):
    email: EmailStr = "user.name@example.com"
    phone_number: str = "0812345678"
    citizen_id: str = "1234567890123"
    first_name_th: str = "สมชาย"
    last_name_th: str = "ใจดี"


class UserCreate(UserBase):
    password: str
    agreed_to_terms: bool
    user_type: UserTypeEnum = UserTypeEnum.TOURIST

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        return v.strip().lower() if v else v

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        if not re.fullmatch(r"[0-9]{7,15}", v):
            raise ValueError(
                "Phone number must contain digits only (7-15 characters), no spaces or symbols"
            )
        return v.strip()

    @field_validator("citizen_id")
    @classmethod
    def validate_citizen_id(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        if not re.fullmatch(r"[0-9]{13}", v):
            raise ValueError(
                "Citizen id must contain digits only (13 characters), no spaces or symbols"
            )
        return v.strip()

    @field_validator("first_name_th")
    @classmethod
    def validate_first_name_th(cls, v: str) -> str:
        if not re.fullmatch(r"[ก-๙]{1,50}", v):
            raise ValueError(
                "First name (TH) must contain only Thai characters (no spaces, numbers, or symbols) and be 1-50 characters long."
            )
        return v.strip()

    @field_validator("last_name_th")
    @classmethod
    def validate_last_name_th(cls, v: str) -> str:
        if not re.fullmatch(r"[ก-๙]{1,50}", v):
            raise ValueError(
                "Last name (TH) must contain only Thai characters (no spaces, numbers, or symbols) and be 1-50 characters long."
            )
        return v.strip()


class Pin(BaseModel):
    pin: str

    @field_validator("pin")
    @classmethod
    def validate_phone_number(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        if not re.fullmatch(r"[0-9]{6}", v):
            raise ValueError("Pin must contain digits only (6 characters), no spaces or symbols")
        return v.strip()


class UserOut(UserBase):
    id: int
    user_type: UserTypeEnum
    agreed_to_terms: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
