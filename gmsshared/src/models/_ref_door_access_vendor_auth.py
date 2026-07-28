from datetime import datetime
from typing import List, Optional, Self

from sqlalchemy import (
    DateTime, Column, Integer, Boolean, ForeignKey, Float, BigInteger, JSON, String, text, Date, func
)
from sqlalchemy.orm import relationship

from gmsshared import db
from gmsshared.src.models._ref_door_access_vendor import _RefDoorAccessVendor

class _RefDoorAccessVendorAuth(db.Model):
    __tablename__ = "_ref_door_access_vendor_auth"
    id = Column(Integer, nullable=False, primary_key=True)
    vendor_id = Column(Integer, ForeignKey("_ref_door_access_vendor.id"), nullable=False)
    display_name = Column(String(100), nullable=False)
    field_name = Column(String(50), nullable=False)
    field_type = Column(String(50), nullable=False)
    field_validation_rules_json = Column(JSON, nullable=True)
    field_help_text = Column(String(200), nullable=True)

    create_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(type_=DateTime, nullable=False, server_default=func.now(), onupdate=datetime.utcnow)

    @classmethod
    def find_by_vendor_id(cls, vendor_id) -> Optional[List[Self]]:
        return cls.query.filter_by(vendor_id=vendor_id).all()

    def save(self):
        db.session.add(self)

    def save_and_commit(self):
        self.save()
        db.session.commit()
