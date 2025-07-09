from sqlalchemy import Column, String, Integer, Boolean, DateTime
from datetime import datetime

from app.database.base import Base

# * ====== User ======


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    email = Column(String, unique=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    full_name = Column(String)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
