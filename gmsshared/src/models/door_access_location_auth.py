from datetime import datetime
from typing import List, Optional, Self

from sqlalchemy import (
    DateTime, Column, Integer, Boolean, ForeignKey, Float, BigInteger, String, text, Date, func
)
from sqlalchemy.orm import relationship

from gmsshared import db
from gmsshared.src.models._ref_door_access_vendor_auth import _RefDoorAccessVendorAuth

class DoorAccessLocationAuth(db.Model):
    id = Column(Integer, nullable=False, primary_key=True)
    location_id = Column(BigInteger, ForeignKey('location.id'), nullable=False)
    field_id = Column(BigInteger, ForeignKey('_ref_door_access_vendor_auth.id'), nullable=False)
    field_value = Column(String(100), nullable=True)

    create_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(type_=DateTime, nullable=False, server_default=func.now(), onupdate=datetime.utcnow)

    door_access_vendor_auth = relationship("_RefDoorAccessVendorAuth")

    @classmethod
    def find_by_location(cls, location_id: int) -> Optional[List[Self]]:
        return cls.query.filter_by(location_id=location_id).all()

    @classmethod
    def delete_by_location_id(cls, location_id) -> Optional[Self]:
        sql = (f"delete from door_access_location_auth where location_id = {location_id}")
        db.session.execute(text(sql))

    def save(self):
        db.session.add(self)

    def save_and_commit(self):
        self.save()
        db.session.commit()
