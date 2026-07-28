from datetime import datetime
from typing import Optional, Self, Any, List

from sqlalchemy import (
    DateTime, Column, ForeignKey, BigInteger, Boolean, text, Integer, String, Float
)
from sqlalchemy.sql import func

from gmsshared.src.util.enums import PayrixTransactionTypeEnum, PayrixTransactionStatusEnum, PaymentTransactionTypeEnum
from gmsshared import db
from gmsshared.src.models.location import Location
from gmsshared.src.models.member_profile import MemberProfile
from gmsshared.src.models.member_payment_method import MemberPaymentMethod
from gmsshared.src.models.membership import Membership
from gmsshared.src.models._ref_payment_transaction_type import _RefPaymentTransactionType
from gmsshared.src.models._ref_payment_category_type import _RefPaymentCategoryType

class MemberPaymentHistory(db.Model):
    id = Column(BigInteger, nullable=False, autoincrement=False, primary_key=True)
    location_id = Column(BigInteger, ForeignKey("location.id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("member_profile.user_id"), nullable=False)
    payment_method_id = Column(BigInteger, ForeignKey("member_payment_method.id"), nullable=True)
    membership_id = Column(BigInteger, ForeignKey("membership.id"), nullable=True)
    payment_number = Column(Integer, nullable=True)
    total_amount = Column(Float, nullable=True)
    amount = Column(Float, nullable=True)
    signup_fee = Column(Float, nullable=True)
    tax = Column(Float, nullable = True)
    surcharge = Column(Float, nullable=True)
    discount = Column(Float, nullable=True)
    revenue_share_fee = Column(Float, nullable=True, default=0)
    processed_date = Column(DateTime, nullable=False)
    processed_by = Column(BigInteger, nullable=True)
    payment_category_type_id = Column(Integer, ForeignKey(_RefPaymentCategoryType.id), nullable=True)
    description = Column(String(250), nullable=True)
    for_payment_id = Column(BigInteger, ForeignKey("member_payment_history.id"), nullable=True)
    payment_transaction_type = Column(Integer, ForeignKey(_RefPaymentTransactionType.id), nullable=True,
                    server_default = str(PaymentTransactionTypeEnum.SALE.value))
    payrix_transaction_id = Column(String(50), nullable=True)
    payrix_disbursement_id = Column(String(50), nullable=True)
    payrix_transaction_status = Column(Integer, nullable=True, server_default='1')
    payrix_transaction_error = Column(String(500), nullable=True)
    renewal_count = Column(Integer, nullable=True)
    notes = Column(String(250), nullable=True)
    v2_payment_id = Column(BigInteger, nullable=True)

    create_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(type_=DateTime, nullable=False, server_default=func.now(), onupdate=datetime.utcnow)

    member = db.relationship(MemberProfile, backref='payments')
    location = db.relationship(Location)
    payment_method = db.relationship(MemberPaymentMethod)
    membership = db.relationship(Membership, backref='payments')
    payment_category = db.relationship(_RefPaymentCategoryType)
    refunds_retries = db.relationship('MemberPaymentHistory', foreign_keys=[for_payment_id], viewonly=True,
                                      primaryjoin="MemberPaymentHistory.id == MemberPaymentHistory.for_payment_id")
    original_payment = db.relationship("MemberPaymentHistory", foreign_keys=[for_payment_id], remote_side=[id])

    @classmethod
    def find_by_id(cls, location_id: int, user_id: int, payment_id) -> Optional[Self]:
        return cls.query.filter_by(location_id=location_id, user_id=user_id, id=payment_id).first()

    @classmethod
    def find_by_payrix_txn_id(cls, payrix_transaction_id) -> Optional[Self]:
        return cls.query.filter_by(payrix_transaction_id=payrix_transaction_id).first()

    @classmethod
    def find_by_member_id(cls, _location_id: int, _user_id: int) -> Optional[List[Self]]:
        return cls.query.filter_by(location_id=_location_id, user_id=_user_id).all()

    @classmethod
    def find_by_member_id_no_membership_or_category(cls, _location_id: int, _user_id: int) -> Optional[List[Self]]:
        return cls.query.filter_by(location_id=_location_id, user_id=_user_id, membership_id=None, payment_category_type_id=None, for_payment_id=None).all()

    @classmethod
    def find_by_v2_payment_id(cls,_location_id: int, _user_id: int, _v2_payment_id: int):
        return  cls.query.filter_by(location_id=_location_id, user_id=_user_id, v2_payment_id=_v2_payment_id).first()

    @classmethod
    def find_history_by_member_id(cls, location_id: int, user_id: int) -> Optional[List[Self]]:
        sql = f"""select mph.*
            from member_payment_history mph 
                left join membership mp on mph.membership_id = mp.id 
                left join plan p on p.id = mp.plan_id 
                left join _ref_payment_category_type pct on pct.id = mph.payment_category_type_id 
                left join member_payment_method mpm on mpm.id = mph.payment_method_id 
                left join _ref_payrix_transaction_status_type pts on pts.id = mph.payrix_transaction_status 
            where mph.location_id = {location_id} and mph.user_id = {user_id} and mph.payment_transaction_type = 1 
               and (mp.plan_id is not null or mph.payment_category_type_id is not null or mp.id is null)"""
        return (cls.query.from_statement(text(sql)).all())

    @classmethod
    def find_failed_by_location_id(cls, location_id: int, report_date_from, report_date_to):
        sql = f"""select * 
               from member_payment_history 
               where location_id = {location_id} and payrix_transaction_status in ({PayrixTransactionStatusEnum.FAILED.value},{PayrixTransactionStatusEnum.RETURNED.value})
                  and for_payment_id is null
                  and processed_date between '{report_date_from}' and '{report_date_to}'"""
        return (cls.query.from_statement(text(sql)).all())


    @classmethod
    def find_last_payment_processed(cls, location_id: int, membership_id: int, user_id: int):
        return (
            cls.query
            .filter(
                cls.location_id == location_id,
                cls.membership_id == membership_id,
                cls.user_id == user_id,
                cls.payment_transaction_type == PaymentTransactionTypeEnum.SALE.value,
                cls.payrix_transaction_status.in_([
                    PayrixTransactionStatusEnum.SETTLED.value,
                    PayrixTransactionStatusEnum.CAPTURED.value,
                    PayrixTransactionStatusEnum.APPROVED.value,
                    PayrixTransactionStatusEnum.FAILED.value,
                    PayrixTransactionStatusEnum.RETURNED.value
                ]),
                cls.payment_number.isnot(None)
            )
            .order_by(cls.processed_date.desc())
            .first()
        )

    def save(self):
        db.session.add(self)

    def save_and_commit(self):
        self.save()
        db.session.commit()
