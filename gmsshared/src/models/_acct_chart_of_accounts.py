from typing import Optional, List, Self
from datetime import datetime
from sqlalchemy import (
    DateTime, Column, Integer, String, BigInteger, Float, Boolean
)
from sqlalchemy.sql import func

from gmsshared import db

class _AcctChartOfAccounts(db.Model):
    __tablename__ = "_acct_chart_of_accounts"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    type = Column(String(50), nullable=False)
    create_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(type_=DateTime, nullable=False, server_default=func.now(), onupdate=datetime.utcnow)

    def __init__(self, name: str):
        self.name = name

    @classmethod
    def find_by_name(cls, description: str) -> Optional[Self]:
        return cls.query.filter_by(desciption=description).first()

    @classmethod
    def find_by_id(cls, id: int) -> Optional[Self]:
        return cls.query.filter_by(id=id).first()

    @classmethod
    def get_all(cls) -> Optional[List[Self]]:
        return cls.query.filter_by().all()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
