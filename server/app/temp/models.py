import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    DateTime,
    Date,
    ForeignKey,
    Boolean,
    TEXT,
    DECIMAL,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


# * ====== Enum Definitions ======


class CityTierEnum(str, enum.Enum):
    MAIN = "MAIN"
    SECONDARY = "SECONDARY"


class UserTypeEnum(str, enum.Enum):
    TOURIST = "TOURIST"
    OPERATOR = "OPERATOR"


class GenderEnum(str, enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"


class BusinessTypeEnum(str, enum.Enum):
    HOTEL = "HOTEL"
    RESTAURANT = "RESTAURANT"
    ATTRACTION = "ATTRACTION"
    OTOP = "OTOP"
    SPA = "SPA"
    TRANSPORT = "TRANSPORT"


class BookingStatusEnum(str, enum.Enum):
    BOOKED = "BOOKED"
    PAID = "PAID"
    CHECKED_IN = "CHECKED_IN"
    CHECKED_OUT = "CHECKED_OUT"
    CANCELLED = "CANCELLED"


class CouponStatusEnum(str, enum.Enum):
    ACTIVE = "ACTIVE"
    USED = "USED"
    EXPIRED = "EXPIRED"


class OperatorStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


# * ====== Tables ======


class Province(Base):
    """ตารางเก็บข้อมูลจังหวัดและประเภทเมือง (หลัก/รอง)"""

    __tablename__ = "provinces"

    id = Column(Integer, primary_key=True, index=True)
    name_th = Column(String(100), nullable=False, unique=True)
    name_en = Column(String(100))
    region = Column(String(50), nullable=False)
    city_tier = Column(Enum(CityTierEnum), nullable=False)

    # * Relationships
    tourists_from_here = relationship("Tourist", back_populates="home_province")
    operators_in_province = relationship("Operator", back_populates="province")


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

    # * One-to-One Relationships
    tourist_profile = relationship("Tourist", back_populates="user", uselist=False)
    operator_profile = relationship("Operator", back_populates="user", uselist=False)


class Tourist(Base):
    """ตารางเก็บข้อมูลรายละเอียดของประชาชน"""

    __tablename__ = "tourists"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    citizen_id = Column(String(13), nullable=False, unique=True, index=True)
    laser_code = Column(String(12), nullable=False)

    id_card_photo_url = Column(String(255), nullable=False)

    prefix_th = Column(String(20), nullable=False)
    first_name_th = Column(String(100), nullable=False)
    middle_name_th = Column(String(100))
    last_name_th = Column(String(100), nullable=False)
    prefix_en = Column(String(20))
    first_name_en = Column(String(100))
    middle_name_en = Column(String(100))
    last_name_en = Column(String(100))

    gender = Column(Enum(GenderEnum))
    date_of_birth = Column(Date, nullable=False)

    address_id_card = Column(TEXT, nullable=False)
    address_current = Column(TEXT)

    home_province_id = Column(Integer, ForeignKey("provinces.id"), nullable=False)
    main_city_rights_remaining = Column(Integer, default=3)
    secondary_city_rights_remaining = Column(Integer, default=2)

    # * Relationships
    user = relationship("User", back_populates="tourist_profile")
    home_province = relationship("Province", back_populates="tourists_from_here")
    bookings = relationship("Booking", back_populates="tourist")
    e_coupons = relationship("ECoupon", back_populates="tourist")


class Operator(Base):
    """ตารางเก็บข้อมูลผู้ประกอบการ"""

    __tablename__ = "operators"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    business_name = Column(String(255), nullable=False)
    business_type = Column(Enum(BusinessTypeEnum), nullable=False)
    registration_status = Column(Enum(OperatorStatusEnum), default=OperatorStatusEnum.PENDING)
    address = Column(TEXT, nullable=False)
    province_id = Column(Integer, ForeignKey("provinces.id"), nullable=False)
    approved_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

    # * Relationships
    user = relationship("User", back_populates="operator_profile")
    province = relationship("Province", back_populates="operators_in_province")
    bookings_received = relationship("Booking", back_populates="hotel")
    coupon_transactions_received = relationship(
        "CouponTransaction", back_populates="service_provider"
    )


class Booking(Base):
    """ตารางสำหรับการจองที่พัก"""

    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    tourist_id = Column(Integer, ForeignKey("tourists.id"), nullable=False)
    hotel_operator_id = Column(Integer, ForeignKey("operators.id"), nullable=False)
    check_in_date = Column(Date, nullable=False)
    check_out_date = Column(Date, nullable=False)
    num_nights = Column(Integer, nullable=False)
    total_cost = Column(DECIMAL(10, 2), nullable=False)
    subsidy_rate = Column(DECIMAL(4, 2), nullable=False)
    government_subsidy = Column(DECIMAL(10, 2), nullable=False)
    tourist_payment = Column(DECIMAL(10, 2), nullable=False)
    booking_status = Column(Enum(BookingStatusEnum), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # * Relationships
    tourist = relationship("Tourist", back_populates="bookings")
    hotel = relationship("Operator", back_populates="bookings_received")
    e_coupons = relationship("ECoupon", back_populates="booking")


class ECoupon(Base):
    """ตารางสำหรับ E-Coupon ที่ได้รับจากการเช็คอิน"""

    __tablename__ = "e_coupons"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    tourist_id = Column(Integer, ForeignKey("tourists.id"), nullable=False)
    coupon_code = Column(String(20), nullable=False, unique=True)
    amount = Column(DECIMAL(10, 2), nullable=False, default=500.00)
    issue_date = Column(Date, nullable=False)
    expiry_datetime = Column(DateTime, nullable=False)
    status = Column(Enum(CouponStatusEnum), default=CouponStatusEnum.ACTIVE)

    # * Relationships
    booking = relationship("Booking", back_populates="e_coupons")
    tourist = relationship("Tourist", back_populates="e_coupons")
    transactions = relationship("CouponTransaction", back_populates="coupon")


class CouponTransaction(Base):
    """ตารางเก็บประวัติการใช้ E-Coupon"""

    __tablename__ = "coupon_transactions"

    id = Column(Integer, primary_key=True, index=True)
    coupon_id = Column(Integer, ForeignKey("e_coupons.id"), nullable=False)
    service_operator_id = Column(Integer, ForeignKey("operators.id"), nullable=False)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    discount_applied = Column(DECIMAL(10, 2), nullable=False)
    transaction_time = Column(DateTime, server_default=func.now())

    # * Relationships
    coupon = relationship("ECoupon", back_populates="transactions")
    service_provider = relationship("Operator", back_populates="coupon_transactions_received")


class ProjectConfig(Base):
    """ตารางสำหรับเก็บค่าตั้งค่ากลางของโครงการ"""

    __tablename__ = "project_config"

    config_key = Column(String(100), primary_key=True)
    config_value = Column(String(255), nullable=False)
    description = Column(TEXT)
