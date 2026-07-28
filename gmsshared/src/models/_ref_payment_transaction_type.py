from datetime import datetime
from typing import Optional, List, Self
from sqlalchemy import (
    Column, Integer, String, DateTime, func
)

from gmsshared import db

class _RefPaymentTransactionType(db.Model):
    __tablename__ = "_ref_payment_transaction_type"
    id = Column(Integer, primary_key=True)
    name = Column(String(30), unique=True, nullable=False)
    description = Column(String(200), nullable=True)
    create_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(type_=DateTime, nullable=False, server_default=func.now(), onupdate=datetime.utcnow)

    def __init__(self, name: str):
        self.name = name

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
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
