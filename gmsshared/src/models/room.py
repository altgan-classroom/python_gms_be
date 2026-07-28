from datetime import datetime
from typing import Optional, Self

from sqlalchemy import (
    DateTime, Column, Integer, String, ForeignKey, BigInteger, Text
)
from sqlalchemy.sql import func

from gmsshared import db
from gmsshared.src.models.location import Location


class Room(db.Model):
    id = Column(BigInteger, primary_key=True)
    name = Column(String(100), nullable=False)
    sft = Column(Integer, nullable=True)
    capacity = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    location_id = Column(BigInteger, ForeignKey('location.id'), nullable=False)
    create_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(type_=DateTime, nullable=False, server_default=func.now(), onupdate=datetime.utcnow)

    def __init__(self, name: str, location_id: int):
        self.name = name
        self.location_id = location_id

    @classmethod
    def find_by_id(cls, _id: int) -> Optional[Self]:
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_location(cls, location_id: int) -> Optional[Self]:
        return cls.query.filter_by(location_id=location_id).all()

    @classmethod
    def find_by_location_and_room(cls, room_id: int, location_id: int) -> Optional[Self]:
        return cls.query.filter(cls.id == room_id, cls.location_id == location_id).first()

    def save(self):
        db.session.add(self)

    def save_and_commit(self):
        self.save()
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
