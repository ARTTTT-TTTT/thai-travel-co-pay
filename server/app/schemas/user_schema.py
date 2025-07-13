# schemas/user_schema.py
import re
from pydantic import BaseModel, EmailStr, model_validator, field_validator
from typing import Optional
from datetime import datetime

from app.models import UserTypeEnum


class UserBase(BaseModel):
    email: EmailStr
    phone_number: str
    citizen_id: str
    first_name_th: str
    last_name_th: str
    user_type: UserTypeEnum = UserTypeEnum.TOURIST


class UserCreate(UserBase):
    password: str
    
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

    @model_validator(mode="after")
    def check_email_or_phone_number(self) -> "UserCreate":
        if not self.email or not self.phone_number:
            raise ValueError("Both email and phone number must be provided.")
        return self


class UserOut(UserBase):
    id: int
    agreed_to_terms: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
