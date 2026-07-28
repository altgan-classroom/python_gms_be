from datetime import datetime
from typing import Optional, Self, List

from sqlalchemy import (
    DateTime, Column, Integer, String, ForeignKey, Float, BigInteger, asc, func, text, and_
)
from sqlalchemy.orm import relationship
from gmsshared.src.util.enums import InvoiceStatusTypeEnum, InvoiceItemStatusTypeEnum

from gmsshared import db
from gmsshared.src.models.user import User
from gmsshared.src.models.location import Location
from gmsshared.src.models.user_profile import UserProfile
from gmsshared.src.models.member_profile import MemberProfile
from gmsshared.src.models.invoice_item import InvoiceItem
from gmsshared.src.models.membership import Membership
from gmsshared.src.models._ref_invoice_type import _RefInvoiceType
from gmsshared.src.models._ref_invoice_status_type import _RefInvoiceStatusType
from gmsshared.src.util.datetime_util import utc_now
from gmsshared.src.util.enums import InvoiceTypeEnum, ProductCategoryTypeEnum


class Invoice(db.Model):
    id = Column(BigInteger, nullable=False, primary_key=True)
    location_id = Column(BigInteger, ForeignKey("location.id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("member_profile.user_id"), nullable=False)
    invoice_type_id = Column(Integer, ForeignKey("_ref_invoice_type.id"), nullable=False, default=1)
    invoice_status_type_id = Column(Integer, ForeignKey("_ref_invoice_status_type.id"), nullable=False, default=1)
    for_invoice_id = Column(BigInteger, ForeignKey("invoice.id"), nullable=True )
    processed_user_id = Column(BigInteger, nullable=True)
    notes = Column(String(200), nullable=True)
    product_category_type_id = Column(Integer, ForeignKey("_ref_product_category_type.id"), nullable=True,
                                      default=ProductCategoryTypeEnum.MEMBERSHIP.value)
    void_datetime = Column(DateTime, nullable=True)
    void_by = Column(BigInteger, ForeignKey("user.id"), nullable=True)

    create_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(type_=DateTime, nullable=False, server_default=func.now(), onupdate=datetime.utcnow)
    description = Column(String(300), nullable=True)

    invoice_items = relationship("InvoiceItem", backref="invoice")
    member = relationship("MemberProfile", backref="invoices")

    @property
    def membership_id(self):
        return self.invoice_items[-1].product_id if self.invoice_items and (self.product_category_type_id == ProductCategoryTypeEnum.MEMBERSHIP.value) else None

    @property
    def due_date(self):
        items_with_due_date = [item for item in self.invoice_items if item.due_date is not None]
        if not items_with_due_date:
            return None
        return max(items_with_due_date, key=lambda item: item.due_date).due_date

    @property
    def total_amount(self):
        return sum([item.total_amount for item in self.invoice_items if item.invoice_item_status_type_id != InvoiceItemStatusTypeEnum.CANCELLED.value])

    @property
    def discount(self):
        return sum([item.discount for item in self.invoice_items if item.invoice_item_status_type_id != InvoiceItemStatusTypeEnum.CANCELLED.value])

    @property
    def discount_percent(self):
        return sum([item.discount_percent for item in self.invoice_items if item.invoice_item_status_type_id != InvoiceItemStatusTypeEnum.CANCELLED.value])

    @property
    def tax(self):
        return sum([item.tax for item in self.invoice_items if item.invoice_item_status_type_id != InvoiceItemStatusTypeEnum.CANCELLED.value])

    @property
    def amount(self):
        return sum([item.amount for item in self.invoice_items if item.invoice_item_status_type_id != InvoiceItemStatusTypeEnum.CANCELLED.value])

    def __init__(self, location_id, user_id: int):
        self.location_id = location_id
        self.user_id = user_id

    @classmethod
    def find_by_id(cls, location_id, member_id: int, id: int) -> Optional[Self]:
        return cls.query.filter_by(location_id=location_id, user_id=member_id, id=id).first()

    @classmethod
    def find_all_invoices_by_member_id(cls, location_id, user_id: int) -> List[Self]:
        return cls.query.filter_by(location_id=location_id, user_id=user_id).order_by(asc(Invoice.create_datetime)).all()

    @classmethod
    def find_all_invoices_by_membership_id(cls, location_id, user_id: int, membership_id: int, pending = False) -> List[Self]:
        filters = [
            cls.location_id == location_id,
            cls.user_id == user_id,
            cls.product_category_type_id == ProductCategoryTypeEnum.MEMBERSHIP.value
        ]
        if pending:
            filters.append(cls.invoice_status_type_id == InvoiceStatusTypeEnum.PENDING.value)

        all_invoices = cls.query.filter(*filters).all()

        # Filter by membership_id
        return [
            inv for inv in all_invoices
            if inv.membership_id == membership_id
        ]

    @classmethod
    def find_all_invoices(cls, location_id, user_id: int):
        sql = f"""select *
                  from invoice 
                  where location_id = {location_id} 
                      and user_id = {user_id}
                      and invoice_status_type_id <> {InvoiceStatusTypeEnum.VOID.value}
                  order by create_datetime"""
        return cls.query.from_statement(text(sql)).all()

    @classmethod
    def find_next_invoices(cls):
        sql = f"""
            with active_membership_data as
                (select mem.location_id,
                    mem.user_id,
                    mem.id as membership_id,
                    mem.plan_id,
                    mem.plan_start_date,
                    mem.plan_end_date,
                    p.recurring_interval,
                    p.recurring_duration_type_id,
                    p.first_of_month,
                    mem.auto_renewal
                from membership mem
                    left join plan p on mem.plan_id = p.id
                    left join location l on l.id = mem.location_id
                where mem.membership_status_type_id = 1
                    and p.billing_type_id = 1
                    and l.is_dea = 1 and l.payments = 1),
            invoice_items as
                (select amd.location_id,
                    amd.user_id,
                    case when isnull(i.create_datetime) then
                        case when amd.recurring_duration_type_id = 1
                                then date_add(amd.plan_start_date, interval -amd.recurring_interval day)
                            when recurring_duration_type_id = 2
                                then date_add(amd.plan_start_date, interval -amd.recurring_interval week)
                            when recurring_duration_type_id = 3
                                then date_add(amd.plan_start_date, interval -amd.recurring_interval month)
                            when recurring_duration_type_id = 4
                                then date_add(amd.plan_start_date, interval -amd.recurring_interval year)
                        end
                        else i.create_datetime
                    end as create_datetime,
                    case when isnull(ii.product_id) then amd.membership_id else ii.product_id end as membership_id,
                    ii.invoice_id,
                    ifnull(i.invoice_type_id, 1) as invoice_type_id
                from invoice_item ii
                    left join invoice i on i.id = ii.invoice_id
                    right join active_membership_data amd on ii.location_id = amd.location_id
                                                                 and ii.user_id = amd.user_id
                                                                 and ifnull(ii.product_id, amd.membership_id) = amd.membership_id),
            recent_invoice_dates as
                (select ii.location_id,
                    ii.user_id,
                    max(ii.create_datetime) as last_invoice_date,
                    ii.membership_id as membership_id
                from invoice_items ii
                where ii.invoice_type_id = 1
                group by ii.location_id, ii.user_id, ii.membership_id),
            recent_freezes as
                (select mf.location_id,
                    mf.user_id,
                    mf.membership_id,
                    sum(datediff(mf.freeze_to, mf.freeze_from) + 1) as freeze_duration
                from recent_invoice_dates rsd
                    left join membership_freeze mf
                        on rsd.location_id = mf.location_id
                           and rsd.user_id = mf.user_id
                           and rsd.membership_id = mf.membership_id
                where rsd.last_invoice_date between if(mf.freeze_from <= rsd.last_invoice_date, mf.freeze_from, rsd.last_invoice_date) and mf.freeze_to
                group by mf.location_id, mf.user_id, mf.membership_id),
            next_invoice_dates as
                (select amd.location_id,
                    amd.user_id,
                    amd.membership_id,
                    amd.plan_start_date,
                    amd.plan_end_date,
                    rsd.last_invoice_date,
                    rf.freeze_duration,
                    amd.plan_id,
                    recurring_interval,
                    recurring_duration_type_id,
                    amd.auto_renewal,
                    first_of_month,
                    case when first_of_month = 1
                            then DATE_SUB(LAST_DAY(DATE_ADD(rsd.last_invoice_date, INTERVAL 1 MONTH)),
                                INTERVAL DAY(LAST_DAY(DATE_ADD(rsd.last_invoice_date, INTERVAL 1 MONTH)))-1 DAY)
                        when recurring_duration_type_id = 1
                            then date_add(rsd.last_invoice_date, interval recurring_interval day)
                        when recurring_duration_type_id = 2
                            then date_add(rsd.last_invoice_date, interval recurring_interval week)
                        when recurring_duration_type_id = 3
                            then date_add(rsd.last_invoice_date, interval recurring_interval month)
                        when recurring_duration_type_id = 4
                            then date_add(rsd.last_invoice_date, interval recurring_interval year)
                     end as next_invoice_date
                from active_membership_data amd
                    left join recent_invoice_dates rsd
                        on amd.location_id = rsd.location_id
                            and amd.user_id = rsd.user_id
                            and amd.membership_id = rsd.membership_id
                    left join recent_freezes rf
                        on amd.location_id = rf.location_id
                            and amd.user_id = rf.user_id
                            and amd.membership_id = rf.membership_id)
            select nid.location_id,
                nid.user_id,
                nid.membership_id,
                nid.plan_id,
                nid.recurring_interval,
                nid.recurring_duration_type_id,
                nid.first_of_month,
                nid.plan_start_date,
                nid.plan_end_date,
                cast(nid.freeze_duration as unsigned) as freeze_duration,
                nid.auto_renewal,
                date_add(nid.next_invoice_date, interval ifnull(nid.freeze_duration, 0) day) as next_invoice_date
            from next_invoice_dates nid
            where date(date_add(nid.next_invoice_date, interval ifnull(nid.freeze_duration, 0) day)) <= date(now()) 
                and if(ifnull(nid.auto_renewal, 0) <> 1, 
                   (date(date_add(nid.next_invoice_date, interval ifnull(nid.freeze_duration, 0) day)) <= nid.plan_end_date), TRUE)                
        """
        result = db.session.execute(text(sql))
        results_as_dict = result.mappings().all()
        return results_as_dict

    @classmethod
    def find_writeoff_invoice_by_id(cls, location_id, user_id: int, id: int) -> List[int]:
        return cls.query.filter_by(location_id=location_id, user_id=user_id, for_invoice_id=id, invoice_type_id=InvoiceTypeEnum.WRITEOFF.value).all()

    @classmethod
    def get_payment_number_for_invoice_(cls, location_id: int, membership_id: int, invoice_id: int):
        sql = f"""
            WITH membership_invoices AS (
                SELECT DISTINCT
                    i.id AS invoice_id,
                    i.create_datetime AS processed_date
                FROM invoice i
                JOIN invoice_item ii ON ii.invoice_id = i.id
                WHERE ii.product_id = {membership_id}
                  AND i.product_category_type_id = {ProductCategoryTypeEnum.MEMBERSHIP.value}
                  AND i.invoice_status_type_id <> {InvoiceStatusTypeEnum.VOID.value}
                  AND i.location_id = {location_id}
            ),
            ranked_invoices AS (
                SELECT
                    invoice_id,
                    ROW_NUMBER() OVER (ORDER BY processed_date ASC) AS payment_number
                FROM membership_invoices
            )
            SELECT payment_number
            FROM ranked_invoices
            WHERE invoice_id = {invoice_id}"""
        result = db.session.execute(text(sql))
        results_as_dict = result.mappings().first()
        return results_as_dict

    @classmethod
    def find_latest_invoice_for_membership(cls, location_id: int, user_id: int, membership_id: int) -> Optional[Self]:
        return (
            db.session.query(cls)
            .join(cls.invoice_items)
            .filter(
                cls.location_id == location_id,
                cls.user_id == user_id,
                cls.product_category_type_id == ProductCategoryTypeEnum.MEMBERSHIP.value,
                cls.invoice_items.any(product_id=membership_id)
            )
            .order_by(cls.create_datetime.desc())
            .first()
        )

    @classmethod
    def find_discount_applied_latest_invoice_for_membership(cls, location_id: int, user_id: int, membership_id: int) -> Optional[Self]:
        return (
            db.session.query(cls)
            .join(InvoiceItem, cls.id == InvoiceItem.invoice_id)
            .join(Membership, and_(
                Membership.id == InvoiceItem.product_id,
                Membership.user_id == user_id,
                Membership.location_id == location_id
            ))
            .filter(
                cls.location_id == location_id,
                cls.user_id == user_id,
                cls.product_category_type_id == ProductCategoryTypeEnum.MEMBERSHIP.value,
                InvoiceItem.product_id == membership_id,
                InvoiceItem.discount > 0,
                Membership.id == membership_id,
                Membership.discount_percent_per_payment <= 0,
                Membership.discount_amount_per_payment <= 0,
                Membership.apply_discount_to_all_payments == False
            )
            .order_by(cls.create_datetime.desc())
            .first()
        )

    def save(self):
        db.session.add(self)

    def save_and_commit(self):
        self.save()
        db.session.commit()