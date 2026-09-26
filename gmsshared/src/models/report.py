from datetime import datetime, timedelta
from typing import List, Optional, Self

from sqlalchemy import text, Column, BigInteger, ForeignKey, Integer, String, Boolean, DateTime, func
from sqlalchemy.sql.elements import TextClause

from gmsshared.src.util.enums import PaymentTransactionTypeEnum
from gmsshared.src.util.enums import PayrixTransactionStatusEnum
from gmsshared.src.util.validators import date_input_validator
from gmsshared.src.util.validators import to_utc
from gmsshared import db
from gmsshared.src.models.location import Location
from gmsshared.src.models._ref_role_type import _RefRoleType
from gmsshared.src.models.user import User


report_role = db.Table(
    "report_role",
    db.Model.metadata,
    Column("report_id", BigInteger, ForeignKey("report.id"), primary_key=True),
    Column("role_type_id", Integer, ForeignKey("_ref_role_type.id"), primary_key=True)
)


class Report(db.Model):
    id = Column(BigInteger, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(200), nullable=True)
    dashboard_id = Column(String(100), nullable=False)
    sheet_id = Column(String(100), nullable=False)
    visual_id = Column(String(100), nullable=False)
    environment = Column(String(5), nullable=False)
    active = Column(Boolean, nullable=False, default=True)

    create_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(type_=DateTime, nullable=False, server_default=func.now(), onupdate=datetime.utcnow)

    # Define the many-to-many relationship
    roles = db.relationship(
        "_RefRoleType",
        secondary=report_role,
        backref=db.backref("reports", lazy="dynamic")
    )

    @classmethod
    def find_by_id(cls, environment: str, id: int) -> Optional[Self]:
        return cls.query.filter_by(environment=environment, id=id).first()

    @classmethod
    def find_by_user(cls, environment: str, user_id: int) -> Optional[List[Self]]:
        return (
            cls.query
            # Join with the roles relationship
            .join(cls.roles)
            # Join with the User table to get the user role
            .join(User, User.role_type_id == _RefRoleType.id)
            .filter(
                cls.environment == environment,
                User.id == user_id
            )
            .all()
        )

    @classmethod
    def new_contacts(cls, location_id: int, from_date: datetime, to_date: datetime) -> List[dict]:
        result = db.session.execute(Report._new_contacts_query(location_id, from_date, to_date))
        dictionaries_list = Report._map_results(result)
        return Report._clean_dates(dictionaries_list)

    @classmethod
    def new_contacts_filter(cls, location_id: int, from_date: datetime, to_date: datetime, nc_filter: dict) -> List[dict]:
        result = db.session.execute(Report._new_contacts_query(location_id, from_date, to_date))
        dictionaries_list = Report._map_results(result)
        filtered_list = Report._filter_results(dictionaries_list, nc_filter)
        return Report._clean_dates(filtered_list)

    @classmethod
    def new_membership_sales(cls, location_id: int, from_date: datetime, to_date: datetime):
        result = db.session.execute(Report._new_sales_query(location_id, from_date, to_date))
        dictionaries_list = Report._map_results(result)
        return dictionaries_list

    @classmethod
    def new_membership_sales_filter(cls, location_id: int, from_date: datetime, to_date: datetime, ns_filter: dict)  -> List[dict]:

        result = db.session.execute(Report._new_sales_query(location_id, from_date, to_date))
        dictionaries_list = Report._map_results(result)
        return Report._filter_results(dictionaries_list, ns_filter)

    @classmethod
    def contact_attendance(cls, location_id: int, from_date: datetime, to_date: datetime | None = None):
        result = db.session.execute(Report._contact_attendance_query(location_id, from_date, to_date))
        dictionaries_list = Report._map_results(result)
        return dictionaries_list

    @classmethod
    def contact_attendance_filter(cls, location_id: int, from_date: datetime, ns_filter: dict,
                                  to_date: datetime | None = None) -> List[dict]:
        user_id: int | None = ns_filter.get("member_id", None)
        result = db.session.execute(Report._contact_attendance_query(location_id, from_date, to_date, user_id))
        dictionaries_list = Report._map_results(result)
        contact_filter_map: dict = {
            "member_id": "member_id",
            "session_year": "year",
            "month": "session_month",
            "attended_sessions": ns_filter.get("attended", None),
            "attended": "cancelled_sessions",
            "no_shows": "no_show_sessions",
        }
        serialized_filter: dict = {}
        for k, v in ns_filter.items():
            if k in contact_filter_map.keys():
                serialized_filter[contact_filter_map[k]] = v
        return Report._filter_results(dictionaries_list, serialized_filter)

    @classmethod
    def member_sessions_attendance_report(cls, location_id: int, user_id: int | None = None) -> List[dict]:
        result = db.session.execute(Report._member_sessions_attendance_query(location_id, user_id))
        dictionaries_list = Report._map_results(result)
        return dictionaries_list

    @classmethod
    def member_sessions_attendance_report_filter(cls, location_id: int, msa_filter: dict) -> List[dict]:
        result = db.session.execute(Report._member_sessions_attendance_query(location_id))
        dictionaries_list = Report._map_results(result)
        return Report._filter_results(dictionaries_list, msa_filter)

    @classmethod
    def contact_attendance_history(cls,
                                   location_id: int, member_id: int,
                                   from_date: datetime, to_date: datetime) -> List[dict]:
        result = db.session.execute(Report._contact_attendance_history_query(location_id, member_id, from_date, to_date))
        dictionaries_list = Report._map_results(result)
        return dictionaries_list

    @classmethod
    def at_risk_attendance_report(cls, location_id: int, from_date: datetime) -> List[dict]:
        result = db.session.execute(Report._at_risk_attendance_query(location_id, from_date))
        dictionaries_list = Report._map_results(result)
        return Report._clean_dates(dictionaries_list)

    @classmethod
    def at_risk_attendance_reports_filter(cls, location_id: int, from_date: datetime, ara_filter: dict) -> List[dict]:
        result = db.session.execute(Report._at_risk_attendance_query(location_id, from_date))
        dictionaries_list = Report._map_results(result)
        filtered_list = Report._filter_results(dictionaries_list, ara_filter)
        return Report._clean_dates(filtered_list)

    @classmethod
    def location_membership_type_count_report(cls, location_id: int) -> List[dict]:
        result = db.session.execute(Report._location_membership_type_count_query(location_id))
        dictionaries_list = Report._map_results(result)
        return dictionaries_list

    @classmethod
    def location_timezone(cls, location_id: int) -> str:
        result = db.session.execute(Report._location_timezone_query(location_id))
        timezone = result.first()[0]
        return timezone

    @classmethod
    def member_payment_history_report(cls, location_id: int, from_date: datetime, to_date: datetime) -> List[dict]:
        result = db.session.execute(Report._member_payment_history_query(location_id, from_date, to_date))
        dictionaries_list = Report._map_results(result)
        return dictionaries_list

    @classmethod
    def payment_history_report_v2(cls, location_id: int, from_date: datetime, to_date: datetime) -> List[dict]:
        result = db.session.execute(Report._payment_history_query_v2(location_id, from_date, to_date))
        dictionaries_list = Report._map_results(result)
        return dictionaries_list

    @classmethod
    def invoice_history_report(cls, location_id: int, from_date: datetime, to_date: datetime) -> List[dict]:
        result = db.session.execute(Report._invoice_query(location_id, from_date, to_date))
        dictionaries_list = Report._map_results(result)
        return dictionaries_list

    @classmethod
    def member_payment_schedule_report(cls, location_id: int, from_date: datetime, to_date: datetime) -> List[dict]:
        result = db.session.execute(Report._member_payment_schedule_query(location_id, from_date, to_date))
        dictionaries_list = Report._map_results(result)
        return dictionaries_list

    @classmethod
    def balance_and_future_contract_value_report(cls, location_id: int) -> List[dict]:
        result = db.session.execute(Report._balance_and_future_contract_value_query(location_id))
        dictionaries_list = Report._map_results(result)
        return dictionaries_list

    @classmethod
    def balance_and_future_contract_value_report_filter(cls, location_id: int, bfcv_filter: dict) -> List[dict]:
        result = db.session.execute(Report._balance_and_future_contract_value_query(location_id))
        dictionaries_list = Report._map_results(result)
        return Report._filter_results(dictionaries_list, bfcv_filter)

    @classmethod
    def recurring_member_churn_report(cls, location_id: int, from_date: datetime, to_date: datetime) -> List[dict]:
        result = db.session.execute(Report._recurring_member_churn_query(location_id, from_date, to_date))
        dictionaries_list = Report._map_results(result)
        return dictionaries_list

    @classmethod
    def recurring_member_churn_report_filter(cls, location_id: int, from_date: datetime, to_date: datetime, rmc_filter: dict) -> List[dict]:
        result = db.session.execute(Report._recurring_member_churn_query(location_id, from_date, to_date))
        dictionaries_list = Report._map_results(result)
        return Report._filter_results(dictionaries_list, rmc_filter)

    @classmethod
    def challenge_conversions_cohort_detail_report(
            cls, location_id: int, from_date: datetime | None = None, to_date: datetime | None = None) -> List[dict]:
        result = db.session.execute(Report._challenge_conversions_cohort_detail_query(location_id, from_date, to_date))
        dictionaries_list = Report._map_results(result)
        return dictionaries_list

    @classmethod
    def challenge_conversions_cohort_detail_report_filter(
            cls, location_id: int, cccd_filter: dict, from_date: datetime | None = None, to_date: datetime | None = None) -> List[dict]:
        result = db.session.execute(Report._challenge_conversions_cohort_detail_query(location_id, from_date, to_date))
        dictionaries_list = Report._map_results(result)
        return Report._filter_results(dictionaries_list, cccd_filter)

    @classmethod
    def challenge_conversions_cohort_summary_report(
            cls, location_id: int, from_date: datetime | None = None, to_date: datetime | None = None) -> List[dict]:
        result = db.session.execute(Report._challenge_conversions_cohort_summary_query(location_id, from_date, to_date))
        dictionaries_list = Report._map_results(result)
        return dictionaries_list

    @classmethod
    def challenge_conversions_cohort_summary_report_filter(
            cls, location_id: int, cccd_filter: dict, from_date: datetime | None = None, to_date: datetime | None = None) -> List[dict]:
        result = db.session.execute(Report._challenge_conversions_cohort_summary_query(location_id, from_date, to_date))
        dictionaries_list = Report._map_results(result)
        return Report._filter_results(dictionaries_list, cccd_filter)

    @staticmethod
    def _new_contacts_query(location_id: int, from_date: datetime, to_date: datetime) -> TextClause:
        sql = f"""select distinct
                    u.id as user_id,
                    ul.location_id as location_id,
                    u.role_type_id as contact_type,
                    concat(up.first_name, ' ', up.last_name) as name,
                    u.create_datetime as date_added,
                    case when (rrt.name = 'Member' and m.plan_id is not null) then m.plan_start_date else '-' end as start_date,
                    case when m.plan_id is null then '-' else m.plan_id end as plan_id
                    from user u
                    join user_profile up on u.id = up.user_id
                    join user_location ul on ul.user_id = u.id and ul.location_id = {location_id}
                    left join membership m on u.id = m.user_id
                    join _ref_role_type rrt on u.role_type_id = rrt.id
                    where u.create_datetime >= '{from_date}' and u.create_datetime <= '{to_date}'
                    order by date_added;"""
        return text(sql)

    @staticmethod
    def _new_sales_query(location_id: int, from_date: datetime, to_date: datetime) -> TextClause:
        delta: timedelta = to_date - from_date
        if delta.days <= 0:
            from_date = to_date - timedelta(days=1)
        sql = f"""
            select 
                p.name as plan_name,
                rbt.name as billing_type,
                count(1) as number_of_new_sales,
                coalesce(round(sum(mph.total_amount),2),0) as fecc, 
                coalesce(round(sum(m.new_contract_value),2),0) as new_contract_value_added
            from member_payment_history mph
            join membership m 
                on mph.membership_id = m.id
            join plan p
                on p.id = m.plan_id
            join `_ref_billing_type` rbt
                on rbt.id = p.billing_type_id
            where 
                mph.payment_number = 1
                and mph.payrix_transaction_status in (
                    select rptst.id
                    from `_ref_payrix_transaction_status_type` rptst
                    where rptst.name in ("Approved", "Captured", "Settled")
                )
                and mph.payment_transaction_type in (
                    select rptt.id 
                    from `_ref_payment_transaction_type` rptt
                    where rptt.name in ("Sale Transaction", "Refund Transaction")
                )
                and mph.location_id = {location_id}
                and mph.processed_date 
                    between '{from_date}' 
                        and '{to_date}'
            group by p.name, p.billing_type_id
            order by p.name, p.billing_type_id;
            """
        return text(sql)

    @staticmethod
    def _contact_attendance_query(
            location_id: int, from_date: datetime, to_date: datetime | None = None,
            user_id: int | None = None) -> TextClause:

        year_subquery: str = ""
        user_subquery: str = ""

        if from_date is not None and to_date is None:
            year_subquery = f"and year(COALESCE(combined.class_time, combined.member_checked_in_time)) = {date_input_validator(from_date).year}"
        elif from_date is not None and to_date is not None:
            year_subquery = f"and year(COALESCE(combined.class_time, combined.member_checked_in_time)) >= {date_input_validator(from_date).year} \
                and year(COALESCE(combined.class_time, combined.member_checked_in_time)) <= {date_input_validator(to_date).year}"

        if user_id is not None:
            user_subquery = f"and combined.user_id = {user_id}"

        sql = f"""
            select  sum(
                    case when combined.member_checked_in_time is not null 
                        and combined.member_cancelled_time is null then 1 else 0 end) 
                            as attended_sessions,
                    sum(case when combined.member_cancelled_time is not null then 1 else 0 end) 
                        as cancelled_sessions,
                    sum(case when combined.member_checked_in_time is null 
                        and combined.member_cancelled_time is null then 1 else 0 end) 
                            as no_show_sessions,
                    month(COALESCE(combined.class_time, combined.member_checked_in_time)) as session_month,
                    year(COALESCE(combined.class_time, combined.member_checked_in_time)) as session_year,
                    combined.user_id as member_id
            from (select user_id, location_id, class_time, member_checked_in_time, member_cancelled_time from member_class union all 
                  select  user_id, location_id, class_time, member_checked_in_time, member_cancelled_time from member_opengym) as combined
            where combined.location_id = {location_id}
                {year_subquery}
                {user_subquery}
            group by session_month, session_year, member_id
        """
        return text(sql)

    @staticmethod
    def _member_sessions_attendance_query(
            location_id: int,
            user_id: int | None = None) -> TextClause:

        user_query = f"and mc.user_id = {user_id}" if user_id is not None else ""

        sql = f"""
            with combined_data as (
                select user_id, class_time, member_checked_in_time, member_cancelled_time, location_id, class_id from member_class
                union all
                select user_id, class_time, member_checked_in_time, member_cancelled_time, location_id, null as class_id from member_opengym
            )
            select mc.user_id as member_id, 
                   max(mc.member_checked_in_time) as last_visit_date,
                   (select coalesce(c.name, 'Opengym Checkin') 
                    from combined_data mc1 
                    left join class c on c.id = mc1.class_id 
                    where mc1.member_checked_in_time = max(mc.member_checked_in_time) and mc1.user_id = mc.user_id limit 1) as last_visit_session_name,
                   min(case when mc.class_time > now() and mc.member_checked_in_time is null then mc.class_time end) as next_scheduled_session_date,
                   (select coalesce(c.name, 'opengym checkin') 
                    from combined_data mc2 
                    left join class c on c.id = mc2.class_id 
                    where mc2.class_time = (select min(mc3.class_time) 
                                            from combined_data mc3 
                                            where mc3.class_time > now() and mc3.member_checked_in_time is null and mc3.user_id = mc.user_id) 
                    and mc2.user_id = mc.user_id limit 1) as next_scheduled_session_name,
                   count(if(mc.member_checked_in_time is not null and mc.member_cancelled_time is null, 1, null)) as total_sessions_attended
            from combined_data mc
            where mc.location_id = {location_id} {user_query}
            group by mc.user_id
            order by mc.user_id;
        """

        return text(sql)

    @staticmethod
    def _contact_attendance_history_query(
            location_id: int, member_id: int,
            from_date: datetime, to_date: datetime) -> TextClause:
        sql = f"""
                SELECT 
                    mc.class_time AS session_date,
                    c.name AS session_name,
                    CASE
                        WHEN mc.member_checked_in_time IS NOT NULL THEN 'Attended'
                        WHEN mc.member_cancelled_time IS NOT NULL THEN 'Cancelled'
                        WHEN mc.class_time < NOW() THEN 'No Showed'
                        ELSE 'Booked'
                    END AS attendance_status
                FROM 
                    member_class mc
                JOIN 
                    class c ON c.id = mc.class_id
                WHERE 
                    mc.location_id = {location_id}
                    AND mc.user_id = {member_id}
                    AND mc.class_time >= '{from_date}'
                    AND mc.class_time <= '{to_date}'

                UNION ALL

                SELECT 
                    mo.member_checked_in_time AS session_date,
                    'OpenGym' AS session_name,
                    'Attended' AS attendance_status
                FROM 
                    member_opengym mo
                WHERE 
                    mo.location_id = {location_id}
                    AND mo.user_id = {member_id}
                    AND mo.member_checked_in_time IS NOT NULL

                ORDER BY 
                    session_date DESC;
            """
        return text(sql)

    @staticmethod
    def _location_membership_type_count_query(location_id: int) -> TextClause:
        sql = f"""
               select 
                (select count(distinct(m.user_id))
                from membership m
                inner join plan p on p.id = m.plan_id
                where p.membership_type_id = (
                    select rmt.id 
                    from `_ref_membership_type` rmt
                    where rmt.name = "Full Membership")
                and m.membership_status_type_id = (
                    select rmst.id 
                    from `_ref_membership_status_type` rmst
                    where rmst.name = "Active")
                and m.location_id = {location_id}) as full_members,
                
                (select count(distinct(m.user_id))
                from membership m
                join plan p 
                    on m.plan_id = p.id
                where m.location_id = {location_id}
                    and p.membership_type_id = (
                        select rmt.id 
                        from `_ref_membership_type` rmt
                        where rmt.name = "Challenge")
                    and m.membership_status_type_id = (
                        select rmst.id 
                        from `_ref_membership_status_type` rmst
                        where rmst.name = "Active")
                    and (m.user_id not in (
                            select m2.user_id
                            from membership m2
                            join plan p2 
                                on m2.plan_id = p2.id
                            where m2.location_id = {location_id}
                            and p2.membership_type_id = (
                                select rmt.id 
                                from `_ref_membership_type` rmt
                                where rmt.name = "Full Membership")
                            and m2.membership_status_type_id = (
                                select rmst.id 
                                from `_ref_membership_status_type` rmst
                                where rmst.name = "Active")
                    )
                        )
                ) as challengers,
                
                (select count(distinct(m.user_id))
                from membership m
                inner join plan p on m.plan_id = p.id
                where m.location_id = {location_id}
                and p.membership_type_id = (
                    select rmt.id 
                    from `_ref_membership_type` rmt
                    where rmt.name = "Limited time pass")
                and m.membership_status_type_id = (
                    select rmst.id 
                    from `_ref_membership_status_type` rmst
                    where rmst.name = "Active")
                and (m.user_id NOT IN (
                        select m2.user_id
                        from membership m2
                        inner join plan p2 on m2.plan_id = p2.id
                        where m2.location_id = {location_id}
                        and p2.membership_type_id in (
                            select rmt.id 
                            from `_ref_membership_type` rmt
                            where rmt.name 
                                in ("Full Membership", "Challenge"))
                        and m2.membership_status_type_id = (
                            select rmst.id 
                            from `_ref_membership_status_type` rmst
                            where rmst.name = "Active")
                        )
                    )
                ) as limited_time_pass;
        """
        return text(sql)

    @staticmethod
    def _at_risk_attendance_query(location_id: int, from_date: datetime) -> TextClause:
        sql = f"""
        SELECT
            CONCAT(up.first_name, ' ', up.last_name) AS name,
            up.phone_number AS phone,
            u.email AS email,
            last_scheduled.max_scheduled_time as last_scheduled_date,
            last_check_in.max_checked_in_time AS last_attended_date,
            GROUP_CONCAT(DISTINCT member_plans.name SEPARATOR ', ') AS plan_names
        FROM member_class mc
        JOIN user u ON mc.user_id = u.id
        JOIN user_profile up ON u.id = up.user_id
        JOIN membership m ON mc.membership_id = m.id 
        JOIN (
            SELECT
                mc.user_id,
                MAX(mc.member_checked_in_time) AS max_checked_in_time
            FROM member_class mc
            WHERE mc.location_id = {location_id}
                AND mc.member_checked_in_time < '{from_date}'
            GROUP BY mc.user_id
        ) AS last_check_in ON mc.user_id = last_check_in.user_id
        JOIN (
            SELECT
                mc.user_id,
                MAX(mc.class_time) AS max_scheduled_time
            FROM member_class mc
            WHERE mc.location_id = {location_id}
                AND mc.class_time < '{from_date}'
            GROUP BY mc.user_id
        ) AS last_scheduled ON mc.user_id = last_scheduled.user_id
        JOIN (
            SELECT
                membership.user_id,
                plan.name
            FROM membership
            JOIN plan ON membership.plan_id = plan.id
            WHERE plan.location_id = {location_id}
            GROUP BY membership.user_id, plan.name
        ) AS member_plans ON mc.user_id = member_plans.user_id
        WHERE mc.location_id = {location_id}
            AND mc.member_cancelled_time IS NULL
            AND m.membership_status_type_id = (
                select rmst.id
                from `_ref_membership_status_type` rmst
                where rmst.name = "Active"
            )
            AND NOT EXISTS (select 1
            from member_class mc_future
            where mc_future.user_id = u.id
              and mc_future.class_time > curdate()
              and mc_future.location_id = {location_id}
              and mc_future.member_cancelled_time is null)
        GROUP BY u.id
        UNION ALL
        SELECT
            CONCAT(up.first_name, ' ', up.last_name) AS name,
            up.phone_number AS phone,
            u.email AS email,
            'Never' as last_scheduled_date,
            'Never' AS last_attended_date,
            GROUP_CONCAT(DISTINCT member_plans.name SEPARATOR ', ') AS plan_names
        FROM membership m
        JOIN user u ON m.user_id = u.id
        JOIN user_profile up ON u.id = up.user_id
        JOIN (
            SELECT
                membership.user_id,
                plan.name
            FROM membership
            JOIN plan ON membership.plan_id = plan.id
            WHERE plan.location_id = {location_id}
            GROUP BY membership.user_id, plan.name
        ) AS member_plans ON m.user_id = member_plans.user_id
        WHERE u.id NOT IN (
            SELECT mc.user_id
            FROM member_class mc
        )
        AND m.membership_status_type_id = (
                select rmst.id
                from `_ref_membership_status_type` rmst
                where rmst.name = "Active"
        )
        GROUP BY u.id;
        """
        return text(sql)

    @staticmethod
    def _member_payment_history_query(location_id: int, from_date: datetime, to_date: datetime) -> TextClause:
        sql = f"""
            SELECT
                ROUND(SUM(revenue_received), 2) - ROUND(SUM(refunds_issued), 2) - ROUND(SUM(tax_taken), 2) AS total_revenue_received,
                ROUND(SUM(fees_revenue), 2) - ROUND(SUM(fees_refunds), 2) - ROUND(SUM(fees_taxes), 2)  AS total_fees_revenue,
                ROUND(SUM(plans_revenue), 2) - ROUND(SUM(plans_refunds), 2) - ROUND(SUM(plans_taxes), 2) AS total_revenue_plans,
                ROUND(SUM(other_revenue), 2) - ROUND(SUM(other_refunds), 2) - ROUND(SUM(other_taxes), 2) AS other_revenue
            FROM (SELECT
                        CASE
                            WHEN mph.payment_transaction_type IN (1, 3)
                                THEN mph.total_amount
                            ELSE 0
                        END AS revenue_received,
                        CASE
                            WHEN mph.payment_transaction_type IN (2)
                                THEN mph.total_amount
                            ELSE 0
                        END AS refunds_issued,
                        CASE
                            WHEN mph.payment_transaction_type IN (1, 3)
                                THEN mph.tax
                            ELSE 0
                        END AS tax_taken,
                        CASE
                            WHEN mph.membership_id IS NOT NULL and mph.payment_transaction_type IN (1, 3)
                                THEN mph.total_amount
                            ELSE 0
                         END AS plans_revenue,
                        CASE
                            WHEN mph.membership_id IS NOT NULL and mph.payment_transaction_type IN (2)
                                THEN mph.total_amount
                            ELSE 0
                         END AS plans_refunds,
                        CASE
                            WHEN mph.membership_id IS NOT NULL and mph.payment_transaction_type IN (1, 3)
                                THEN mph.tax
                            ELSE 0
                         END AS plans_taxes,
                        CASE
                            WHEN mph.payment_transaction_type IN (1, 3)  AND mph.payment_category_type_id in (1, 2, 3)
                                THEN mph.total_amount
                            ELSE 0
                        END AS fees_revenue,
                        CASE
                            WHEN mph.payment_transaction_type IN (2)  AND mph.payment_category_type_id in (1, 2, 3)
                                THEN mph.total_amount
                            ELSE 0
                        END AS fees_refunds,
                        CASE
                            WHEN mph.payment_transaction_type IN (1, 3)  AND mph.payment_category_type_id in (1, 2, 3)
                                THEN mph.tax
                            ELSE 0
                        END AS fees_taxes,
                        CASE
                            WHEN mph.payment_transaction_type IN (1, 3)  AND mph.payment_category_type_id in (4)
                                THEN mph.total_amount
                            ELSE 0
                        END AS other_revenue,
                        CASE
                            WHEN mph.payment_transaction_type IN (2)  AND mph.payment_category_type_id in (4)
                                THEN mph.total_amount
                            ELSE 0
                        END AS other_refunds,
                        CASE
                            WHEN mph.payment_transaction_type IN (1, 3)  AND mph.payment_category_type_id in (4)
                                THEN mph.tax
                            ELSE 0
                        END AS other_taxes,
                        CASE
                            WHEN mph.payment_transaction_type IN (2)
                                THEN mph.tax
                            ELSE 0
                        END AS tax_refunds
                  FROM member_payment_history mph
                  WHERE mph.location_id = {location_id} AND mph.payrix_transaction_status not in (2) and payrix_transaction_error is null
                    AND mph.processed_date BETWEEN '{from_date}' AND '{to_date}'
                    AND (SELECT is_dea FROM location WHERE id = {location_id}) = 0            
            ) as combined;
            """
        return text(sql)

    @staticmethod
    def _invoice_query(location_id: int, from_date: datetime, to_date: datetime) -> TextClause:
        sql = f"""
                with invoice_data as
                    (select ii.location_id, ii.id,
                       case when i.invoice_type_id != 2 and i.product_category_type_id = 1 and ii.description like '%signup%' then
                          ii.amount
                       end as signup_fee,
                       case when i.invoice_type_id != 2 and i.product_category_type_id = 1 and ii.description not like '%signup%' then
                          ii.amount
                       end as membership_fee,
                       case when i.product_category_type_id = 3 and ii.product_id = 1 then
                          ii.amount
                       end as cancellation_fee,
                       case when i.product_category_type_id = 3 and ii.product_id = 2 then
                          ii.amount
                       end as late_fee,
                       case when i.product_category_type_id = 3 and ii.product_id = 3 then
                          ii.amount
                       end as no_show_fee,
                       case when i.product_category_type_id = 3 and ii.product_id = 4 then
                          ii.amount
                       end as other,
                       case when i.invoice_type_id = 2 then
                          ii.total_amount 
                       end as credit_memo,
                       ii.discount as discount,
                       ii.tax as tax
                    from invoice_item ii left join invoice i on ii.invoice_id = i.id
                    where i.invoice_status_type_id in (1,2,3) and
                          ii.location_id = {location_id} and ii.due_date between date('{from_date}') and date('{to_date}')),
                aggregated_invoice_data as
                    (select location_id,
                           sum(ifnull(signup_fee, 0)) as signup_fees,
                           sum(ifnull(membership_fee, 0)) as membership_fees,
                           sum(ifnull(cancellation_fee, 0)) as cancellation_fees,
                           sum(ifnull(late_fee, 0)) as late_fees,
                           sum(ifnull(no_show_fee, 0)) as no_show_fees,
                           sum(ifnull(other, 0)) as others,
                           sum(ifnull(discount, 0)) as discounts,
                           sum(ifnull(tax, 0)) as taxes,
                           sum(ifnull(credit_memo, 0)) as credit_memos
                    from invoice_data
                    group by location_id)
                select location_id, 
                       signup_fees, 
                       membership_fees, 
                       cancellation_fees, 
                       late_fees, 
                       no_show_fees, 
                       others, 
                       discounts,
                       (signup_fees + membership_fees + cancellation_fees + late_fees + no_show_fees + others - discounts - credit_memos) as sub_total,
                       taxes as total_taxes,
                       case 
                            when credit_memos = 0 THEN 0 
                            else -credit_memos 
                        end as credit_memos,
                       (signup_fees + membership_fees + cancellation_fees + late_fees + no_show_fees + others - discounts - credit_memos) + taxes as total_invoice_value
                from aggregated_invoice_data
                """
        return text(sql)

    @staticmethod
    def _payment_history_query_v2(location_id: int, from_date: datetime, to_date: datetime) -> TextClause:
        sql = f"""
                with payment_data as
                    (select mph.location_id,
                        case when mph.payment_transaction_type_id in (1, 3) and mpm.method in (1, 2, 3, 4, 5)
                            then mph.total_amount
                        end as credit_card_payment,
                        case when mph.payment_transaction_type_id in (1, 3) and mpm.method in (7)
                            then mph.total_amount
                        end as debit_card_payment,
                        case when mph.payment_transaction_type_id in (1, 3) and mpm.method in (8, 9, 10, 11) and payrix_transaction_status not in (5)
                            then mph.total_amount
                        end as ach_payment,
                        case when mph.payment_transaction_type_id in (1, 3) and mph.payment_method_id = 0
                            then mph.total_amount
                        end as cash_payment,
                        case when mph.payment_transaction_type_id = 2 and mpm.method in (1, 2, 3, 4, 5) 
                            then mph.total_amount
                        end as credit_card_refund,
                        case when mph.payment_transaction_type_id = 2 and mpm.method in (7) 
                            then mph.total_amount
                        end as debit_card_refund,
                        case when mph.payment_transaction_type_id = 2 and mpm.method in (8, 9, 10, 11) and payrix_transaction_status not in (5)
                            then mph.total_amount
                        end as ach_refund,
                        case when mph.payment_transaction_type_id in (2) and mph.payment_method_id = 0
                            then mph.total_amount
                        end as cash_refund                        
                    from member_payment_history_v2 mph
                          left join member_payment_method mpm on mph.payment_method_id = mpm.id
                    where mph.location_id = {location_id}
                        and payrix_transaction_status in (4)
                        and payrix_transaction_error is null
                        and processed_date between '{from_date}' and '{to_date}')
                select location_id,
                    sum(ifnull(credit_card_payment, 0)) - sum(ifnull(credit_card_refund, 0)) as credit_card_payments,
                    sum(ifnull(debit_card_payment, 0)) - sum(ifnull(debit_card_refund, 0)) as debit_card_payments,
                    sum(ifnull(ach_payment, 0)) - sum(ifnull(ach_refund, 0)) as ach_payments,
                    sum(ifnull(cash_payment, 0)) - sum(ifnull(cash_refund, 0)) as cash_payments,
                    sum(ifnull(credit_card_refund, 0)) + sum(ifnull(debit_card_refund, 0)) + sum(ifnull(ach_refund, 0))
                     + sum(ifnull(cash_refund, 0)) as refunds,
                    (sum(ifnull(credit_card_payment, 0)) + sum(ifnull(debit_card_payment, 0)) + sum(ifnull(ach_payment, 0)) 
                        + sum(ifnull(cash_payment, 0)) - sum(ifnull(credit_card_refund, 0)) - sum(ifnull(debit_card_refund, 0))
                        - sum(ifnull(ach_refund, 0)) - sum(ifnull(cash_refund, 0))) as total_payments
                from payment_data
                group by location_id;            
                """
        return text(sql)

    @staticmethod
    def _member_payment_schedule_query(location_id: int, from_date: datetime, to_date: datetime) -> TextClause:
        sale = PaymentTransactionTypeEnum.SALE.value
        retry_sale = PaymentTransactionTypeEnum.RETRY_SALE.value
        failed = PayrixTransactionStatusEnum.FAILED.value
        sql = f"""
            WITH cte_auto_renewal_payments AS (
                SELECT
                    (
                        IF(
                            DATEDIFF(membership.plan_end_date, membership.plan_start_date)
                            >
                            DATEDIFF('{to_date.date()}', membership.plan_end_date),
                            1,
                            DATEDIFF('{to_date.date()}', membership.plan_end_date)
                            DIV
                            DATEDIFF(membership.plan_end_date, membership.plan_start_date)
                        )
                        *
                        ROUND(
                            COALESCE(member_payment_history.total_amount, 0)
                            -
                            COALESCE(member_payment_history.tax, 0),
                        2)
                    ) AS total
                FROM member_payment_history
                JOIN membership ON membership.id = member_payment_history.membership_id
                WHERE member_payment_history.location_id = {location_id}
                AND member_payment_history.processed_date -- datetime type
                    -- first day of the next month
                    BETWEEN '{to_utc(from_date).date()}'
                    -- last day of the next month
                    AND '{to_utc(to_date).date()}'
                AND membership.auto_renewal = 1
                AND membership.cancel_date IS NULL
            ),
            cte_member_payment_schedule AS (
                SELECT
                    mps.membership_id,
                    mps.scheduled_date,
                    IF(
                        mps.payment_transaction_type IN ({sale}, {retry_sale}),
                        COALESCE(mps.total_amount, 0) - COALESCE(mps.tax, 0),
                        0
                    ) AS total
                FROM member_payment_schedule mps
                WHERE mps.location_id = {location_id}
                    AND mps.payrix_onboarding_status NOT IN ({failed})
                    AND payrix_onboarding_error IS NULL
                    AND mps.scheduled_date -- date type
                        -- first day of the next month
                        BETWEEN '{from_date.date()}'
                        -- last day of the next month
                        AND '{to_date.date()}'
            )
            SELECT (
                (
                    SELECT COALESCE(ROUND(SUM(total), 2), 0)
                    FROM cte_auto_renewal_payments
                )
                +
                (
                    SELECT COALESCE(ROUND(SUM(total), 2), 0)
                    FROM cte_member_payment_schedule
                )
            ) AS revenue;
        """
        return text(sql)

    @staticmethod
    def _balance_and_future_contract_value_query(location_id: int) -> TextClause:
        sql = f"""
            SELECT 
                CONCAT(up.first_name, ' ', up.last_name) AS contact,
                mph.user_id AS member_id,
                COALESCE(CASE 
                    WHEN mph.membership_id IS NOT NULL THEN p.name
                    ELSE rpct.name
                END,'N/A') AS plan,
                COALESCE(ROUND(fc.scheduled_future_contract_value, 2), 0) AS future_contract_value,
                ROUND(SUM(
                    CASE
                        WHEN mph.payrix_transaction_status = ft.id THEN mph.total_amount
                        ELSE 0
                    END
                ), 2) AS balance
            FROM member_payment_history mph
            JOIN `user` u ON u.id = mph.user_id 
            JOIN user_profile up ON up.user_id = u.id
            LEFT JOIN membership m ON m.id = mph.membership_id 
            LEFT JOIN plan p ON p.id = m.plan_id
            LEFT JOIN `_ref_billing_type` rbt ON rbt.id = p.billing_type_id
            LEFT JOIN `_ref_payment_category_type` rpct ON rpct.id = mph.payment_category_type_id
            LEFT JOIN (
                SELECT
                    mps.user_id,
                    p.id AS plan_id,
                    rpct.id AS category_id,
                    SUM(mps.total_amount) AS scheduled_future_contract_value
                FROM member_payment_schedule mps
                LEFT JOIN membership m ON m.id = mps.membership_id
                LEFT JOIN plan p ON p.id = m.plan_id 
                LEFT JOIN `_ref_payment_category_type` rpct ON rpct.id = mps.payment_category_type_id 
                WHERE mps.location_id = {location_id}
                GROUP BY mps.user_id, p.id, rpct.id
            ) fc ON fc.user_id = mph.user_id AND (p.id = fc.plan_id OR rpct.id = fc.category_id) 
            JOIN `_ref_payrix_transaction_status_type` ft ON ft.name = 'Failed'
            WHERE mph.location_id = {location_id}
            AND (mph.membership_id IS NOT NULL OR mph.payment_category_type_id IS NOT NULL)
            GROUP BY up.first_name, 
                up.last_name, 
                mph.user_id, 
                p.name, 
                rpct.name, 
                fc.scheduled_future_contract_value,
                mph.membership_id
            HAVING future_contract_value > 0 OR balance > 0
            ORDER BY up.first_name, up.last_name;
        """
        return text(sql)

    @staticmethod
    def _location_timezone_query(location_id: int) -> TextClause:
        sql = f"""
        select rtt.iana_tzdata
        from location l
        join gym g on g.id = l.gym_id
        join `_ref_timezone_type` rtt on rtt.id = g.timezone_type_id
        where l.id = {location_id};
        """
        return text(sql)

    @staticmethod
    def _recurring_member_churn_query(location_id: int, from_date: datetime, to_date: datetime) -> TextClause:
        sql = f"""
        select
            ms.plan_name,
            ms.billing_type,
            ms.plan_type,
            count(ms.plan_name) as plan_total,
            sum(ms.cancelled) as plan_total_exited,
            coalesce(round(((sum(ms.cancelled)*100)/count(ms.plan_name)),2),0) as churn_percentage
        from
        (select
            p.name as plan_name,
            rbt.name as billing_type,
            group_concat(distinct(rpt.name), "") as plan_type,
            m.id as membership_id,
            m.plan_start_date,
            (case when m.cancel_date between '{from_date.date()}' and '{to_date.date()}' then 1 else 0 end) as cancelled,
            (select 
                rmst.name
            from `_ref_membership_status_type` rmst
            where rmst.id = m.membership_status_type_id) as status,
            m.cancel_date
        from membership m
        join plan p
            on m.plan_id = p.id
        join `_ref_billing_type` rbt 
            on p.billing_type_id = rbt.id
        join plan_plan_type ppt 
            on ppt.plan_id = p.id
        join `_ref_plan_type` rpt 
            on ppt.plan_type_id = rpt.id
        where 
            m.location_id = {location_id}
            and m.plan_start_date <= '{from_date.date()}'
        group by p.id, m.cancel_date, m.id, p.billing_type_id
        order by p.id) as ms
        group by plan_name, billing_type, plan_type
        order by churn_percentage desc, plan_name;
        """
        return text(sql)

    @staticmethod
    def _challenge_conversions_cohort_detail_query(
            location_id: int, from_date: datetime | None = None, to_date: datetime | None = None) -> TextClause:
        dates_query: str = ""
        if from_date and to_date:
            dates_query = f"AND m.plan_start_date between '{from_date}' and '{to_date}'"
        sql = f"""
        SELECT
            m.user_id AS member_id,
            CONCAT(up.first_name, ' ', up.last_name) AS member_name,
            CASE
                WHEN EXISTS (
                    SELECT 1
                    FROM membership m2
                    JOIN plan p2 ON m2.plan_id = p2.id
                    WHERE m2.location_id = {location_id}
                        AND p2.membership_type_id = (SELECT id FROM `_ref_membership_type` WHERE name = 'Full Membership')
                        AND MONTH(m2.plan_start_date) = MONTH(NOW())
                        AND m2.user_id = m.user_id
                ) THEN 'yes'
                ELSE 'no'
            END AS converted,
            m.plan_start_date AS challenge_start_date,
            m.plan_end_date AS challenge_end_date,
            p.name AS challenge_plan_name,
            CASE
                WHEN EXISTS (
                    SELECT 1
                    FROM membership m2
                    JOIN plan p2 ON m2.plan_id = p2.id
                    WHERE m2.location_id = {location_id}
                        AND p2.membership_type_id = (SELECT id FROM `_ref_membership_type` WHERE name = 'Full Membership')
                        AND MONTH(m2.plan_start_date) = MONTH(NOW())
                        AND m2.user_id = m.user_id
                ) THEN (
                    SELECT p2.name
                    FROM membership m2
                    JOIN plan p2 ON m2.plan_id = p2.id
                    WHERE m2.location_id = {location_id}
                        AND p2.membership_type_id = (SELECT id FROM `_ref_membership_type` WHERE name = 'Full Membership')
                        AND MONTH(m2.plan_start_date) = MONTH(NOW())
                        AND m2.user_id = m.user_id
                    LIMIT 1
                )
                ELSE '-'
            END AS full_membership_plan
        FROM membership m
        JOIN user u ON u.id = m.user_id
        JOIN user_profile up ON u.id = up.user_id
        JOIN plan p ON m.plan_id = p.id
        JOIN `_ref_membership_type` rmt2 ON p.membership_type_id = rmt2.id
        WHERE m.location_id = {location_id}
            AND rmt2.name = 'Challenge'
            {dates_query}
        GROUP BY m.user_id, m.plan_start_date, m.plan_end_date, p.name, up.first_name, up.last_name;
        """
        return text(sql)

    @staticmethod
    def _challenge_conversions_cohort_summary_query(
            location_id: int, from_date: datetime | None = None, to_date: datetime | None = None) -> TextClause:
        dates_query: str = ""
        if from_date and to_date:
            dates_query = f"AND m.plan_start_date between '{from_date}' and '{to_date}'"
        sql = f"""
        SELECT 
            challenge_plan,
            cohort_month,
            SUM(tot_part) as total_participants,
            MAX(c_end_date) as cohort_end_date,
            SUM(memb_conv) as members_converted,
            round(coalesce((SUM(memb_conv) * 100 / SUM(tot_part)),0),0) AS conversion_rate_percentage
        FROM (
            SELECT 
                p.name AS challenge_plan,
                MONTHNAME(m.plan_start_date) AS cohort_month,
                COUNT(DISTINCT m.user_id) AS tot_part,
                CASE 
                    WHEN m.plan_end_date IS NOT NULL THEN DATE(m.plan_end_date)
                    ELSE '-'
                END AS c_end_date,
                SUM(
                    CASE 
                        WHEN EXISTS (
                            SELECT 1
                            FROM membership m2
                            JOIN plan p2 ON m2.plan_id = p2.id
                            WHERE m2.location_id = {location_id}
                                AND p2.membership_type_id = (
                                    SELECT id 
                                    FROM `_ref_membership_type` 
                                    WHERE name = 'Full Membership'
                                )
                                AND MONTH(m2.plan_start_date) = MONTH(CURDATE())
                                AND m2.user_id = m.user_id
                        ) THEN 1
                        ELSE 0 
                    END
                ) AS memb_conv
            FROM membership m
            JOIN user_profile up ON m.user_id = up.user_id
            JOIN plan p ON m.plan_id = p.id
            WHERE m.location_id = {location_id}
                {dates_query}
                AND p.membership_type_id = (
                    SELECT rmt.id
                    FROM `_ref_membership_type` rmt
                    WHERE rmt.name = 'Challenge'
                )
            GROUP BY m.plan_start_date, 
            m.plan_end_date, 
            p.name
        ) AS subquery
        GROUP BY challenge_plan, cohort_month
        ORDER BY challenge_plan;
        """
        return text(sql)

    @staticmethod
    def get_dict(result: list) -> dict | None:
        _dict = next(iter(result), {})
        return _dict

    @staticmethod
    def get_scalar(result) -> float | int | str  | None:
        _dict = Report.get_dict(result)
        scalar, = _dict.values() if _dict else (None,)
        return scalar

    @staticmethod
    def _map_results(result):
        results_list = result.mappings().all()
        dictionaries_list = [dict(r) for r in results_list]
        return dictionaries_list

    @staticmethod
    def _filter_results(results: List[dict], nc_filter: dict):
        for key, value in nc_filter.items():
            results = [result for result in results if result[key] == value]
        return results

    @staticmethod
    def _clean_dates(results: List[dict]):
        for contact in results:
            for k, v in contact.items():
                if isinstance(v, datetime):
                    contact[k] = v.strftime("%Y-%m-%d %H:%M")
        return results
