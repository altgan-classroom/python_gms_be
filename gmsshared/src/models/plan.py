from datetime import datetime
from typing import Optional, Self

from sqlalchemy import (
    Boolean, DateTime, Column, Integer, String, ForeignKey, Float, text, BigInteger, Date, or_
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from gmsshared import db
from gmsshared.src.models._ref_billing_type import _RefBillingType
from gmsshared.src.models.location import Location
from gmsshared.src.models._ref_duration_type import _RefDurationType
from gmsshared.src.models._ref_plan_type import _RefPlanType
from gmsshared.src.models._ref_plan_status_type import _RefPlanStatusType
from gmsshared.src.models._ref_membership_type import _RefMembershipType
from gmsshared.src.util.enums import MembershipStatusEnum, PlanStatusType

plan_plan_type = db.Table("plan_plan_type",
                          Column("plan_id", BigInteger, ForeignKey("plan.id"), primary_key=True),
                          Column("plan_type_id", Integer, ForeignKey("_ref_plan_type.id"), primary_key=True))

# A plan can belong to one or more locations
plan_location = db.Table("plan_location",
                         Column("plan_id", BigInteger, ForeignKey("plan.id"), primary_key=True),
                         Column("location_id", BigInteger, ForeignKey("location.id"), primary_key=True))


class Plan(db.Model):
    id = Column(BigInteger, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(200), nullable=True)
    duration = Column(Float, nullable=True)
    signup_fee = Column(Float, nullable=True)
    recurring_amount = Column(Float, nullable=True)
    recurring_interval = Column(Float, nullable=True)
    classes_per_week = Column(Integer, nullable=True)
    unlimited = Column(Boolean, nullable=True, default=False)
    auto_renewal = Column(Boolean, nullable=True, default=False)
    paid_in_full_price = Column(Float, nullable=True)
    limit_total_classes = Column(Boolean, nullable=True, default=False)
    class_or_session_pack_price = Column(Float, nullable=True)
    pass_limit = Column(Integer, nullable=True)
    pass_expiration = Column(Integer, nullable=True)
    trial = Column(Boolean, nullable=True)
    challenge = Column(Boolean, nullable=True)
    grandfathered = Column(Boolean, nullable=True, default=False)
    check_in_required = Column(Boolean, nullable=True, default=False)
    booking_required = Column(Boolean, nullable=True, default=False)
    min_age = Column(Integer, nullable=True)
    max_age = Column(Integer, nullable=True)
    access_for_24_hrs = Column(Boolean, nullable=True, default=False)
    revenue_rate = Column(Float, nullable=True, default=0.0)
    sessions_count = Column(Integer, nullable=True)
    sessions_limit_times = Column(Integer, nullable=True)
    sessions_limit_every = Column(Integer, nullable=True)
    first_of_month = Column(Boolean, nullable=True, default=False)
    taxable = Column(Boolean, nullable=True, default=False)
    apply_weekly_registration_limits = Column(Boolean, nullable=True, default=False)
    weekly_limit_times = Column(Integer, nullable=True)

    create_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(type_=DateTime, nullable=False, server_default=func.now(), onupdate=datetime.utcnow)

    # A Plan can belong to a Location
    location_id = Column(BigInteger, ForeignKey("location.id"), nullable=False)

    # A Plan can be of one Type
    plan_types = relationship("_RefPlanType", secondary=plan_plan_type)

    # A plan can have one Duration Type
    duration_type_id = Column(Integer, ForeignKey("_ref_duration_type.id"), nullable=True, server_default="1")

    # A plan be of a Billing Type
    billing_type_id = Column(Integer, ForeignKey("_ref_billing_type.id"), nullable=False)

    # If recurring plan, then define recurring duration
    recurring_duration_type_id = Column(Integer, ForeignKey("_ref_duration_type.id"), nullable=True, server_default="1")

    # If class or session packs plan, then define pass expiration duration
    pass_expiration_duration_type_id = Column(Integer, ForeignKey("_ref_duration_type.id"), nullable=True, server_default="1")

    # If class or session packs plan, then define pass expiration duration
    sessions_limit_duration_type_id = Column(Integer, ForeignKey("_ref_duration_type.id"), nullable=True, server_default="1")

    # A plan has a status
    plan_status_type_id = Column(Integer, ForeignKey("_ref_plan_status_type.id"), nullable=True)

    # A plan can be of a certain membership_type (just a label) for reporting
    membership_type_id = Column(Integer, ForeignKey("_ref_membership_type.id"), nullable=True, default="1")

    # A plan can be used to give access to many locations
    plan_locations = relationship("Location", secondary=plan_location)

    location = relationship(Location)

    @classmethod
    def find_by_id(cls, id: int) -> Optional[Self]:
        return cls.query.filter_by(id=id).first()

    @classmethod
    def find_by_location(cls, location_id: int) -> dict:
        sql = f"""
            select 
                p.location_id, 
                p.id as plan_id, 
                p.name as plan_name, 
                group_concat(distinct pt.name SEPARATOR ', ') as plan_type,
                concat(p.duration, ' ', dt.name) as plan_duration, 
                p.billing_type_id, 
                group_concat(distinct cagp.class_access_group_id SEPARATOR ',') as class_access_group,
                p.grandfathered, 
                bt.name as billing_type, 
                p.signup_fee,
                CASE
                   WHEN p.billing_type_id = 1 THEN recurring_amount
                   WHEN p.billing_type_id = 2 THEN paid_in_full_price
                   WHEN p.billing_type_id = 3 THEN class_or_session_pack_price
                   WHEN p.billing_type_id = 4 THEN 0
                   ELSE NULL
                END AS price,
                case when p.plan_status_type_id = 3 then 'Cancelled'
                     when p.grandfathered then 'Grandfathered'
                     else 'Active'
                end as plan_status,
            mt.name as membership_type, p.membership_type_id,
            (select
                 count(1)
             from membership
             where location_id = {location_id} 
               and plan_id = p.id
               and membership_status_type_id <> {MembershipStatusEnum.CANCELLED.value}
            ) as member_count
        from plan p
                 left join plan_plan_type ppt on ppt.plan_id = p.id
                 left join _ref_plan_type pt on pt.id = ppt.plan_type_id
                 left join _ref_duration_type dt on dt.id = p.duration_type_id
                 left join _ref_billing_type bt on p.billing_type_id = bt.id
                 left join _ref_membership_type mt on mt.id = p.membership_type_id
                 left join class_access_group_plan cagp on cagp.plan_id = p.id
        where location_id = {location_id}
        group by location_id, p.id
        order by p.name asc;
        """
        result = db.session.execute(text(sql))
        results_as_dict = result.mappings().all()
        return results_as_dict

    @classmethod
    def find_by_location_and_plan(cls, location_id: int, plan_id: int) -> Optional[Self]:
        return cls.query.filter_by(location_id=location_id, id=plan_id).first()

    @classmethod
    def find_non_cancelled_plans_by_location_and_plan_name(cls, location_id: int, plan_name: str) -> Optional[Self]:
        return cls.query.filter(
            cls.location_id == location_id,
            cls.name == plan_name,
            func.lower(func.trim(cls.name)) == func.lower(func.trim(plan_name)),
            or_(
                cls.plan_status_type_id != PlanStatusType.CANCELLED.value,  # Exclude CANCELLED plans
                cls.plan_status_type_id.is_(None)  # Include NULL plan_status_type_id
            )
        ).first()

    @classmethod
    def find_by_location_and_plan_with_member_count(cls, location_id: int, plan_id: int) -> Optional[Self]:
        sql = f"""select p.*, (select count(1) from membership 
                             where location_id = {location_id} 
                               and plan_id = p.id
                               and membership_status_type_id <> {MembershipStatusEnum.CANCELLED.value}
                             ) as member_count
                  from plan p
                  where p.location_id = {location_id} and p.id = {plan_id}"""
        plan, member_count = db.session.query(Plan, Column("member_count")).from_statement(text(sql)).first()
        return plan, member_count

    @classmethod
    def find_by_location_and_plan_name(cls, location_id: int, plan_name: str) -> Optional[Self]:
        return cls.query.filter_by(location_id=location_id, name=plan_name).first()

    @classmethod
    def get_active_and_frozen_memberships(cls, location_id: int, plan_id: int) -> dict | None:
        sql = f"""
        select 
            coalesce(sum(
                case 
                    when m.membership_status_type_id = (
                        select rmst.id
                        from `_ref_membership_status_type` rmst
                        where rmst.name = "Active"
                    )
                    then 1
                    else 0
                end
            ),0) as active_member_count,
            coalesce(sum(
                case 
                    when m.membership_status_type_id = (
                        select rmst.id
                        from `_ref_membership_status_type` rmst
                        where rmst.name = "Frozen"
                    )
                    then 1
                    else 0
                end
            ),0) as frozen_member_count
        from membership m
        where m.plan_id = {plan_id}
            and m.location_id = {location_id};
        """
        result = db.session.execute(text(sql))
        results_as_dict = result.mappings().all()
        if results_as_dict is None:
            return None
        return results_as_dict[0]

    def save(self):
        db.session.add(self)

    def save_and_commit(self):
        self.save()
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
