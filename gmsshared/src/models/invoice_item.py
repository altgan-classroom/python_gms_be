from datetime import datetime
from typing import Optional, Self, List

from sqlalchemy import (
    DateTime, Column, Integer, ForeignKey, Float, BigInteger, asc, Date, func, String, text
)

from gmsshared import db
from gmsshared.src.models._ref_invoice_item_status_type import _RefInvoiceItemStatusType
from gmsshared.src.models._ref_product_category_type import _RefProductCategoryType
from gmsshared.src.util.datetime_util import utc_now
from gmsshared.src.util.enums import InvoiceStatusTypeEnum, ProductCategoryTypeEnum, InvoiceItemStatusTypeEnum, MembershipStatusEnum


class InvoiceItem(db.Model):
    id = Column(BigInteger, nullable=False, primary_key=True)
    location_id = Column(BigInteger, ForeignKey("location.id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("member_profile.user_id"), nullable=False)
    invoice_id = Column(BigInteger, ForeignKey("invoice.id"), nullable=False)
    invoice_item_status_type_id = Column(Integer, ForeignKey("_ref_invoice_item_status_type.id"), nullable=True, default=1)
    product_id = Column(BigInteger, nullable=True)
    description = Column(String(300), nullable=True)
    amount = Column(Float, nullable=False, default=0)
    discount = Column(Float, nullable=False, default=0)
    discount_percent = Column(Float, nullable=True, default=0)
    tax = Column(Float, nullable=False, default=0)
    total_amount = Column(Float, nullable=False, default=0)
    due_date = Column(Date, nullable=True)

    #invoice = db.relationship(Invoice, backref="invoice_items")
    create_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(type_=DateTime, nullable=False, server_default=func.now(), onupdate=datetime.utcnow)

    def __init__(self, location_id: int, user_id: int, product_id: int | None, description: str, amount: float, discount: float, tax: float,
                  due_date: datetime.date = utc_now().date()):
        self.location_id = location_id
        self.user_id = user_id
        self.product_id = product_id
        self.description = description
        self.amount = amount
        self.discount = discount
        self.tax = tax
        self.total_amount = max(0.0, round(amount - discount + tax, 2))
        self.due_date = due_date

    @classmethod
    def find_by_id(cls, location_id, member_id: int, id: int) -> Optional[Self]:
        return cls.query.filter_by(location_id=location_id, user_id=member_id, id=id).first()

    @classmethod
    def find_by_ids(cls, location_id, user_id, invoice_item_ids):
        return cls.query.filter(location_id==location_id, user_id==user_id, InvoiceItem.id.in_(invoice_item_ids)).all()

    @classmethod
    def find_invoice_items(cls, location_id, user_id: int, membership_id: int) -> List[Self]:
        return cls.query.filter_by(location_id=location_id, user_id=user_id, product_id=membership_id).order_by(asc(InvoiceItem.due_date)).all()

    @classmethod
    def find_upcoming_payments(cls) -> List[Self]:
        sql = (f""" select ii.* 
                    from invoice_item ii 
                        left join invoice i on ii.invoice_id = i.id 
                        left join location l on ii.location_id = l.id
                        left join membership mem on mem.id = ii.product_id
                    where ii.due_date <= '{utc_now().date()}' 
                        and ii.invoice_item_status_type_id = {InvoiceItemStatusTypeEnum.PENDING.value}
                        and i.invoice_status_type_id not in ({InvoiceStatusTypeEnum.PAID.value}, {InvoiceStatusTypeEnum.VOID.value})
                        and l.is_dea = 1 and l.payments = 1
                        and (i.product_category_type_id = 1 and mem.membership_status_type_id in (1, 5) 
                           or (product_category_type_id in (2, 3) and ii.product_id in (1, 2, 3, 4)))
                        
        """)
        return (cls.query.from_statement(text(sql)).all())

    def save(self):
        db.session.add(self)

    def save_and_commit(self):
        self.save()
        db.session.commit()