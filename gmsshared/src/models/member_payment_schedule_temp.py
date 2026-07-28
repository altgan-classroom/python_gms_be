from datetime import datetime
from typing import Optional, Self, Any, List

from sqlalchemy import (
    DateTime, Column, ForeignKey, BigInteger, Boolean, text, Integer, Float, String, Date, JSON)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from gmsshared import db
from gmsshared.src.util.enums import PayrixOnboardStatusEnum, PaymentTransactionTypeEnum
from gmsshared.src.models.location import Location


class MemberPaymentScheduleTemp(db.Model):
    id = Column(BigInteger, nullable=False, primary_key=True)
    location_id = Column(BigInteger, ForeignKey("location.id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("member_profile.user_id"), nullable=False)
    plan_id = Column(BigInteger, nullable=True)
    membership_id = Column(String(50), nullable=True)
    payment_number = Column(Integer, nullable=True)
    plan_start_date = Column(Date, nullable=True)
    plan_end_date = Column(Date, nullable=True)
    auto_renewal = Column(Boolean, nullable=True)
    discount_percent_per_payment = Column(Float, nullable=True)
    discount_amount_per_payment = Column(Float, nullable=True)
    apply_discount_to_all_payments = Column(Boolean, nullable=True)
    salesperson_id = Column(BigInteger, nullable=True)
    total_amount = Column(Float, nullable=True)
    amount = Column(Float, nullable=True)
    signup_fee = Column(Float, nullable=True)
    tax = Column(Float, nullable = True)
    surcharge = Column(Float, nullable=True)
    discount = Column(Float, nullable=True)
    scheduled_date = Column(Date, nullable=True)
    sessions_count = Column(Integer, nullable=True)
    price_per_session = Column(Float, nullable=True)
    split_payments = Column(JSON, nullable=True, default=None)
    create_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(type_=DateTime, nullable=False, server_default=func.now(), onupdate=datetime.utcnow)

    location = relationship(Location)

    def __init__(self, location_id: int, member_id: int):
        self.location_id = location_id
        self.user_id = member_id

    @classmethod
    def find_by_id(cls, location_id: int, user_id: int, membership_id: str, payment_number: int) -> Optional[Self]:
        return cls.query.filter_by(location_id=location_id, user_id=user_id, membership_id=membership_id,
                                   payment_number=payment_number).first()

    @classmethod
    def find_by_membership_id(cls, location_id: int, user_id: int, membership_id: str, payment_number: int = None) -> List[Self]:
        if payment_number:
            return cls.query.filter_by(location_id=location_id, user_id=user_id, membership_id=membership_id,
                                       payment_number=payment_number).first()
        else:
            return cls.query.filter_by(location_id=location_id, user_id=user_id, membership_id=membership_id).all()

    @classmethod
    def copy_payment_schedule(cls, location_id: int, user_id: int, membership_id: str, payment_number:int, new_membership_id:int):
        sql = (f"insert into member_payment_schedule (location_id, user_id, membership_id, payment_number, total_amount,  \
                      amount, signup_fee, tax, surcharge, discount, scheduled_date, payrix_onboarding_status, payment_transaction_type, renewal_count) \
                select location_id, user_id, {new_membership_id}, payment_number, total_amount, amount, signup_fee, tax, \
                     surcharge, discount, scheduled_date, {PayrixOnboardStatusEnum.NOT_READY.value}, {PaymentTransactionTypeEnum.SALE.value}, 0 \
                 from member_payment_schedule_temp \
                 where location_id = {location_id} and user_id = {user_id} \
                     and membership_id='{membership_id}' and payment_number <> {payment_number}")
        db.session.execute(text(sql))
        db.session.commit()

    @classmethod
    def insert_payment_schedule(cls, location_id: int, user_id: int, plan_id: int, membership_id: Any, schedule: Any):
        sql = (f"delete from member_payment_schedule_temp where location_id = {location_id} \
                      and user_id = {user_id} and plan_id = {plan_id} and membership_id = '{membership_id}'")
        db.session.execute(text(sql))
        db.session.commit()

        db.session.add_all(schedule)
        db.session.commit()

    def save(self):
        db.session.add(self)

    def save_and_commit(self):
        self.save()
        db.session.commit()
