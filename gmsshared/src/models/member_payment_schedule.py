from datetime import datetime
from typing import Optional, Self, Any, List

from sqlalchemy import (
    DateTime, Column, ForeignKey, BigInteger, text, Integer, String, Float, Date
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from gmsshared.src.util.enums import PayrixOnboardStatusEnum, PaymentTransactionTypeEnum, MembershipStatusEnum
from gmsshared import db
from gmsshared.src.models._ref_payrix_onboard_status_type import _RefPayrixOnboardStatusType
from gmsshared.src.models._ref_payment_transaction_type import _RefPaymentTransactionType
from gmsshared.src.models.member_profile import MemberProfile
from gmsshared.src.models.location import Location
from gmsshared.src.models._ref_payment_category_type import _RefPaymentCategoryType


class MemberPaymentSchedule(db.Model):
    id = Column(BigInteger, nullable=False, primary_key=True)
    location_id = Column(BigInteger, ForeignKey("location.id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("member_profile.user_id"), nullable=False)
    membership_id = Column(BigInteger, nullable=True)
    payment_number = Column(Integer, nullable=True)
    total_amount = Column(Float, nullable=True)
    amount = Column(Float, nullable=True)
    signup_fee = Column(Float, nullable=True)
    tax = Column(Float, nullable = True)
    surcharge = Column(Float, nullable=True)
    discount = Column(Float, nullable=True)
    scheduled_date = Column(Date, nullable=False)
    payment_category_type_id = Column(Integer, ForeignKey(_RefPaymentCategoryType.id), nullable=True)
    description = Column(String(250), nullable=True)
    for_payment_id = Column(BigInteger, nullable=True)
    payment_transaction_type = Column(Integer, ForeignKey(_RefPaymentTransactionType.id), nullable=True,
                    server_default = str(PaymentTransactionTypeEnum.SALE.value))
    payrix_onboarding_status: int = Column(Integer, ForeignKey(_RefPayrixOnboardStatusType.id), nullable=True,
                    server_default=str(PayrixOnboardStatusEnum.NOT_READY.value))
    payrix_onboarding_error = Column(String(250), nullable=True)
    sessions_count = Column(Integer, nullable=True)
    price_per_session = Column(Float, nullable=True)
    renewal_count = Column(Integer, nullable=True)
    notes = Column(String(250), nullable=True)

    create_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(type_=DateTime, nullable=False, server_default=func.now(), onupdate=datetime.utcnow)

    member = relationship(MemberProfile, backref="payments_scheduled")
    location = relationship(Location)
    payment_category = relationship(_RefPaymentCategoryType)

    def __init__(self, location_id: int, user_id: int):
        self.location_id = location_id
        self.user_id = user_id

    @classmethod
    def find_active_payment_schedule_by_id(cls, location_id: int, user_id: int, payment_id: int) -> Optional[Self]:
        return (
            cls.query
            .join(Location, Location.id == cls.location_id)  # Join with Location table
            .filter(
                cls.location_id == location_id,
                cls.user_id == user_id,
                cls.id == payment_id,
                Location.payments == True  # Combined all filters
            ).first()
        )

    @classmethod
    def find_by_id(cls, location_id: int, user_id: int, payment_id: int) -> Optional[Self]:
        return cls.query.filter_by(location_id=location_id, user_id=user_id, id=payment_id).first()

    @classmethod
    def find_by_member_id(cls, location_id: int, user_id: int) -> List[Self]:
        return cls.query.filter_by(location_id=location_id, user_id=user_id).all()

    @classmethod
    def find_by_membership_id(cls, location_id: int, user_id: int, membership_id: int, payment_number: int = None) -> List[Self]:
        if payment_number:
            return cls.query.filter_by(location_id=location_id, user_id=user_id, membership_id=membership_id, payment_number=payment_number).first()
        else:
            return cls.query.filter_by(location_id=location_id, user_id=user_id, membership_id=membership_id).all()

    @classmethod
    def get_queued_retry_payment_of_original_payment(cls, location_id: int, for_payment_id: int, payment_transaction_type: int):
        return cls.query.filter_by(location_id=location_id, for_payment_id = for_payment_id, payment_transaction_type = payment_transaction_type).first()

    @classmethod
    def find_schedule_by_member_id(cls, location_id: int, user_id: int) -> Optional[Self]:
        sql = (f'select mph.location_id, mph.user_id, mph.total_amount as amount, mph.discount, mph.id, \
                 p.name as plan, mph.scheduled_date, mp.plan_id \
            from member_payment_schedule mph \
                left join membership mp on mph.membership_id = mp.id \
                left join plan p on p.id = mp.plan_id \
            where mph.location_id = {location_id} and mph.user_id = {user_id} and mph.membership_id is not null')
        result = db.session.execute(text(sql))
        return result.mappings().all()

    @classmethod
    def find_upcoming_payments(cls) -> Optional[Self]:
        sql = (f'select mps.location_id, mps.user_id, mps.id as payment_id, scheduled_date, \
                     (select mpm.id \
                      from member_payment_method mpm \
                      where mpm.location_id = mps.location_id and mpm.user_id = mps.user_id \
                          and default_method = 1 and payrix_onboarding_status = {PayrixOnboardStatusEnum.BOARDED.value} \
                      order by mpm.update_datetime desc limit 1)  as payment_method_id \
                 from member_payment_schedule mps \
                      left join membership mp on mps.membership_id = mp.id \
                      join location l ON mps.location_id = l.id \
                 where scheduled_date <= \'{datetime.utcnow().date()}\' \
                       and ifnull(mp.membership_status_type_id, 1) = {MembershipStatusEnum.ACTIVE.value} and mps.membership_id is not null \
                       and l.payments != FALSE and l.is_dea <> 1 \
                 order by scheduled_date')
        result = db.session.execute(text(sql))
        return result.mappings().all()

    @classmethod
    def delete_payment_schedule_by_member_id(cls, location_id, user_id: int) -> Optional[Self]:
        sql = (f"delete from member_payment_schedule where location_id = {location_id} and user_id = {user_id}")
        db.session.execute(text(sql))

    @classmethod
    def insert_payment_schedule(cls, location_id: int, user_id: int, membership_id: Any, schedule: Any):
        db.session.add_all(schedule)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def save(self):
        db.session.add(self)

    def save_and_commit(self):
        self.save()
        db.session.commit()
