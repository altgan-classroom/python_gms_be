import time
from datetime import datetime, timezone
from typing import Optional, Self
from sqlalchemy import (
    DateTime, Column, Float, Integer, String, BigInteger, JSON, insert, update
)
from sqlalchemy.sql import func

from gmsshared import db

class DoorAccessLog(db.Model):
    id = Column(BigInteger, primary_key=True)
    location_id = Column(BigInteger, nullable=True)
    user_id = Column(BigInteger, nullable=True)
    resource = Column(Integer, nullable=False)
    resource_id = Column(String(50), nullable=True)
    request_type = Column(Integer, nullable=False)
    request_url = Column(String(250), nullable=False)
    request_payload = Column(JSON, nullable=True)
    response_payload = Column(JSON, nullable=True)
    response_status_code = Column(Integer, nullable=True)
    error = Column(String(1000), nullable=True)
    request_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    response_elapsed_sec = Column(Float, nullable=True)

    @classmethod
    def find_by_id(cls, _id: int) -> Optional[Self]:
        return cls.query.filter_by(id=_id).first()

    def save(self):
        db.session.add(self)

    def save_and_commit(self):
        self.save()
        db.session.commit()

    @classmethod
    def insert(cls, location_id, user_id, resource, resource_id, request_type, url, request_payload,
               response_payload=None, response_status_code=None, error=None, response_elapsed_sec=None):
        params = {}
        params.update({"location_id": location_id, "user_id": user_id, "resource": resource, "resource_id": resource_id,
                       "request_type": request_type, "request_url": url, "request_payload": request_payload,
                       "response_elapsed_sec": response_elapsed_sec, "error": error,
                       "response_payload": response_payload, "response_status_code": response_status_code})
        insert_stmt = (insert(cls))
        result = db.session.execute(insert_stmt, params)
        db.session.commit()
        return result
