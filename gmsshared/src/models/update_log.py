from datetime import datetime
from typing import Optional, Self

from sqlalchemy import (DateTime, Column, Integer, String, ForeignKey, BigInteger, Text, JSON, DateTime)
from sqlalchemy.sql import func
from gmsshared import db
from gmsshared.src.models.location import Location
from sqlalchemy.orm import relationship

class UpdateLog(db.Model):
    __tablename__ = 'update_log'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    location_id = Column(BigInteger, nullable=True)
    target_user_id = Column(BigInteger, nullable=True)
    actor_user_id = Column(BigInteger, nullable=True)
    method = Column(String(255), nullable=True)
    request_body = Column(JSON, nullable=True)
    response = Column(JSON, nullable=True)
    create_datetime = Column(DateTime, nullable=False, server_default=func.now())
    request_url = Column(String(255), nullable=True)

    def save(self):
        db.session.add(self)

    def save_and_commit(self):
        self.save()
        db.session.commit()
