import time
from datetime import datetime, timezone
from typing import Optional, Self
from sqlalchemy import (
    DateTime, Column, Integer, String, BigInteger, JSON, insert, update
)
from sqlalchemy.sql import func

from gmsshared import db

class BatchProcessingLog(db.Model):
    id = Column(BigInteger, primary_key=True)
    location_id = Column(BigInteger, nullable=True)
    user_id = Column(BigInteger, nullable=True)
    membership_id = Column(BigInteger, nullable=True)
    process_name = Column(String(50), nullable=False)
    message = Column(String(200), nullable=True)
    data = Column(JSON, nullable=True)
    error = Column(String(500), nullable=True)
    create_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(type_=DateTime, nullable=False, server_default=func.now(), onupdate=datetime.utcnow)

    @classmethod
    def find_by_id(cls, _id: int) -> Optional[Self]:
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def insert(cls, process_name, message, location_id=None, user_id=None, membership_id=None, data=None, error=None):
        params = {}
        if not location_id is None:
            params['location_id'] = location_id
        if not user_id is None:
            params['user_id'] = user_id
        if not membership_id is None:
            params['membership_id'] = membership_id
        if not message is None:
            params['message'] = message
        if not data is None:
            params['data'] = data
        if not error is None:
            params['error'] = error
        params.update({"process_name": process_name})
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
