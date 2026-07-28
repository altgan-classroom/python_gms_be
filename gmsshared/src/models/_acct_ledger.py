from typing import Optional, List, Self
from datetime import datetime
from sqlalchemy import (
    DateTime, Column, Integer, String, BigInteger, Float, Boolean, ForeignKey
)
from sqlalchemy.sql import func
from gmsshared.src.util.datetime_util import utc_now
from gmsshared import db

class _AcctLedger(db.Model):
    __tablename__ = "_acct_ledger"
    id = Column(BigInteger, primary_key=True)
    location_id = Column(BigInteger, ForeignKey("location.id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("member_profile.user_id"), nullable=True)
    account_id = Column(Integer, nullable=False)
    txn_date = Column(DateTime, nullable=False)
    amount = Column(Float, nullable=False)
    credit = Column(Boolean, nullable=False)
    create_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(type_=DateTime, nullable=False, server_default=func.now(), onupdate=datetime.utcnow)

    def __init__(self, location_id, user_id, account_id, amount, credit):
        self.location_id = location_id
        self.user_id = user_id
        self.account_id = account_id
        self.txn_date = utc_now()
        self.amount = amount
        self.credit = credit

    @classmethod
    def find_by_id(cls, id: int) -> Optional[Self]:
        return cls.query.filter_by(id=id).first()

    @classmethod
    def bulk_insert(cls, rows: List[Self]):
        db.session.add_all(rows)
        db.session.commit()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
