import time
from datetime import datetime, timezone
from typing import Optional, Self, List
from sqlalchemy import (
    DateTime, Column, Integer, String, BigInteger, JSON, insert, update, ForeignKey,Boolean
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from gmsshared.src.models.location import Location

from gmsshared import db
from gmsshared.src.util.enums import DoorAccessStatusEnum


class DoorAccessDoor(db.Model):
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    location_id = Column(BigInteger, ForeignKey("location.id"), nullable=False)
    name = Column(String(30), nullable=False)
    door_location = Column(String(50), nullable=True)
    active = Column(Boolean, nullable=False, default=True)
    door_access_door_status = Column(Integer, nullable=False, default=1)
    create_datetime = Column(DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    vendor_door_id = Column(BigInteger, nullable=True)

    location = db.relationship(Location, backref="doors")

    def __init__(self, location_id, name: str, door_location: str):
        self.location_id = location_id
        self.name = name
        self.door_location = door_location
        self.door_access_door_status = DoorAccessStatusEnum.PENDING.value

    @classmethod
    def find_by_id(cls, location_id, _id: int) -> Optional[Self]:
        return cls.query.filter_by(location_id=location_id, id=_id).first()

    @classmethod
    def find_by_location_id(cls, location_id: int) -> Optional[List[Self]]:
        return cls.query.filter_by(location_id=location_id).all()

    @classmethod
    def find_door_by_location_and_name(cls, location_id: int, door_name: str) -> Optional[Self]:
        return cls.query.filter(
            cls.location_id == location_id,
            func.lower(func.trim(cls.name)) == func.lower(func.trim(door_name)),
        ).first()

    def save(self):
        db.session.add(self)

    def save_and_commit(self):
        self.save()
        db.session.commit()
