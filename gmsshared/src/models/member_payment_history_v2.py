from datetime import datetime
from typing import Optional, Self, Any, List

from sqlalchemy import (
    Date, DateTime, Column, ForeignKey, BigInteger, Boolean, text, Integer, String, Float, JSON
)
from sqlalchemy.sql import func

from gmsshared.src.util.enums import PayrixOnboardStatusEnum, PayrixTransactionTypeEnum, PayrixTransactionStatusEnum, \
    PaymentTransactionTypeEnum
from gmsshared.src.util.datetime_util import utc_now

from gmsshared import db
from gmsshared.src.models.location import Location
from gmsshared.src.models.member_profile import MemberProfile
from gmsshared.src.models.member_payment_method import MemberPaymentMethod
from gmsshared.src.models.membership import Membership
from gmsshared.src.models.invoice import Invoice
from gmsshared.src.models._ref_payment_transaction_type import _RefPaymentTransactionType
from gmsshared.src.models._ref_payment_category_type import _RefPaymentCategoryType
from gmsshared.src.models._ref_product_category_type import _RefProductCategoryType

class MemberPaymentHistory_v2(db.Model):
    id = Column(BigInteger, nullable=False, primary_key=True)
    location_id = Column(BigInteger, ForeignKey("location.id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("member_profile.user_id"), nullable=False)
    payment_method_id = Column(BigInteger, ForeignKey("member_payment_method.id"), nullable=True)
    invoice_id = Column(BigInteger, ForeignKey("invoice.id"), nullable=True)
    invoice_item_ids = Column(JSON, nullable=True)
    amount = Column(Float, nullable=False, default=0)
    discount = Column(Float, nullable=False, default=0)
    tax = Column(Float, nullable=False, default=0)
    total_amount = Column(Float, nullable=False, default=0)
    original_total_amount = Column(Float, nullable=False, default=0)
    revenue_share_fee = Column(Float, nullable=True, default=0)
    scheduled_date = Column(Date, nullable=True)
    processed_date = Column(DateTime, nullable=True)
    processed_by = Column(BigInteger, nullable=True)
    for_payment_id = Column(BigInteger, ForeignKey("member_payment_history_v2.id"), nullable=True)
    payment_transaction_type_id = Column(Integer, ForeignKey(_RefPaymentTransactionType.id), nullable=True,
                    server_default = str(PaymentTransactionTypeEnum.SALE.value))
    payrix_transaction_id = Column(String(50), nullable=True)
    payrix_disbursement_id = Column(String(50), nullable=True)
    payrix_transaction_status = Column(Integer, nullable=True)
    payrix_transaction_error = Column(String(500), nullable=True)
    payrix_onboarding_status = Column(Integer, nullable=False, server_default='1')
    notes = Column(String(250), nullable=True)
    v1_payment_id = Column(BigInteger, nullable=True)

    create_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(type_=DateTime, nullable=False, server_default=func.now(), onupdate=datetime.utcnow)

    location = db.relationship(Location)
    member = db.relationship(MemberProfile)
    payment_method = db.relationship(MemberPaymentMethod)
    invoice = db.relationship(Invoice, backref="payments")
    refunds_retries = db.relationship('MemberPaymentHistory_v2', foreign_keys=[for_payment_id], viewonly=True,
                                      primaryjoin="MemberPaymentHistory_v2.id == MemberPaymentHistory_v2.for_payment_id")
    original_payment = db.relationship("MemberPaymentHistory_v2", foreign_keys=[for_payment_id], remote_side=[id])

    def __init__(self, location_id: int, user_id: int, payment_method_id: int):
        self.location_id = location_id
        self.user_id = user_id
        self.payment_method_id = payment_method_id
        self.scheduled_date = utc_now().date()
        self.payrix_onboarding_status = PayrixOnboardStatusEnum.NOT_READY.value
        self.amount = 0
        self.discount = 0
        self.tax = 0
        self.total_amount = 0

    @classmethod
    def find_by_id(cls, location_id: int, user_id: int, payment_id) -> Optional[Self]:
        return cls.query.filter_by(location_id=location_id, user_id=user_id, id=payment_id).first()

    @classmethod
    def find_by_location_id(cls, location_id):
        return cls.query.filter_by(location_id=location_id).all()


    @classmethod
    def find_by_payrix_txn_id(cls, payrix_transaction_id) -> Optional[Self]:
        return cls.query.filter_by(payrix_transaction_id=payrix_transaction_id).first()


    @classmethod
    def find_by_member_id(cls, _location_id: int, _user_id: int) -> Optional[List[Self]]:
        return cls.query.filter_by(location_id=_location_id, user_id=_user_id).all()

    @classmethod
    def find_history_by_member_id(cls, location_id: int, user_id: int) -> Optional[List[Self]]:
        sql = f"""select mph.*
            from member_payment_history_v2 mph 
                left join member_payment_method mpm on mpm.id = mph.payment_method_id 
                left join _ref_payrix_transaction_status_type pts on pts.id = mph.payrix_transaction_status 
            where mph.location_id = {location_id} and mph.user_id = {user_id} 
                and mph.payment_transaction_type_id = {PaymentTransactionTypeEnum.SALE.value} 
                and (payrix_transaction_status is not null or scheduled_date is not null) and mph.payrix_onboarding_status <> {PayrixOnboardStatusEnum.QUEUED.value}"""
        return (cls.query.from_statement(text(sql)).all())

    @classmethod
    def find_failed_by_location_id(cls, location_id: int, report_date_from, report_date_to):
        sql = f"""select * 
               from member_payment_history_v2 
               where location_id = {location_id} and payrix_transaction_status in ({PayrixTransactionStatusEnum.FAILED.value},{PayrixTransactionStatusEnum.RETURNED.value})
                  and for_payment_id is null
                  and processed_date between '{report_date_from}' and '{report_date_to}'"""
        return (cls.query.from_statement(text(sql)).all())

    @classmethod
    def get_queued_retry_payment_of_original_payment(cls, location_id: int, for_payment_id: int, payment_transaction_type_id: int):
        return cls.query.filter_by(location_id=location_id, for_payment_id=for_payment_id,
                                   payment_transaction_type_id=payment_transaction_type_id,
                                   payrix_onboarding_status=PayrixOnboardStatusEnum.QUEUED.value).first()

    @classmethod
    def get_payments_total(cls, location_id: int, user_id: int):
        sql = f"""
                with normal_sale_txns as
                     (select sum(total_amount) as sales
                      from member_payment_history_v2
                      where location_id = {location_id}
                        and user_id = {user_id}
                        and payrix_transaction_status in (4)
                        and payment_transaction_type_id in (1, 3)
                        and payrix_transaction_error is null
                        and processed_date is not null),
                refund_txns as
                    (select sum(total_amount) as refunds
                    from member_payment_history_v2
                    where location_id = {location_id}
                    and user_id = {user_id}
                        and payrix_transaction_status in (4)
                        and payment_transaction_type_id in (2)
                        and payrix_transaction_error is null
                        and processed_date is not null)
                select ifnull((select sales from normal_sale_txns), 0) - ifnull((select refunds from refund_txns), 0) as payments_total;
              """
        result = db.session.execute(text(sql))
        return result.mappings().first()

    @classmethod
    def find_upcoming_payments(cls):
        sql = f"""
                select mphv2.* 
                from member_payment_history_v2 mphv2 left join location l on l.id = mphv2.location_id 
                where mphv2.payrix_onboarding_status = {PayrixOnboardStatusEnum.NOT_READY.value} 
                   and ifnull(payrix_transaction_status, 0) <> {PayrixTransactionStatusEnum.CANCELLED.value} 
                   and processed_date is null
                   and payment_transaction_type_id = {PaymentTransactionTypeEnum.SALE.value}
                   and scheduled_date <= date(now())
                   and payment_method_id <> 0
                   and l.is_dea = 1 and l.payments = 1
              """
        return (cls.query.from_statement(text(sql)).all())


    def save(self):
        db.session.add(self)

    def save_and_commit(self):
        self.save()
        db.session.commit()
