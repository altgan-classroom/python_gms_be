from datetime import datetime
from typing import List, Optional, Self

from sqlalchemy import (
    DateTime, Column, Integer, Boolean, ForeignKey, Float, BigInteger, String, text, Date, func
)
from sqlalchemy.orm import relationship

from gmsshared import db

class _RefDoorAccessVendor(db.Model):
    __tablename__ = "_ref_door_access_vendor"
    id = Column(Integer, nullable=False, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(200), nullable=True)
    authentication_type = Column(String(50), nullable=False)
    api_url = Column(String(200), nullable=False)

    create_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(type_=DateTime, nullable=False, server_default=func.now(), onupdate=datetime.utcnow)

    door_access_vendor_auth = relationship("_RefDoorAccessVendorAuth", backref="door_access_vendor")

    @classmethod
    def get_all(cls) -> Optional[List[Self]]:
        return cls.query.filter_by().all()

    def save(self):
        db.session.add(self)

    def save_and_commit(self):
        self.save()
        db.session.commit()
