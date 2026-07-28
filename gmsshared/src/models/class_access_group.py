from datetime import datetime
from typing import Optional, Self, List

from sqlalchemy import (
    Boolean, DateTime, Column, Integer, JSON, String, ForeignKey, BigInteger, Float, SmallInteger
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from gmsshared import db

class_access_group_plan = db.Table("class_access_group_plan",
                         Column("class_access_group_id", BigInteger, ForeignKey("class_access_group.id"), primary_key=True),
                         Column("plan_id", BigInteger, ForeignKey("plan.id"), primary_key=True))

class_access_group_class = db.Table("class_access_group_class",
                         Column("class_access_group_id", BigInteger, ForeignKey("class_access_group.id"), primary_key=True),
                         Column("class_id", BigInteger, ForeignKey("class.id"), primary_key=True))

class_access_group_format = db.Table("class_access_group_format",
                         Column("class_access_group_id", BigInteger, ForeignKey("class_access_group.id"), primary_key=True),
                         Column("plan_type_id", Integer, ForeignKey("_ref_plan_type.id"), primary_key=True))

class_access_group_door = db.Table("class_access_group_door",
                           Column("class_access_group_id", BigInteger, ForeignKey("class_access_group.id"), primary_key=True),
                           Column("door_id", BigInteger, ForeignKey("door_access_door.id"), primary_key=True))

class ClassAccessGroup(db.Model):
    __tablename__ = "class_access_group"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    location_id = Column(BigInteger, ForeignKey("location.id"), nullable=False)
    name = Column(String(50), nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    create_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(type_=DateTime, nullable=False, server_default=func.now(), onupdate=datetime.utcnow)

    plans = relationship("Plan", secondary=class_access_group_plan, backref="class_access_groups")
    classes = relationship("Class", secondary=class_access_group_class, backref="class_access_groups")
    class_access_group_formats = relationship("_RefPlanType", secondary=class_access_group_format, backref="class_access_groups")
    class_access_group_doors = relationship("DoorAccessDoor", secondary=class_access_group_door, backref="class_access_groups")

    door_access_group_id = Column(String(100), nullable=True)
    door_access_group_status = Column(Integer, nullable=True, server_default='0')
    door_access_access_times_flag = Column(Boolean, nullable=False, server_default='0')
    door_access_access_times = Column(JSON, nullable=True)

    location = relationship("Location")

    def __init__(self, location_id: int, name: str, active: bool):
        self.location_id = location_id
        self.name = name
        self.active = active

    @classmethod
    def find_by_id(cls, location_id: int, id: int):
        return cls.query.filter_by(location_id=location_id, id=id).first()

    @classmethod
    def find_by_location_id(cls, location_id: int):
        return cls.query.filter_by(location_id=location_id).all()

    @classmethod
    def find_door_by_location_and_name(cls, location_id: int, name: str) -> Optional[Self]:
        return cls.query.filter(
            cls.location_id == location_id,
            func.lower(func.trim(cls.name)) == func.lower(func.trim(name)),
        ).first()

    def save(self):
        db.session.add(self)

    def save_and_commit(self):
        self.save()
        db.session.commit()

