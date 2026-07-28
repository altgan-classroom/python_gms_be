from datetime import datetime
from typing import Optional, Self, List

from sqlalchemy import (
    DateTime, Column, Integer, Boolean, ForeignKey, Float, BigInteger, text, Date, func, JSON, String, and_
)
from sqlalchemy import or_, select, outerjoin
from gmsshared import db
from gmsshared.src.models.user import User
from gmsshared.src.models.location import Location
from gmsshared.src.models.user_profile import UserProfile
from gmsshared.src.models.member_profile import MemberProfile
from gmsshared.src.models.plan import Plan
from gmsshared.src.util.enums import (
    RoleEnum,
    MembershipStatusEnum,
    PayrixOnboardStatusEnum,
    PayrixTransactionStatusEnum,
    BillingTypeEnum
)
from gmsshared.src.models._ref_freeze_reason_type import _RefFreezeReasonType
from gmsshared.src.models._ref_cancel_reason_type import _RefCancelReasonType
from gmsshared.src.models.membership_freeze import MembershipFreeze
from gmsshared.src.util.datetime_util import utc_now


class Membership(db.Model):
    id = Column(BigInteger, nullable=False, primary_key=True)
    location_id = Column(BigInteger, ForeignKey("location.id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("member_profile.user_id"), nullable=False)
    plan_id = Column(BigInteger, ForeignKey("plan.id"), nullable=False)
    signup_fee = Column(Float, nullable=True)
    plan_start_date = Column(Date, nullable=False)
    plan_end_date = Column(Date, nullable=True)
    auto_renewal = Column(Boolean, nullable=True)
    discount_percent_per_payment = Column(Float, nullable=True)
    discount_amount_per_payment = Column(Float, nullable=True)
    apply_discount_to_all_payments = Column(Boolean, nullable=True)
    membership_status_type_id = Column(Integer, nullable=False)
    salesperson_id = Column(BigInteger, nullable=True)
    sessions_count = Column(Integer, nullable=True)
    # After migration everyone to DEA, remove the freeze related fields. Moved them to membership_edit table
    freeze_from = Column(Date, nullable=True)
    freeze_to = Column(Date, nullable=True)
    freeze_reason_type_id = Column(Integer, ForeignKey("_ref_freeze_reason_type.id"), nullable=True)
    freeze_by = Column(BigInteger, nullable=True)
    freeze_date = Column(Date, nullable=True)
    unfreeze_date = Column(Date, nullable=True)
    unfreeze_by = Column(BigInteger, nullable=True)
    cancel_date = Column(Date, nullable=True)
    cancel_reason_type_id = Column(Integer, ForeignKey("_ref_cancel_reason_type.id"), nullable=True)
    cancelled_by = Column(BigInteger, nullable=True)
    cancelled_date = Column(DateTime, nullable=True)
    non_renewal = Column(Boolean, nullable=True)
    new_contract_value = Column(Float, nullable=True)
    renewal_count = Column(Integer, nullable=True)
    final_payment_date = Column(Date, nullable=True)
    split_payments = Column(JSON, nullable=True, default=None)
    cancel_description = Column(String(100), nullable=True, default=None)
    next_billing_date = Column(Date, nullable=True)
    next_billing_amount = Column(Float, nullable=True, default=0)
    apply_next_billing_date_to_all_invoices = Column(Boolean, nullable=True, default=0)
    previous_membership_id = Column(BigInteger, ForeignKey("membership.id"), nullable=True)

    plan = db.relationship(Plan)
    member = db.relationship(MemberProfile, backref="memberships")
    location = db.relationship(Location)
    freezes = db.relationship(MembershipFreeze, backref="membership")
    previous_membership = db.relationship('Membership', remote_side=[id], foreign_keys=[previous_membership_id])

    create_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(type_=DateTime, nullable=False, server_default=func.now(), onupdate=datetime.utcnow)

    def __init__(self, location_id, user_id: int, plan_id: int, plan_start_date: datetime.date, membership_status_type_id):
        self.location_id = location_id
        self.user_id = user_id
        self.plan_id = plan_id
        self.plan_start_date = plan_start_date
        self.membership_status_type_id = membership_status_type_id

    @classmethod
    def find_by_id(cls, location_id, member_id: int, _id: int) -> Optional[Self]:
        return cls.query.filter_by(location_id=location_id, user_id=member_id, id=_id).first()

    @classmethod
    def find_all_by_location(cls, location_id: int):
        return cls.query.filter(Membership.location_id == location_id,
                                Membership.membership_status_type_id != MembershipStatusEnum.ACTIVE.value).all()

    @classmethod
    def find_by_plan_id(cls, location_id, member_id: int, plan_id: int) -> List[Self]:
        return cls.query.filter_by(location_id=location_id, user_id=member_id, plan_id=plan_id).all()

    @classmethod
    def find_by_member_id(cls, location_id, member_id: int) -> List[Self]:
        return cls.query.filter_by(location_id=location_id, user_id=member_id).all()

    # TODO: Refactor this query to SQLAlchemy QL
    @classmethod
    def find_by_membership_id(cls, location_id: int, user_id: int, membership_id: int) -> Optional[Self]:
        sql = (f"""SELECT 
                mpl.id AS membership_id,
                u.id AS member_id,
                mp.location_id,
                mpl.plan_id,
                p.name AS plan_name,
                mpl.plan_start_date AS start_date,
                mpl.plan_end_date AS end_date,
                mpl.cancel_date,
                mpl.freeze_to,
                mpl.auto_renewal,
                mst.name AS member_status,
                pst.name AS plan_status,
                msst.name AS membership_status,
                mpl.sessions_count,
                (
                    SELECT GROUP_CONCAT(plan_type_id)
                    FROM plan_plan_type ppt
                    WHERE ppt.plan_id = mpl.plan_id
                ) AS plan_types,
                mpl.discount_percent_per_payment,
                mpl.discount_amount_per_payment,
                mpl.apply_discount_to_all_payments,
                mpl.split_payments,
                mpl.next_billing_date,
                mpl.next_billing_amount,
                mpl.apply_next_billing_date_to_all_invoices,
                CASE 
                    WHEN IFNULL(p.first_of_month, 0) = 1 THEN '1st of month'
                    ELSE CONCAT(p.recurring_interval, ' ', rec.name)
                END AS billing_interval,
                -- Past freezes
                (
                    SELECT JSON_ARRAYAGG(
                        JSON_OBJECT(
                            'freeze_from', freeze_from,
                            'freeze_to', COALESCE(unfreeze_date, freeze_to),
                            'freeze_reason_type_id', frt.id,
                            'freeze_id', mf2.id
                        )
                    )
                    FROM membership_freeze mf2
                    LEFT JOIN _ref_freeze_reason_type frt ON frt.id = mf2.freeze_reason_type_id
                    WHERE mf2.membership_id = mpl.id
                      AND (
                          (mf2.freeze_from < CURRENT_DATE AND mf2.freeze_to < CURRENT_DATE)
                          OR mf2.unfreeze_date IS NOT NULL
                      )
                ) AS past_freezes,
                -- Current freeze
                (
                    SELECT JSON_ARRAYAGG(
                        JSON_OBJECT(
                            'freeze_from', freeze_from,
                            'freeze_to', freeze_to,
                            'freeze_reason_type_id', frt.id,
                            'freeze_id', mf2.id
                        )
                    )
                    FROM membership_freeze mf2
                    LEFT JOIN _ref_freeze_reason_type frt ON frt.id = mf2.freeze_reason_type_id
                    WHERE mf2.membership_id = mpl.id
                      AND mf2.unfreeze_date IS NULL
                      AND CURDATE() BETWEEN mf2.freeze_from AND mf2.freeze_to
                ) AS current_freeze,
                -- Upcoming freeze
                (
                    SELECT JSON_ARRAYAGG(
                        JSON_OBJECT(
                            'freeze_id', mf2.id,
                            'freeze_from', mf2.freeze_from,
                            'freeze_to', mf2.freeze_to,
                            'freeze_reason_type_id', frt.id
                        )
                    )
                    FROM membership_freeze mf2
                    LEFT JOIN _ref_freeze_reason_type frt ON frt.id = mf2.freeze_reason_type_id
                    WHERE mf2.membership_id = mpl.id
                      AND mf2.unfreeze_date IS NULL
                      AND CURDATE() < mf2.freeze_from
                ) AS upcoming_freezes
            FROM member_profile mp
            JOIN membership mpl ON mp.user_id = mpl.user_id
            LEFT JOIN plan p ON p.id = mpl.plan_id
            LEFT JOIN _ref_member_status_type mst ON mst.id = mp.member_status_type_id
            LEFT JOIN _ref_plan_status_type pst ON pst.id = p.plan_status_type_id
            LEFT JOIN _ref_duration_type rec ON rec.id = p.recurring_duration_type_id
            LEFT JOIN _ref_membership_status_type msst ON msst.id = mpl.membership_status_type_id
            LEFT JOIN user u ON u.id = mp.user_id
            WHERE u.role_type_id = {RoleEnum.MEMBER.value}
              AND u.id = {user_id}
              AND mp.location_id = {location_id}
              AND mpl.id = {membership_id};
""")
        result = db.session.execute(text(sql))
        results_as_dict = result.mappings().first()
        return results_as_dict

    @classmethod
    def get_memberships_by_member_id(cls, location_id: int, user_id: int) -> List[Self]:
        sql = f"""with
         this_location as (
                    select l.id as location_id, rtt.iana_tzdata as timezone
                    from location l left join _ref_timezone_type rtt on rtt.id = l.timezone_type_id
                    where l.id = {location_id}
                ),
                     membership_intervals_converted as (
                         select
                             m.id as membership_id, m.user_id, m.location_id, m.plan_id, m.plan_start_date,
                             case
                                 when p.unlimited then 'Unlimited'
                                 when p.apply_weekly_registration_limits then concat('Weekly Limit: ', p.weekly_limit_times)
                                 when p.sessions_limit_times and p.sessions_limit_every then concat(p.sessions_limit_times, ' every ', p.sessions_limit_every, ' days')
                                 end as session_limits,
                             case
                                 when p.unlimited then null
                                 when p.apply_weekly_registration_limits then greatest(m.plan_start_date, date_sub(curdate(), interval ((dayofweek(curdate()) + 5) % 7) day))
                                 else date_add(m.plan_start_date, interval floor(datediff(curdate(), m.plan_start_date) / p.sessions_limit_every) * p.sessions_limit_every day)
                                 end as recent_interval_start_date,
                             case
                                 when p.unlimited then null
                                 when p.apply_weekly_registration_limits then date_add(curdate(), interval ((9 - dayofweek(curdate())) % 7) day)
                                 else date_add(m.plan_start_date, interval (floor(datediff(curdate(), m.plan_start_date) / p.sessions_limit_every) + 1) * p.sessions_limit_every day)
                                 end as next_interval_start_date,
                             convert_tz(
                                     concat(
                                             case
                                                 when p.unlimited then null
                                                 when p.apply_weekly_registration_limits then greatest(m.plan_start_date, date_sub(curdate(), interval ((dayofweek(curdate()) + 5) % 7) day))
                                                 else date_add(m.plan_start_date, interval floor(datediff(curdate(), m.plan_start_date) / p.sessions_limit_every) * p.sessions_limit_every day)
                                                 end,
                                             ' 00:00:00'
                                     ),
                                     '+00:00',
                                     (select timezone from this_location)
                             ) as recent_interval_local,
                             convert_tz(concat(date_sub(
                                     case
                                         when p.unlimited then null
                                         when p.apply_weekly_registration_limits then date_add(curdate(), interval ((9 - dayofweek(curdate())) % 7) day)
                                         else date_add(m.plan_start_date, interval (floor(datediff(curdate(), m.plan_start_date) / p.sessions_limit_every) + 1) * p.sessions_limit_every day)
                                         end,
                                     interval 1 day), ' 23:59:59'),'+00:00', (select timezone from this_location)) as next_interval_local
                         from membership m left join plan p on p.id = m.plan_id where m.user_id ={user_id} and m.location_id ={location_id}
                     ),
                     membership_session_info as (
                         select
                             mic.*,
                             count(
                                     case
                                         when mic.recent_interval_local is not null
                                             and mic.next_interval_local is not null
                                             and mc.id is not null
                                             then 1
                                         end
                             ) as sessions_attended
                         from membership_intervals_converted mic
                                  left join member_class mc
                                            on mc.membership_id = mic.membership_id
                                                and mc.no_show_credited = 0
                                                and mc.class_time between mic.recent_interval_local and mic.next_interval_local
                         group by mic.membership_id
                     ),
                     upcoming_freeze AS (
                        SELECT
                            mf.membership_id,
                            MIN(mf.freeze_from) AS next_freeze_date
                        FROM membership_freeze mf
                        WHERE mf.freeze_from > CURRENT_DATE
                        GROUP BY mf.membership_id
                    )
                    SELECT
                        mpl.id AS membership_id,
                        u.id AS member_id,
                        mp.location_id,
                        mpl.plan_id,
                        p.name AS plan_name,
                        mpl.plan_start_date AS start_date,
                        mpl.plan_end_date AS end_date,
                        mpl.cancel_date,
                        mpl.freeze_to,
                        mpl.auto_renewal,
                        mst.name AS member_status,
                        pst.name AS plan_status,
                        msst.name AS membership_status,
                        mpl.sessions_count,
                        CASE
                            WHEN l.class_access_group IS TRUE THEN
                                (
                                    SELECT GROUP_CONCAT(DISTINCT cagf.plan_type_id)
                                    FROM class_access_group_format cagf
                                    JOIN class_access_group cag ON cag.id = cagf.class_access_group_id
                                    JOIN class_access_group_plan cagp ON cagp.class_access_group_id = cag.id
                                    WHERE cagp.plan_id = mpl.plan_id and cag.active = 1
                                )
                            ELSE
                                (
                                    SELECT GROUP_CONCAT(DISTINCT ppt.plan_type_id)
                                    FROM plan_plan_type ppt
                                    WHERE ppt.plan_id = mpl.plan_id
                                )
                        END AS plan_types,
                        cast((select json_arrayagg(
                                       json_object(
                                               'name', cag.name,
                                               'active', cag.active
                                       )
                               )
                            from class_access_group cag
                                     join class_access_group_plan cagp on cagp.class_access_group_id = cag.id
                                     join plan p2 on cagp.plan_id = p2.id
                            where p2.id = mpl.plan_id
                        )as json) as class_access_groups,
                        mpl.discount_percent_per_payment,
                        mpl.discount_amount_per_payment,
                        mpl.apply_discount_to_all_payments,
                        mpl.split_payments,
                        mpl.next_billing_date,
                        mpl.next_billing_amount,
                        mpl.apply_next_billing_date_to_all_invoices,
                        CASE
                            WHEN IFNULL(p.first_of_month, 0) = 1 THEN '1st of month'
                            ELSE CONCAT(p.recurring_interval, ' ', rec.name)
                            END AS billing_interval,
                        (
                            SELECT t.action_date
                            FROM (
                                 SELECT uf.next_freeze_date AS action_date, 1 AS action_type_id
                                 UNION ALL
                                 SELECT CASE WHEN p.billing_type_id = 3 THEN NULL ELSE mpl.cancel_date END AS action_date, 2 AS action_type_id
                                 UNION ALL
                                 SELECT CASE
                                            WHEN p.billing_type_id = 3 THEN NULL
                                            WHEN mpl.auto_renewal THEN DATE_ADD(mpl.plan_end_date, INTERVAL 1 DAY)
                                            ELSE NULL
                                            END AS action_date, 3 AS action_type_id
                                 UNION ALL
                                 SELECT CASE
                                            WHEN p.billing_type_id = 3 THEN NULL
                                            WHEN NOT mpl.auto_renewal THEN mpl.plan_end_date
                                            ELSE NULL
                                            END AS action_date, 4 AS action_type_id
                             ) AS t
                            WHERE t.action_date IS NOT NULL
                            ORDER BY t.action_date
                            LIMIT 1
                        ) AS next_action_date,

                        (
                            SELECT t.action_type_id
                            FROM (
                                 SELECT uf.next_freeze_date AS action_date, 1 AS action_type_id
                                 UNION ALL
                                 SELECT CASE WHEN p.billing_type_id = 3 THEN NULL ELSE mpl.cancel_date END AS action_date, 2 AS action_type_id
                                 UNION ALL
                                 SELECT CASE
                                            WHEN p.billing_type_id = 3 THEN NULL
                                            WHEN mpl.auto_renewal THEN DATE_ADD(mpl.plan_end_date, INTERVAL 1 DAY)
                                            ELSE NULL
                                            END AS action_date, 3 AS action_type_id
                                 UNION ALL
                                 SELECT CASE
                                            WHEN p.billing_type_id = 3 THEN NULL
                                            WHEN NOT mpl.auto_renewal THEN mpl.plan_end_date
                                            ELSE NULL
                                            END AS action_date, 4 AS action_type_id
                             ) AS t
                        WHERE t.action_date IS NOT NULL
                        ORDER BY t.action_date
                        LIMIT 1
                        ) AS next_action_type_id,
                        msi.session_limits as session_limits,
                        msi.next_interval_start_date as session_limits_reset_on,
                        p.sessions_limit_times - msi.sessions_attended  as sessions_remaining

                    FROM member_profile mp
                             JOIN membership mpl ON mp.user_id = mpl.user_id
                             LEFT JOIN plan p ON p.id = mpl.plan_id
                             LEFT JOIN _ref_member_status_type mst ON mst.id = mp.member_status_type_id
                             LEFT JOIN _ref_plan_status_type pst ON pst.id = p.plan_status_type_id
                             LEFT JOIN _ref_duration_type rec ON rec.id = p.recurring_duration_type_id
                             LEFT JOIN _ref_membership_status_type msst ON msst.id = mpl.membership_status_type_id
                             LEFT JOIN user u ON u.id = mp.user_id
                             LEFT JOIN upcoming_freeze uf ON uf.membership_id = mpl.id
                             LEFT JOIN location l on l.id = mpl.location_id
                             LEFT JOIN membership_session_info msi on msi.membership_id = mpl.id
                    WHERE
                        u.role_type_id = 6
                      AND u.id = {user_id}
                      AND mp.location_id = {location_id}
                      AND mpl.membership_status_type_id <> 4

                    ORDER BY
                        FIELD(msst.name, 'Active', 'Frozen', 'Cancelled'),
                        p.name"""
        result = db.session.execute(text(sql))
        results_as_dict = result.mappings().all()
        return results_as_dict

    @classmethod
    def find_all_memberships_by_member_id(cls, location_id, user_id: int) -> List[Self]:
        return cls.query.filter(and_(cls.location_id == location_id, cls.user_id == user_id,
                                     cls.membership_status_type_id == MembershipStatusEnum.ACTIVE.value,
                                     cls.cancelled_date.is_(None), cls.plan_end_date >= utc_now().date())).all()

    @classmethod
    def find_all_memberships_by_location_id(cls, location_id):
        return cls.query.filter(and_(cls.location_id == location_id,
                                     cls.membership_status_type_id.notin_([
                                         MembershipStatusEnum.CANCELLED.value,
                                         MembershipStatusEnum.RENEWED.value
                                     ]),
                                     cls.cancelled_date.is_(None), cls.plan_end_date >= utc_now().date())).all()

    @classmethod
    def find_all_members_by_location(cls, location_id: int, query):
        from gmsshared.src.models.member_class import MemberClass
        from gmsshared.src.models.user import User
        stmt = (
            select(cls, MemberClass, User.id, User.email, UserProfile.first_name, UserProfile.last_name, UserProfile.phone_number, UserProfile.photo_url)
            .select_from(Membership)
            .outerjoin(MemberClass, Membership.id == MemberClass.membership_id)
            .outerjoin(MemberProfile, Membership.user_id == MemberProfile.user_id)
            .outerjoin(User, MemberProfile.user_id == User.id)
            .outerjoin(UserProfile, User.id == UserProfile.user_id)
            .filter(Membership.location_id == location_id)
        )

        if query.name:
            name_parts = query.name.split()
            if len(name_parts) == 1:
                stmt = stmt.filter(
                    or_(
                        UserProfile.first_name.ilike(f"%{query.name}%"),
                        UserProfile.last_name.ilike(f"%{query.name}%")
                    )
                )
            elif len(name_parts) > 1:
                stmt = stmt.filter(
                    *[
                        or_(
                            UserProfile.first_name.ilike(f"%{part}%"),
                            UserProfile.last_name.ilike(f"%{part}%")
                        ) for part in name_parts
                    ],
                )
        elif query.member_id:
            stmt = stmt.filter(User.id == query.member_id)
        return Membership.query.session.execute(stmt).all()

    @classmethod
    def get_next_scheduled_payment(cls, location_id: int, user_id: int, membership_id: int) -> List[Self]:
        sql = (f"""select cast(scheduled_date as date) as scheduled_date 
                 from member_payment_schedule 
                 where location_id = {location_id} and user_id = {user_id} and membership_id = {membership_id} 
                     and payrix_onboarding_status in ({PayrixOnboardStatusEnum.NOT_READY.value}) 
                 order by payment_number limit 1""")
        result = db.session.execute(text(sql))
        results_as_dict = result.mappings().all()
        return results_as_dict

    @classmethod
    def delete_upcoming_payments(cls, location_id: int, user_id: int, membership_id: int) -> None:
        sql = (f"""delete from member_payment_schedule 
                 where location_id = {location_id} and user_id = {user_id} and membership_id = {membership_id} 
                     and payrix_onboarding_status in ({PayrixOnboardStatusEnum.NOT_READY.value})""")
        db.session.execute(text(sql))
        db.session.commit()

    @classmethod
    def get_last_scheduled_payment(cls, location_id: int, user_id: int, membership_id: int) -> List[Self]:
        sql = (f"""select cast(scheduled_date as date) as scheduled_date 
                 from member_payment_schedule 
                 where location_id = {location_id} and user_id = {user_id} and membership_id = {membership_id} 
                     and payrix_onboarding_status in ({PayrixOnboardStatusEnum.NOT_READY.value}) 
                 order by id desc limit 1""")
        result = db.session.execute(text(sql))
        results_as_dict = result.mappings().all()
        return results_as_dict

    @classmethod
    def get_last_payment(cls, location_id: int, user_id: int, membership_id: int) -> List[Self]:
        sql = (f"""select cast(processed_date as date) as scheduled_date 
                 from member_payment_history 
                 where location_id = {location_id} and user_id = {user_id} and membership_id = {membership_id} 
                     and member_payment_history.payrix_transaction_status not in ({PayrixTransactionStatusEnum.FAILED.value}) 
                 order by id desc limit 1""")
        result = db.session.execute(text(sql))
        results_as_dict = result.mappings().all()
        return results_as_dict

    @classmethod
    def find_frozen_memberships(cls) -> List[Self]:
        return cls.query.filter(Membership.membership_status_type_id==MembershipStatusEnum.FROZEN.value,
                                Membership.freeze_to < datetime.today().utcnow().date()).all()

    @classmethod
    def find_active_memberships(cls, location_id: int, user_id: int) -> List[Self]:
        return cls.query.filter(
            cls.location_id == location_id,
            cls.user_id == user_id,
            cls.membership_status_type_id.in_([
                MembershipStatusEnum.FROZEN.value,
                MembershipStatusEnum.ACTIVE.value
            ])
        ).all()

    @classmethod
    def find_to_be_frozen_memberships(cls) -> List[Self]:
        return cls.query.filter(Membership.membership_status_type_id==MembershipStatusEnum.ACTIVE.value,
                                Membership.freeze_from <= datetime.today().utcnow().date()).all()

    @classmethod
    def find_cancel_memberships(cls) -> List[Self]:
        sql = f"""select * from membership m 
                  where (m.membership_status_type_id not in ({MembershipStatusEnum.CANCELLED.value}, {MembershipStatusEnum.RENEWED.value}) 
                      and m.plan_end_date < cast(now() as date) and auto_renewal = 0)
                      or (m.membership_status_type_id = {MembershipStatusEnum.ACTIVE.value} and m.cancel_date <= cast(now() as date))"""
        return cls.query.from_statement(text(sql)).all()

    @classmethod
    def find_renewal_memberships(cls) -> List[Self]:
        return cls.query.filter(Membership.membership_status_type_id == MembershipStatusEnum.ACTIVE.value,
                                Membership.plan_end_date < utc_now().date(),
                                Membership.auto_renewal == 1).all()

    @classmethod
    def find_renewal_session_pack_memberships(cls) -> List[Self]:
        return db.session.query(Membership).join(Plan).filter(Membership.membership_status_type_id == MembershipStatusEnum.ACTIVE.value,
                                Membership.sessions_count <= 0, Plan.billing_type_id == BillingTypeEnum.SESSION_PACKS.value,
                                Membership.auto_renewal == 1).all()

    def update_ncv_final_payment_date(self, membership_id: str):
        sql = (f"""update membership mem left join plan p on mem.plan_id = p.id set mem.new_contract_value = (select sum(total_amount) from member_payment_schedule_temp
                                 where location_id = mem.location_id and user_id = mem.user_id and membership_id = '{membership_id}'),
                        mem.final_payment_date = if(p.billing_type_id = {BillingTypeEnum.RECURRING.value}, (select scheduled_date from member_payment_schedule_temp mps
                                 where location_id = mem.location_id and user_id = mem.user_id and membership_id = '{membership_id}'
                                 order by mps.payment_number desc limit 1), null)
                where mem.location_id = {self.location_id} and mem.user_id = {self.user_id} and mem.id = {self.id}""")
        db.session.execute(text(sql))
        db.session.commit()

    def update_final_payment_date(self, renewal_count: int = 0):
        sql = (f"""update membership mem left join plan p on mem.plan_id = p.id 
                      set mem.final_payment_date = if(p.billing_type_id = {BillingTypeEnum.RECURRING.value},
                                (select scheduled_date from member_payment_schedule mps
                                 where location_id = mem.location_id and user_id = mem.user_id and membership_id = {self.id}
                                     and mps.renewal_count = {renewal_count}
                                 order by mps.payment_number desc limit 1), null)
                where mem.location_id = {self.location_id} and mem.user_id = {self.user_id} and mem.id = {self.id}""")
        db.session.execute(text(sql))
        db.session.commit()

    @classmethod
    def find_not_started_memberships(cls):
        return cls.query.filter(cls.membership_status_type_id == MembershipStatusEnum.NOT_STARTED.value, cls.plan_start_date <= utc_now().date()).all()

    @classmethod
    def find_active_memberships_by_plans(cls, location_id: int, plans: List[int]) -> List[Self]:
        return (
            cls.query
            .filter(
                cls.location_id == location_id,
                cls.plan_id.in_(plans),
                cls.membership_status_type_id == MembershipStatusEnum.ACTIVE.value
            )
            .all()
        )

    @classmethod
    def session_activity_history(self, location_id: int, user_id: int, membership_id: int):
        sql = f"""
                WITH session_activity_data AS (
                    SELECT
                        mc.membership_id AS membership_id,
                        mc.class_time AS activity_date,
                        c.name AS activity_name,
                        CASE
                            WHEN mc.member_cancelled_time IS NOT NULL THEN 4
                            WHEN mc.member_checked_in_time IS NOT NULL THEN 3
                            WHEN mc.class_time < NOW() THEN 6
                            ELSE 5
                            END AS activity_type_id,
                        CASE
                            WHEN p.billing_type_id = 3 THEN
                                CASE
                                    WHEN mc.member_cancelled_time IS NOT NULL AND mc.no_show_credited = 1 THEN 0
                                    WHEN mc.class_time < NOW() AND mc.no_show_credited = 1 AND mc.member_checked_in_time IS NULL THEN 0
                                    WHEN mc.member_cancelled_time IS NOT NULL AND mc.no_show_credited = 0 THEN -1
                                    WHEN mc.member_checked_in_time IS NOT NULL AND mc.class_time >= NOW() AND mc.member_cancelled_time IS NULL THEN -1
                                    ELSE -1
                                    END
                            WHEN p.billing_type_id != 3 THEN NULL
                            END AS session_count,
                        CASE
                            WHEN (mc.member_cancelled_time IS NOT NULL AND mc.no_show_credited = 1)
                                OR (mc.class_time < NOW() AND mc.no_show_credited = 1 AND mc.member_checked_in_time IS NULL)
                                THEN '1 session credited back'
                            ELSE ''
                            END AS activity_description
                    FROM member_class mc
                             LEFT JOIN class c ON mc.class_id = c.id
                             LEFT JOIN membership m ON mc.membership_id = m.id
                             LEFT JOIN plan p ON m.plan_id = p.id
                    WHERE mc.location_id = {location_id} AND mc.user_id = {user_id} AND m.id = {membership_id}
                
                    UNION ALL
                
                    SELECT
                        ms.membership_id AS membership_id,
                        ms.sessions_purchase_date AS activity_date,
                        CONCAT(
                                ABS(ms.sessions_count),
                                ' ',
                                CASE
                                    WHEN ms.sessions_count < 0 AND ABS(ms.sessions_count) = 1 THEN 'session removed'
                                    WHEN ms.sessions_count < 0 THEN 'sessions removed'
                                    WHEN ms.sessions_count = 1 THEN 'session added'
                                    ELSE 'sessions added'
                                    END
                        ) AS activity_name,
                        CASE
                            WHEN ms.sessions_count > 0 THEN 1
                            WHEN ms.sessions_count < 0 THEN 2
                            END AS activity_type_id,
                        ABS(ms.sessions_count) AS session_count,
                        '' AS activity_description             
                    FROM membership_session ms
                    WHERE ms.location_id = {location_id} AND ms.user_id = {user_id} AND ms.membership_id = {membership_id}
                ),
                     ordered_data AS (
                         SELECT *
                         FROM session_activity_data
                         ORDER BY activity_date ASC
                     ),
                     with_balance AS (
                         SELECT
                             membership_id,
                             activity_date,
                             activity_name,
                             activity_description,
                             activity_type_id,
                             session_count,
                             SUM(
                                     CASE
                                         WHEN activity_type_id = 2 THEN -session_count
                                         ELSE session_count
                                         END
                             ) OVER (
                                         PARTITION BY membership_id
                                         ORDER BY activity_date ASC
                                         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                                         ) AS balance
                         FROM ordered_data
                     )
                SELECT *
                FROM with_balance
                ORDER BY activity_date;
                """
        result = db.session.execute(text(sql))
        results_as_dict = result.mappings().all()
        return results_as_dict

    def save(self):
        db.session.add(self)

    def save_and_commit(self):
        self.save()
        db.session.commit()