from datetime import datetime
from sqlalchemy import (
    DateTime, Column, Integer, String, BigInteger, JSON, insert, update
)
from sqlalchemy.sql import func

from gmsshared import db

class DoorAccessUpdatesLog(db.Model):
    id = Column(BigInteger, primary_key=True)
    vendor_id = Column(Integer, nullable=False)
    vendor_location_id = Column(String(50), nullable=False)
    actor_id = Column(String(50), nullable=True)
    event_id = Column(String(50), nullable=True)
    event_type = Column(Integer, nullable=True)
    error_code = Column(String(15), nullable=True)
    event_payload = Column(JSON, nullable=True)

    create_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(type_=DateTime, nullable=False, server_default=func.now(), onupdate=datetime.utcnow)

    def save(self):
        db.session.add(self)

    def save_and_commit(self):
        self.save()
        db.session.commit()
