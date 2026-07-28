import time
from datetime import datetime, timezone
from typing import Optional, Self
from sqlalchemy import (
    DateTime, Column, Integer, String, BigInteger, JSON, insert, update
)
from sqlalchemy.sql import func

from gmsshared import db


class PayrixUpdatesLog(db.Model):
    id = Column(BigInteger, primary_key=True)
    payrix_resource = Column(Integer, nullable=False)
    payrix_request_payload = Column(JSON, nullable=True)
    payrix_transaction_id = Column(String(50), nullable=True)
    payrix_transaction_status = Column(Integer, nullable=True)

    create_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(type_=DateTime, nullable=False, server_default=func.now(), onupdate=datetime.utcnow)

    @classmethod
    def find_by_id(cls, _id: int) -> Optional[Self]:
        return cls.query.filter_by(id=_id).first()

    def save(self):
        db.session.add(self)

    def save_and_commit(self):
        self.save()
        db.session.commit()
