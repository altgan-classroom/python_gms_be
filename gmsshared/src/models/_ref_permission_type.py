from typing import Optional, Self
from datetime import datetime
from sqlalchemy import (
    DateTime, Column, Integer, String
)
from sqlalchemy.sql import func

from gmsshared import db

class _RefPermissionType(db.Model):
    __tablename__ = "_ref_permission_type"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(50), nullable=False)
    description = Column(String(200), nullable=True)
    create_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(type_=DateTime, nullable=False, server_default=func.now(), onupdate=datetime.utcnow)

    def __init__(self, name: str, display_name: str) -> Self:
        self.name = name
        self.display_name = display_name

    @classmethod
    def find_by_name(cls, name: str) -> Optional[Self]:
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_id(cls, id: int) -> Optional[Self]:
        return cls.query.filter_by(id=id).first()

    @classmethod
    def get_all(cls):
        return cls.query.filter_by().all()

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete(self) -> None:
        db.session.delete(self)
        db.session.commit()
