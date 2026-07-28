import time
from datetime import datetime, timezone
from typing import Optional, Self
from sqlalchemy import (
    DateTime, Column, Integer, String, BigInteger, JSON, insert, update
)
from sqlalchemy.sql import func

from gmsshared import db


class PayrixLog(db.Model):
    id = Column(BigInteger, primary_key=True)
    resource = Column(Integer, nullable=False)
    location_id = Column(BigInteger, nullable=True)
    user_id = Column(BigInteger, nullable=True)
    payment_id = Column(BigInteger, nullable=True)
    payment_method_id = Column(BigInteger, nullable=True)
    resource_id = Column(String(50), nullable=True)
    request_type = Column(String(10), nullable=True)
    request_url = Column(String(250), nullable=False)
    request_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    request_payload = Column(JSON, nullable=True)
    response_payload = Column(JSON, nullable=True)
    response_datetime = Column(type_=DateTime, nullable=False, server_default=func.now(), onupdate=datetime.utcnow)
    response_status_code = Column(Integer, nullable=True)
    error = Column(String(1000), nullable=True)

    @classmethod
    def find_by_id(cls, _id: int) -> Optional[Self]:
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def insert(cls, location_id, user_id, payment_id, payment_method_id, resource, resource_id, request_type,
               url, request_payload, response_payload, response_status_code, error):
        params = {}
        if not payment_method_id is None:
            params['payment_method_id'] = payment_method_id
        if not response_payload is None:
            params['response_payload'] = response_payload
        if not payment_id is None:
            params['payment_id'] = payment_id
        if not error is None:
            params['error'] = error
        if not response_status_code is None:
            params['response_status_code'] = response_status_code
        params.update({"location_id": location_id, "user_id": user_id, "resource": resource, "resource_id": resource_id,
                       "request_type": request_type, "request_url": url, "request_payload": request_payload})
        insert_stmt = (insert(cls))
        result = db.session.execute(insert_stmt, params)
        db.session.commit()
        return result

    def __init__(self, first_name: str, last_name: str):
        self.first_name = first_name
        self.last_name = last_name

    def save(self):
        db.session.add(self)

    def save_and_commit(self):
        self.save()
        db.session.commit()
