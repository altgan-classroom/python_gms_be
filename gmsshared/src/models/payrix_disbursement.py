import time
from datetime import datetime, timezone
from typing import Optional, Self

from sqlalchemy import (
    and_,
    Boolean, DateTime, Column, Float, ForeignKey, Integer, String, BigInteger, JSON, insert, text, update
)
from sqlalchemy.sql import func

from gmsshared import db
from gmsshared.src.models._ref_payrix_disbursement_status_type import _RefPayrixDisbursementStatusType
from gmsshared.src.models.location import Location

class PayrixDisbursement(db.Model):
    id = Column(BigInteger, primary_key=True)
    location_id = Column(BigInteger, ForeignKey("location.id"), nullable=False)
    payrix_disbursement_id = Column(String(50), nullable=False)
    payrix_disbursement_status_type_id = Column(Integer, ForeignKey("_ref_payrix_disbursement_status_type.id"), nullable=False)
    payrix_created = Column(DateTime, nullable=False)
    payrix_processed = Column(DateTime, nullable=True)
    amount = Column(Float, nullable=True)
    sales = Column(Float, nullable=True, default=0)
    e_check_sales = Column(Float, nullable=True, default=0)
    e_check_refunds = Column(Float, nullable=True, default=0)
    e_check_chargebacks = Column(Float, nullable=True, default=0)
    remainder = Column(Float, nullable=True, default=0)
    remainder_used = Column(Float, nullable=True, default=0)
    other_events = Column(Float, nullable=True, default=0)
    auth_fees = Column(Float, nullable=True, default=0)
    capture_fees = Column(Float, nullable=True, default=0)
    interchange_fees = Column(Float, nullable=True, default=0)
    payout_fees = Column(Float, nullable=True, default=0)
    refund_fees = Column(Float, nullable=True, default=0)
    chargeback_fees = Column(Float, nullable=True, default=0)
    e_check_sale_fees = Column(Float, nullable=True, default=0)
    e_check_refund_fees = Column(Float, nullable=True, default=0)
    e_check_chargeback_fees = Column(Float, nullable=True, default=0)
    other_fees = Column(Float, nullable=True, default=0)
    refunds = Column(Float, nullable=True, default=0)
    chargebacks = Column(Float, nullable=True, default=0)
    go_fees = Column(Float, nullable=True, default=0)
    in_process = Column(Boolean, nullable=False, default=False)

    create_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(type_=DateTime, nullable=False, server_default=func.now(), onupdate=datetime.utcnow)

    location = db.relationship("Location")

    @classmethod
    def find_most_recent_by_location(cls, location_id: int) -> Optional[Self]:
        return cls.query.filter_by(location_id=location_id).order_by(PayrixDisbursement.payrix_created.desc()).first()

    @classmethod
    def find_non_zero_amount_with_zero_values(cls, location_id: int) -> Optional[Self]:
        zero_fields = [
            "sales", "e_check_sales", "e_check_refunds", "e_check_chargebacks",
            "remainder", "remainder_used", "other_events", "auth_fees",
            "capture_fees", "interchange_fees", "payout_fees", "refund_fees",
            "chargeback_fees", "e_check_sale_fees", "e_check_refund_fees",
            "e_check_chargeback_fees", "other_fees", "refunds", "chargebacks"
        ]
        conditions = [getattr(cls, field) == 0 for field in zero_fields]
        return (
            cls.query.filter_by(location_id=location_id)
            .filter(and_(cls.amount > 0, *conditions))
            .order_by(PayrixDisbursement.payrix_created.asc())
            .first()
        )

    @classmethod
    def delete_by_location_and_start_date(cls, location_id: int, start_date: datetime.date) -> Optional[Self]:
        sql = (f"delete from payrix_disbursement where location_id = {location_id} and payrix_created > '{start_date}'")
        db.session.execute(text(sql))
        db.session.commit()

    @classmethod
    def find_by_id(cls, _id: int) -> Optional[Self]:
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_payrix_disbursement_id(cls, payrix_disbursement_id: str) -> Optional[Self]:
        return cls.query.filter_by(payrix_disbursement_id=payrix_disbursement_id).first()

    def save(self):
        db.session.add(self)

    def save_and_commit(self):
        self.save()
        db.session.commit()
