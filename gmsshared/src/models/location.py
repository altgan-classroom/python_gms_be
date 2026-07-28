from datetime import datetime
from typing import Optional, Self, List

from sqlalchemy import (
    Boolean, DateTime, Column, Integer, String, ForeignKey, BigInteger, Float, SmallInteger
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from gmsshared import db
from gmsshared.src.models._ref_gym_type import _RefGymType
from gmsshared.src.models._ref_timezone_type import _RefTimezoneType
from gmsshared.src.models.gym import Gym
from gmsshared.src.models._ref_location_type import _RefLocationType
from gmsshared.src.models._ref_door_access_vendor import _RefDoorAccessVendor
from gmsshared.src.models.door_access_location_auth import DoorAccessLocationAuth
from gmsshared.src.util.enums import LocationTypeEnum
from gmsshared.src.models.user import User

location_gym_type = db.Table("location_gym_type",
                         Column("location_id", BigInteger, ForeignKey("location.id"), primary_key=True),
                         Column("gym_type_id", Integer, ForeignKey("_ref_gym_type.id"), primary_key=True))


class Location(db.Model):
    id = Column(BigInteger, primary_key=True)
    name = Column(String(50), nullable=False)
    address_1 = Column(String(50), nullable=True)
    address_2 = Column(String(50), nullable=True)
    city = Column(String(50), nullable=True)
    state = Column(String(50), nullable=True)
    zip = Column(String(10), nullable=True)
    country = Column(String(50), nullable=True)
    area_sft = Column(Integer, nullable=True)
    active = Column(Boolean(), nullable=True, default=True)
    primary = Column(Boolean(), nullable=True, default=False)
    cs_phone = Column(String(20), nullable=True)
    cs_email = Column(String(100), nullable=True)
    sales_tax = Column(Float, nullable=True)
    payrix_merchant_id = Column(String(50), nullable=True)
    payrix_entity_id = Column(String(50), nullable=True)
    payrix_onboarding_status = Column(Integer, nullable=True, server_default='1')
    revenue_share_enabled = Column(Boolean(), nullable=False, default=False)
    revenue_share_model_id = Column(SmallInteger, nullable=True, server_default='1')
    payrix_group_id = Column(String(50), nullable=True)


    kiosk_enabled = Column(Boolean(), nullable=True, default=False)
    checkin_type = Column(Integer, nullable=True)
    accent_color = Column(String(10), nullable=True, default="#000000")
    kiosk_user_id = Column(BigInteger, ForeignKey('user.id'), nullable=True, default=None)
    kiosk_user = relationship("User", backref="kiosk_location")
    logo_url = Column(String(200), nullable=True)

    create_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(type_=DateTime, nullable=False, server_default=func.now(), onupdate=datetime.utcnow)

    # A Location will have a session registration start time type
    registration_start_time_type_id = Column(Integer, ForeignKey("_ref_registration_times_type.id"), nullable=True)
    registration_start_time_value = Column(Integer, nullable=True)

    # A Location will have a session registration end time type
    registration_end_time_type_id = Column(Integer, ForeignKey("_ref_registration_times_type.id"), nullable=True)
    registration_end_time_value = Column(Integer, nullable=True)

    # A Location will have a late cancellation time type
    late_cancellation_time_type_id = Column(Integer, ForeignKey("_ref_registration_times_type.id"), nullable=True)
    late_cancellation_time_value = Column(Integer, nullable=True)
    late_cancellation = Column(Boolean, nullable=True, default=False)

    waitlist = Column(Boolean(), nullable=True, default=False)

    no_show_time_penalty = Column(Integer, nullable=True)
    no_show_credit = Column(Boolean, nullable=True, default=True)
    no_show_enabled_datetime = Column(DateTime, nullable=True)

    payments = Column(Boolean, default=True)
    class_access_group = Column(Boolean, default=False)

    # A location can be of one Type
    gym_types = relationship("_RefGymType", secondary=location_gym_type, backref="locations")
    other_gym_type = Column(String(50), nullable=True)

    # A location can belong to one Gym
    gym_id = Column(BigInteger, ForeignKey('gym.id'), nullable=False)
    gym = relationship("Gym", backref="locations")

    timezone_type_id = Column(Integer, ForeignKey("_ref_timezone_type.id"), nullable=True, server_default='1')
    timezone = relationship("_RefTimezoneType")
    location_type_id = Column(Integer, ForeignKey("_ref_location_type.id"), nullable=False, default=LocationTypeEnum.PHYSICAL.value)

    is_dea = Column(Boolean(), nullable=False, default=False)
    block_registrations_on_balance_due = Column(Boolean(), nullable=False, default=False)

    door_access = Column(Boolean(), nullable=False, default=False)
    door_access_vendor_id = Column(Integer, ForeignKey("_ref_door_access_vendor.id"), nullable=True)
    door_access_auth_status = Column(Integer, nullable=False, default=0)
    door_access_auth_error = Column(String(100), nullable=True)
    door_access_place_id = Column(BigInteger, nullable=True)
    door_access_unlock_doors = Column(Boolean(), nullable=False, default=False)
    door_access_vendor = relationship("_RefDoorAccessVendor")
    door_access_location_auth = relationship("DoorAccessLocationAuth")

    def __init__(self, name: str, gym_id: int):
        self.name = name
        self.gym_id = gym_id

    @classmethod
    def find_by_gym(cls, gym_id: int) -> Optional[Self]:
        return cls.query.filter_by(gym_id=gym_id).all()

    @classmethod
    def find_by_id(cls, id: int) -> Optional[Self]:
        return cls.query.filter_by(id=id).first()

    @classmethod
    def find_by_revenue_share_enabled(cls) -> Optional[List[Self]]:
        return cls.query.filter(Location.revenue_share_enabled==True, Location.payrix_merchant_id.isnot(None)).all()

    def save(self):
        db.session.add(self)

    def save_and_commit(self):
        self.save()
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
