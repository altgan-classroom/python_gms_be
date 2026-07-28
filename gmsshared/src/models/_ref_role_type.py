from datetime import datetime
from typing import Optional, List, Self

from sqlalchemy import (
    DateTime, Column, Integer, String, ForeignKey, Boolean
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from gmsshared import db
from gmsshared.src.models._ref_permission_type import _RefPermissionType

role_permission = db.Table("role_permission",
                           Column("role_type_id", Integer, ForeignKey("_ref_role_type.id"), primary_key=True),
                           Column("permission_type_id", Integer, ForeignKey("_ref_permission_type.id"),
                                  primary_key=True))


class _RefRoleType(db.Model):
    __tablename__ = "_ref_role_type"
    id = Column(Integer, primary_key=True)
    name = Column(String(20), unique=True, nullable=False)
    description = Column(String(200), nullable=True)
    create_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(type_=DateTime, nullable=False, server_default=func.now(), onupdate=datetime.utcnow)
    is_staff = Column(type_=Boolean, nullable=False)
    access_token_timeout_hrs = Column(type_=Integer, nullable=False, default=6)
    refresh_token_timeout_days = Column(type_=Integer, nullable=False, default=3)
    permissions = relationship("_RefPermissionType", secondary=role_permission, backref="roles")

    def __init__(self, name: str, type: str):
        self.name = name
        self.type = type

    @classmethod
    def find_by_name(cls, name: str) -> Optional[Self]:
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_id(cls, id: int) -> Optional[Self]:
        return cls.query.filter_by(id=id).first()

    @classmethod
    def get_all(cls) -> Optional[List[Self]]:
        return cls.query.filter_by().all()

    def save(self):
        db.session.add(self)

    def save_and_commit(self):
        self.save()
        db.session.commit()
