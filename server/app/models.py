import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    DateTime,
    Boolean,
    TEXT,
    DECIMAL,
    Date,
    ForeignKey,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.base import Base


# * ====== Enum Definitions ======


class CityTierEnum(str, enum.Enum):
    MAIN = "MAIN"
    SECONDARY = "SECONDARY"


class UserTypeEnum(str, enum.Enum):
    TOURIST = "TOURIST"
    OPERATOR = "OPERATOR"


# * ====== Tables ======


class UserTravel(Base):
    """ตารางเก็บข้อมูลแผนการเดินทางของผู้ใช้"""

    __tablename__ = "user_travels"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    province_id = Column(Integer, ForeignKey("provinces.id"), nullable=False)

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    notes = Column(TEXT, default="")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # * Relationships
    user = relationship("User", back_populates="travels")
    province = relationship("Province", back_populates="travels")


class Province(Base):
    """ตารางเก็บข้อมูลจังหวัดและประเภทเมือง (หลัก/รอง)"""

    __tablename__ = "provinces"

    id = Column(Integer, primary_key=True, index=True)
    name_th = Column(String(100), nullable=False, unique=True)
    name_en = Column(String(100))
    region = Column(String(50), nullable=False)
    city_tier = Column(Enum(CityTierEnum), nullable=False)

    tax_reduction_rate = Column(DECIMAL(4, 2), default=0.00)
    tax_description = Column(TEXT, default="")

    # * Relationships
    travels = relationship("UserTravel", back_populates="province")


class User(Base):
    """ตารางสำหรับเก็บข้อมูลบัญชีผู้ใช้ร่วมกัน"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone_number = Column(String(15), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    pin_hash = Column(String(255))

    citizen_id = Column(String(13), nullable=False, unique=True, index=True)
    first_name_th = Column(String(100), nullable=False)
    last_name_th = Column(String(100), nullable=False)

    user_type = Column(Enum(UserTypeEnum), nullable=False)
    agreed_to_terms = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # * Relationships
    travels = relationship("UserTravel", back_populates="user")
