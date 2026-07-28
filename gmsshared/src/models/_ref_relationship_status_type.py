from typing import Optional, Any, List, Self
from datetime import datetime
from sqlalchemy import (
    DateTime, Column, String, BigInteger, Integer, )
from sqlalchemy.sql import func

from gmsshared import db

class _RefRelationshipStatusType(db.Model):
    __tablename__ = "_ref_relationship_status_type"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=False, nullable=False)
    create_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(type_=DateTime, nullable=False, server_default=func.now(), onupdate=datetime.utcnow)

    def __init__(self, name: str):
        self.name = name

    @classmethod
    def find_by_name(cls, name: str) -> Optional[Any]:
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_id(cls, id: int) -> Optional[Any]:
        return cls.query.filter_by(id=id).first()

    @classmethod
    def get_all(cls) -> Optional[List[Self]]:
        return cls.query.filter_by().all()

    def save(self):
        db.session.add(self)

    def save_and_commit(self):
        self.save()
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
