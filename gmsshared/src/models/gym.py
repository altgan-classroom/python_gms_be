from datetime import datetime
from typing import Optional, Any

from sqlalchemy import (
    DateTime, Column, String, BigInteger, Integer, ForeignKey, Boolean)
from sqlalchemy.sql import func

from gmsshared import db
from gmsshared.src.models._ref_location_type import _RefLocationType
from gmsshared.src.models._ref_timezone_type import _RefTimezoneType
from gmsshared.src.util.enums import LocationTypeEnum, SessionClassEnum
from gmsshared.src.models._ref_registration_times_type import _RefRegistrationTimesType


class Gym(db.Model):
    id = Column(BigInteger, primary_key=True)
    name = Column(String(50), unique=False, nullable=False)
    logo_url = Column(String(255), nullable=True)
    company_name = Column(String(50), nullable=True)
    company_website = Column(String(255), nullable=True)
    location_type_id = Column(Integer, ForeignKey("_ref_location_type.id"), nullable=False,
                              server_default=str(LocationTypeEnum.PHYSICAL.value))
    timezone_type_id = Column(Integer, ForeignKey("_ref_timezone_type.id"), nullable=False, server_default='1')
    session_or_class = Column(Integer, nullable=False, server_default=str(SessionClassEnum.SESSION.value))
    registration_start_time_type_id = Column(Integer, ForeignKey("_ref_registration_times_type.id"), nullable=False,
                                             server_default='1')
    registration_start_time_value = Column(Integer, nullable=True)
    registration_end_time_type_id = Column(Integer, ForeignKey("_ref_registration_times_type.id"), nullable=False,
                                           server_default='1')
    registration_end_value = Column(Integer, nullable=True)
    late_cancellation_enforcement = Column(Boolean(), nullable=False, server_default='1')
    late_cancellation_time_type_id = Column(Integer, ForeignKey("_ref_registration_times_type.id"), nullable=False,
                                            server_default='1')
    cancellation_penalty = Column(Integer, nullable=True)
    no_show_penalties = Column(Boolean(), nullable=False, server_default='0')
    no_show_time_penalty = Column(Integer, nullable=True)
    waitlist_availability = Column(Boolean(), nullable=False, server_default='1')

    create_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(type_=DateTime, nullable=False, server_default=func.now(), onupdate=datetime.utcnow)

    def __init__(self, name: str):
        self.name = name

    @classmethod
    def find_by_name(cls, name: str) -> Optional[Any]:
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_id(cls, id: int) -> Optional[Any]:
        return cls.query.filter_by(id=id).first()

    def save(self):
        db.session.add(self)

    def save_and_commit(self):
        self.save()
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
