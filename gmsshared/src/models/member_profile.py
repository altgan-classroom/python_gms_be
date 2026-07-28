from datetime import datetime
from typing import List, Optional, Self
import json
from sqlalchemy import (
    DateTime, Column, Integer, Boolean, ForeignKey, text, Float, BigInteger, String, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from gmsshared import db
from gmsshared.src.models.user import User
from gmsshared.src.models.location import Location
from gmsshared.src.models._ref_member_status_type import _RefMemberStatusType
from gmsshared.src.models._ref_payment_status_type import _RefPaymentStatusType
from gmsshared.src.models._ref_objective_type import _RefObjectiveType
from gmsshared.src.models._ref_relationship_type import _RefRelationshipType
from gmsshared.src.models.plan import Plan
from gmsshared.src.util.enums import (InvoiceStatusTypeEnum, RoleEnum, ContactTypeEnum, MembershipStatusEnum,
    MembershipTypeEnum, PayrixTransactionStatusEnum, PaymentTransactionTypeEnum, PayrixOnboardStatusEnum, PaymentStatusEnum)


class MemberProfile(db.Model):
    # A member is a type of user
    user_id = Column(BigInteger, ForeignKey('user.id'), nullable=False, primary_key=True)
    user = relationship("User")

    # A member belongs to a location
    location_id = Column(BigInteger, ForeignKey('location.id'), nullable=False, primary_key=True)
    location = relationship("Location")

    member_status_type_id = Column(Integer, ForeignKey('_ref_member_status_type.id'))
    member_status = relationship('_RefMemberStatusType')
    payment_status_type_id = Column(Integer, ForeignKey('_ref_payment_status_type.id'))
    payment_status = relationship('_RefPaymentStatusType')
    objective_type_id = Column(Integer, nullable=True)

    start_date = Column(DateTime, nullable=True)
    last_check_in = Column(DateTime, nullable=True)
    cp_phone_calls = Column(Boolean(), nullable=True, default=False)
    cp_email = Column(Boolean(), nullable=True, default=False)
    cp_sms = Column(Boolean(), nullable=True, default=False)
    cp_in_app_message = Column(Boolean(), nullable=True, default=False)
    favourite_gym_clothing_website = Column(String(50), nullable=True)
    favourite_website = Column(String(50), nullable=True)
    favourite_restaurant = Column(String(50), nullable=True)
    payrix_customer_id = Column(String(50), nullable=True)
    payrix_onboarding_status = Column(Integer, nullable=True, server_default='1')
    outstanding_balance = Column(Float, nullable=True, default=0)

    door_access_user_id = Column(String(100), nullable=True)
    door_access_auth_info = Column(JSON, nullable=True, server_default='{}')
    door_access_auth_status = Column(Integer, nullable=True, server_default='1')

    door_access_credential = Column(String(100), nullable=True)
    door_access_credential_id = Column(String(100), nullable=True)
    door_access_credential_status = Column(Integer, nullable=True, server_default='1')

    create_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(type_=DateTime, nullable=False, server_default=func.now(), onupdate=datetime.utcnow)

    @classmethod
    def find_by_id(cls, location_id: int, user_id: int) -> Optional[Self]:
        return cls.query.filter_by(user_id=user_id, location_id=location_id).first()

    @classmethod
    def find_all_dea_location(cls) -> Optional[List[Self]]:
        sql = f"""
               select user_id as member_id, l.id as location_id
               from member_profile mp left join location l on mp.location_id = l.id
               where l.is_dea = 1
               """
        result = db.session.execute(text(sql))
        results_as_dict = result.mappings().all()
        return results_as_dict

    @classmethod
    def find_users_with_no_payrix_data(cls, location_id: int) -> Optional[list]:
        sql = f"""SELECT mp.user_id FROM member_profile mp WHERE mp.location_id = {location_id} AND mp.payrix_customer_id IS NULL"""
        result = db.session.execute(text(sql))
        results_as_dict = result.mappings().all()
        return results_as_dict

    @classmethod
    # TODO: Change all get to find or vice-versa. Be consistent
    def get_info_by_id(cls, location_id: int, user_id: int) -> Optional[Self]:
        sql = f"""select u.id as member_id, 
                    p.first_name as first_name, 
                    p.last_name as last_name, 
                    p.middle_name,
                    p.preferred_name, 
                    u.email, 
                    p.photo_url, 
                    p.birth_date, 
                    p.gender_type_id, 
                    p.address_street,
                    p.address_street_2,
                    p.address_city,
                    p.address_state, 
                    p.address_zip, 
                    p.address_country,
                    p.emergency_first_name, 
                    p.emergency_last_name, 
                    p.emergency_phone_number, 
                    p.emergency_relationship_type_id,
                    p.guardian_first_name, 
                    p.guardian_last_name, 
                    p.guardian_phone_number,
                    p.have_children,
                    mst.name as membership_status,
                    if((ifnull(mps.payments_due, 0) > 0 or ifnull(mph.failed_payments, 0) > 0), '{PaymentStatusEnum.PAST_DUE.value}', '{PaymentStatusEnum.CURRENT.value}') as payment_status,
                    mp.last_check_in, 
                    mp.location_id, 
                    mp.objective_type_id,
                    mp.outstanding_balance,
                    (select mpin.plan_start_date
                           from membership mpin
                           where location_id = {location_id} and user_id = {user_id}
                           order by mpin.plan_start_date
                           limit 1) as create_datetime,
                    p.about,
                    case when ifnull(msp.num_memberships, 0) = 0 then '{ContactTypeEnum.LEAD.value}' 
                         when ifnull(active.num_active, 0) > 0 then '{ContactTypeEnum.CLIENT.value}'
                         when ifnull(frozen.num_frozen, 0) > 0 and ifnull(active.num_active, 0) = 0 then '{ContactTypeEnum.FROZEN.value}'
                         else '{ContactTypeEnum.EXITED.value}' 
                    end as contact_type,
                    mp.door_access_credential,
                    mp.door_access_credential_status                                        
                from member_profile mp
                    left join _ref_member_status_type mst on mst.id = mp.member_status_type_id
                    left join _ref_payment_status_type pst on pst.id = mp.payment_status_type_id
                    left join user u  on u.id = mp.user_id
                    left join user_profile p on u.id = p.user_id
                    left join (select location_id, user_id, count(*) as num_memberships 
                               from membership group by location_id, user_id) msp
                        on msp.location_id = mp.location_id and msp.user_id = mp.user_id
                    left join (select location_id, user_id, count(*) as num_active 
                               from membership where membership_status_type_id = {MembershipStatusEnum.ACTIVE.value} group by location_id, user_id) active
                        on active.location_id = mp.location_id and active.user_id = mp.user_id
                    left join (select location_id, user_id, count(*) as num_cancelled 
                               from membership where membership_status_type_id = {MembershipStatusEnum.CANCELLED.value} group by location_id, user_id) cancelled
                        on cancelled.location_id = mp.location_id and cancelled.user_id = mp.user_id
                    left join (select location_id, user_id, count(*) as num_frozen 
                               from membership where membership_status_type_id = {MembershipStatusEnum.FROZEN.value} group by location_id, user_id) frozen
                        on frozen.location_id = mp.location_id and frozen.user_id = mp.user_id                    
                    left join (select location_id, user_id, count(*) as num_renewed 
                               from membership where membership_status_type_id = {MembershipStatusEnum.RENEWED.value} group by location_id, user_id) renewed
                        on renewed.location_id = mp.location_id and renewed.user_id = mp.user_id
                    left join (select location_id, user_id, count(*) as failed_payments
                               from member_payment_history
                               where payment_transaction_type = {PaymentTransactionTypeEnum.SALE.value} and payrix_transaction_status = {PayrixTransactionStatusEnum.FAILED.value} group by location_id, user_id) mph 
                        on mph.location_id = mp.location_id and mph.user_id = mp.user_id
                    left join (select location_id, user_id, count(*) as payments_due
                               from member_payment_schedule
                               where scheduled_date < now() and (payrix_onboarding_error is null or trim(payrix_onboarding_error) = '')
                                 and payrix_onboarding_status <> {PayrixOnboardStatusEnum.NOT_READY.value} group by location_id, user_id) mps 
                        on mps.location_id = mp.location_id and mps.user_id = mp.user_id                     
                where u.role_type_id = {RoleEnum.MEMBER.value} 
                    and u.id = {user_id} 
                    and mp.location_id = {location_id}"""
        result = db.session.execute(text(sql))
        result_mapping = result.mappings().first()
        if result_mapping is None:
            return None
        else:
            results_as_dict = {}
            for key, value in result_mapping.items():
                results_as_dict[key] = value
            return results_as_dict


    @classmethod
    def find_by_location(cls, location_id: int, user_name: str = None) -> Optional[List[Self]]:
        where_sql = f"""
        WHERE u.role_type_id = {RoleEnum.MEMBER.value} 
        AND mp.location_id = {location_id}
        """
        name_parts = user_name.split() if user_name else []
        params = {}
        if len(name_parts) == 1:
            where_sql += """
            AND (p.first_name LIKE :name_part 
                 OR p.last_name LIKE :name_part)
            """
            params['name_part'] = f"%{name_parts[0]}%"
        elif len(name_parts) == 2:
            where_sql += """
            AND (p.first_name LIKE :first_name 
                 AND p.last_name LIKE :last_name)
            """
            params['first_name'] = f"%{name_parts[0]}%"
            params['last_name'] = f"%{name_parts[1]}%"

        # TODO: Delete the payment_status logic from here later after beta
        sql = f"""select concat(p.first_name, ' ', p.last_name) as member_name, 
                    u.email as email,
                    p.first_name as first_name,
                    p.last_name as last_name,
                    p.phone_number as phone_number,
                    u.id as member_id,
                    mp.location_id, 
                    u.create_datetime,
                    case when ifnull(msp.num_memberships, 0) = 0 then '{ContactTypeEnum.LEAD.value}' 
                         when ifnull(active.num_active, 0) > 0 then '{ContactTypeEnum.CLIENT.value}'
                         when ifnull(frozen.num_frozen, 0) > 0 and ifnull(active.num_active, 0) = 0 then '{ContactTypeEnum.FROZEN.value}'
                         else '{ContactTypeEnum.EXITED.value}' 
                    end as contact_type,
                    case when (ifnull(active.num_active, 0) >= 0 or ifnull(msp.num_memberships, 0) = ifnull(frozen.num_frozen, 0)) then
                            (concat(if(ifnull(full.num_full, 0) > 0, 'Full Membership,', ''),
                                    if(ifnull(chall.num_chall, 0) > 0, 'Challenge,', ''),
                                    if(ifnull(lim.num_lim, 0) > 0, 'Limited Time Pass,', '')))
                        when (ifnull(msp.num_memberships, 0) = 0 or ifnull(msp.num_memberships, 0) = ifnull(cancelled.num_cancelled, 0)) then
                            '-'
                    end as membership_status,
                    mp.door_access_credential,
                    mp.door_access_credential_status                    
                from member_profile mp
                    left join _ref_member_status_type mst on mst.id = mp.member_status_type_id
                    left join _ref_payment_status_type pst on pst.id = mp.payment_status_type_id
                    left join user u  on u.id = mp.user_id
                    left join user_profile p on u.id = p.user_id
                    left join (select location_id, user_id, count(*) as num_memberships 
                               from membership group by location_id, user_id) msp
                        on msp.location_id = mp.location_id and msp.user_id = mp.user_id
                    left join (select location_id, user_id, count(*) as num_active 
                               from membership where membership_status_type_id = {MembershipStatusEnum.ACTIVE.value} group by location_id, user_id) active
                        on active.location_id = mp.location_id and active.user_id = mp.user_id
                    left join (select location_id, user_id, count(*) as num_cancelled 
                               from membership where membership_status_type_id = {MembershipStatusEnum.CANCELLED.value} group by location_id, user_id) cancelled
                        on cancelled.location_id = mp.location_id and cancelled.user_id = mp.user_id
                    left join (select location_id, user_id, count(*) as num_frozen 
                               from membership where membership_status_type_id = {MembershipStatusEnum.FROZEN.value} group by location_id, user_id) frozen
                        on frozen.location_id = mp.location_id and frozen.user_id = mp.user_id
                    left join (select location_id, user_id, count(*) as num_renewed 
                               from membership where membership_status_type_id = {MembershipStatusEnum.RENEWED.value} group by location_id, user_id) renewed
                        on renewed.location_id = mp.location_id and renewed.user_id = mp.user_id
                    left join (select full.location_id, full.user_id, count(*) as num_full 
                               from membership full left join plan p on full.plan_id = p.id 
                               where p.membership_type_id = {MembershipTypeEnum.FULL_MEMBERSHIP.value} and full.membership_status_type_id <> {MembershipStatusEnum.CANCELLED.value} 
                               group by location_id, user_id) full
                        on full.location_id = mp.location_id and full.user_id = mp.user_id
                    left join (select chall.location_id, chall.user_id, count(*) as num_chall 
                               from membership chall left join plan p on chall.plan_id = p.id 
                               where p.membership_type_id = {MembershipTypeEnum.CHALLENGE.value} and chall.membership_status_type_id <> {MembershipStatusEnum.CANCELLED.value}
                               group by location_id, user_id) chall
                        on chall.location_id = mp.location_id and chall.user_id = mp.user_id
                    left join (select lim.location_id, lim.user_id, count(*) as num_lim 
                               from membership lim left join plan p on lim.plan_id = p.id 
                               where p.membership_type_id = {MembershipTypeEnum.LIMITED_TIME_PASS.value} and lim.membership_status_type_id <> {MembershipStatusEnum.CANCELLED.value}
                               group by location_id, user_id) lim
                        on lim.location_id = mp.location_id and lim.user_id = mp.user_id
                {where_sql}"""
        result = db.session.execute(text(sql), params)
        results_as_dict = result.mappings().all()
        return results_as_dict

    @classmethod
    def get_profile_info_by_id(cls, location_id: int, user_id: int) -> Optional[Self]:
        sql = f"""select u.id as member_id, 
                    p.first_name as first_name, 
                    p.last_name as last_name, 
                    p.middle_name,
                    p.preferred_name,
                    u.email,
                    p.birth_date,
                    p.gender_type_id,
                    p.address_street,
                    p.address_street_2,
                    p.address_city,
                    p.address_state,
                    p.address_zip,
                    p.address_country,
                    p.phone_number,
                    p.have_children,
                    p.shirt_size_type_id,
                    p.shirt_fit_type_id,
                    p.emergency_first_name,
                    p.emergency_last_name,
                    p.emergency_phone_number,
                    p.emergency_relationship_type_id,
                    p.guardian_first_name,
                    p.guardian_last_name,
                    p.guardian_phone_number,
                    p.relationship_status_type_id,
                    p.have_children as do_you_have_children,
                    mp.location_id,
                    mp.objective_type_id,
                    mp.favourite_restaurant,
                    mp.favourite_website,
                    mp.cp_phone_calls,
                    mp.cp_sms,
                    mp.cp_email,
                    mp.cp_in_app_message,
                    mp.favourite_gym_clothing_website,
                    mp.payrix_customer_id,
                    mp.payrix_onboarding_status,
                    mp.outstanding_balance,
                    p.about,
                    u.create_datetime,
                    mp.door_access_auth_info,
                    mp.door_access_auth_status,
                    u.create_datetime,
                    mp.door_access_credential,
                    mp.door_access_credential_status
                from member_profile mp
                    left join user u  on u.id = mp.user_id
                    left join user_profile p on u.id = p.user_id
                where u.role_type_id = {RoleEnum.MEMBER.value} 
                    and u.id = {user_id} 
                    and mp.location_id = {location_id}"""
        result = db.session.execute(text(sql))
        result_mapping = result.mappings().first()
        if result_mapping is None:
            return None
        else:
            results_as_dict = {}
            for key, value in result_mapping.items():
                results_as_dict[key] = json.loads(value) if key == "door_access_auth_info" and value else value
            return results_as_dict


    @classmethod
    def get_reconciliation_info(cls, location_id: int, user_id: int) -> Optional[List]:
        sql = f"""
                with invoice_entries as
                         (select ii.id,
                                 ii.create_datetime as processed_date,
                                 case
                                     when i.invoice_type_id = 1 then 'Invoice'
                                     when i.invoice_type_id = 2 then 'Credit Memo'
                                     when i.invoice_type_id = 3 then 'Write Off'
                                     end     as type,
                                 case
                                     when i.invoice_type_id = 1 then 0
                                     when i.invoice_type_id = 2 then 1
                                     when i.invoice_type_id = 3 then 1
                                     end     as credit,
                                 ii.total_amount
                          from invoice_item ii
                                   left join invoice i on ii.invoice_id = i.id
                          where ii.location_id = {location_id} and ii.user_id = {user_id} 
                              and i.invoice_status_type_id not in ({InvoiceStatusTypeEnum.VOID.value})),
                normal_payment_entries as
                    (select mph.id,
                        mph.processed_date,
                        case
                            when mph.payment_transaction_type_id in (1, 3)
                                and mpm.method in (1, 2, 3, 4, 5)
                                then 'Credit Card Payment'
                            when mph.payment_transaction_type_id in (1, 3)
                                and mpm.method in (7)
                                then 'Debit Card Payment'
                            when mph.payment_transaction_type_id in (1, 3)
                                and mpm.method in (8, 9, 10, 11) and payrix_transaction_status not in (5)
                                then 'ACH Payment'
                            when mph.payment_transaction_type_id = 2
                                then 'Refund' 
                            when mph.payment_method_id = 0
                                then 'Cash'                                 
                            end as type,
                        case
                            when mph.payment_transaction_type_id in (1, 3) then 1
                            when mph.payment_transaction_type_id = 2 then 0
                        end as credit,
                        mph.total_amount
                    from member_payment_history_v2 mph
                          left join member_payment_method mpm on mph.payment_method_id = mpm.id
                    where mph.location_id = {location_id} 
                        and mph.user_id = {user_id} 
                        and payrix_transaction_status in (4) 
                        and payrix_transaction_error is null
                        and processed_date is not null)
                select * from normal_payment_entries
                union all
                select * from invoice_entries
                order by processed_date desc
        """
        result = db.session.execute(text(sql))
        results_as_dict = result.mappings().all()
        return results_as_dict


    @classmethod
    def get_activity_history(cls, location_id: int, user_id: int) -> Optional[List]:
        sql = f"""with invoice_entries as
                    (select i.id,
                         ifnull(ii.due_date, ii.create_datetime) as activity_date,
                         'invoice' as instrument_type,
                         case
                            when i.invoice_type_id in (2, 3) THEN concat('Account Credit - ', ifnull(i.notes, i.description))
                            else i.description
                         end as description,
                         case
                             when (i.invoice_type_id = 1 and i.product_category_type_id = 1) then 'Charges Recurring'
                             when (i.invoice_type_id = 1 and i.product_category_type_id in (2, 3)) then 'Charges'
                             when i.invoice_type_id in (2, 3) then 'Charges Credit'
                         end as type,
                         case
                             when i.invoice_type_id in (1, 2, 3) and i.invoice_status_type_id = 4 then 0
                             when (i.invoice_type_id = 1) then sum(ii.total_amount)
                             when (i.invoice_type_id in (2, 3)) then -sum(ii.total_amount)
                         end as total,
                         case
                             when i.invoice_type_id in (1, 2, 3) and i.invoice_status_type_id = 4 then sum(ii.total_amount)
                             when i.invoice_type_id = 1 then sum(ii.total_amount)
                             when i.invoice_type_id in (2, 3) then -sum(ii.total_amount)
                         end as charges,
                         case
                             when i.invoice_type_id in (1, 2, 3) and i.invoice_status_type_id = 4 then 'Voided'
                             when max(ii.due_date) <= date(now()) then 'Posted'
                             else 'Scheduled'
                        end as status,
                        null as error,
                        ii.amount,
                        ii.discount,
                        ii.tax
                    from invoice_item ii
                        left join invoice i on ii.invoice_id = i.id
                        left join membership mem on ii.product_id = mem.id
                        left join plan p on mem.plan_id = p.id
                    where ii.user_id = {user_id}
                        and ii.location_id = {location_id}
                    group by i.id, i.description, ii.due_date, ii.create_datetime, i.invoice_type_id, i.product_category_type_id, ii.amount, ii.discount, ii.tax),
                payment_entries as
                    (select mph.id,
                        case when mph.payrix_transaction_status is null and mph.payrix_onboarding_status in (1) then mph.scheduled_date
                             when mph.payrix_transaction_status in (7) then mph.scheduled_date
                            else mph.processed_date
                        end as activity_date,
                        case when mph.payrix_transaction_status is null and mph.payrix_onboarding_status in (1) then 'true'
                            else 'false'
                        end as can_cancel,
                        'payment' as instrument_type,
                        case when mpm.method in (1, 2, 3, 4, 5)
                                 then concat('CC ', pmt.name, ' ', mpm.last_4_digits_card)
                              when mpm.method in (8, 9, 10, 11)
                                 then concat(pmt.name, ' ', mpm.last_4_digits_account)
                              when mpm.method in (7)
                                 then concat('DC', pmt.name, ' ', mpm.last_4_digits_card)
                              when mpm.id is null and mph.payment_method_id = 0
                                 then "Cash"
                              when mpm.id is null
                                 then 'Missing card / ach details'
                        end as payment_method,
                        mph.notes as description,
                        case when mph.payment_transaction_type_id in (1, 3) and ifnull(mph.processed_by, 0) = 0 then 'Payments Recurring'
                             when mph.payment_transaction_type_id in (1, 3) and mph.processed_by <> 0 then 'Payments'
                             when mph.payment_transaction_type_id = 2 then 'Payments Refund'
                        end as type,
                        case when mph.payment_transaction_type_id in (1, 3) and mph.payrix_transaction_status in (1, 2, 3, 4, 7) then round(mph.total_amount,2)
                             when mph.payment_transaction_type_id = 2 and mph.payrix_transaction_status in (0, 1, 2, 3, 4, 7) then -round(mph.total_amount,2)
                             when mph.payrix_transaction_status is null and mph.payrix_onboarding_status in (1) then round(mph.total_amount,2)
                        end as payment,
                        case when mph.payment_transaction_type_id in (1, 3) and mph.payrix_transaction_status in (0, 1, 3, 4) then -round(mph.total_amount,2)
                             when mph.payment_transaction_type_id = 2 and mph.payrix_transaction_status in (0, 1, 3, 4) then round(mph.total_amount,2)
                             when mph.payrix_transaction_status in (2, 5) then 0
                             when mph.payrix_transaction_status is null and mph.payrix_onboarding_status in (1) then -round(mph.total_amount,2)
                        end as total,
                        0 as charges,
                        case when mph.payrix_transaction_status in (2, 5) then 'Failed'
                             when mph.payrix_transaction_status in (4) then 'Processed'
                             when mph.payrix_transaction_status in (7) then 'Cancelled'
                             when mph.payrix_transaction_status in (0, 1, 3) then 'Processing'
                             when mph.payrix_transaction_status is null and mph.payrix_onboarding_status in (1) then 'Scheduled'
                        end as status,
                        case when mph.payrix_transaction_status in (2, 5) and locate('{{', mph.payrix_transaction_error) = 1
                            then cast(replace(replace(replace(replace(payrix_transaction_error, 'null', 'None'), 'None', '''None'''), '''', '"'), '"To"', 'To') as JSON)
                            else cast(concat('{{"msg": "', mph.payrix_transaction_error, '" }}') as JSON)
                        end as error,
                        null as amount,
                        null as discount,
                        null as tax
                    from member_payment_history_v2 mph
                        left join member_payment_method mpm on mpm.id = mph.payment_method_id
                        left join _ref_payrix_payment_method_type pmt on pmt.id = mpm.method
                    where mph.user_id = {user_id}
                      and mph.location_id = {location_id}
                    ),
                union_data as
                    (select ie.id, ie.activity_date, ie.instrument_type, ie.type, ie.description, ie.status, ie.charges, null as payment, null as payment_method, 'false' as can_cancel, ie.total, ie.error, ie.amount, ie.discount, ie.tax from invoice_entries ie
                    union all
                    select pe.id, pe.activity_date, pe.instrument_type, pe.type, pe.description, pe.status, null as charges, pe.payment, pe.payment_method, can_cancel, pe.total, pe.error, pe.amount, pe.discount, pe.tax from payment_entries pe),
                ordered_data as
                    (select id,
                           activity_date,
                           instrument_type,
                           type, description,
                           status,
                           charges,
                           payment,
                           payment_method,
                           can_cancel,
                           total,
                           error,
                           row_number() over (order by activity_date, id) as order_by,
                           amount,
                           discount,
                           tax
                    from union_data)
                    select null as id, (select min(activity_date) from union_data) as activity_date, null as instrument_type, null as type, null as description, 'Starting Balance' as status, 0 as charges, 0 as payment, payment_method, null as can_cancel, 0 as total, null as msg, 0 as balance, 0 as order_by, amount, discount, tax from payment_entries
                    union
                    select id,
                           activity_date,
                           instrument_type,
                           type, description,
                           status,
                           charges,
                           payment,
                           payment_method,
                           can_cancel,
                           total,
                           (select json_extract(error, '$.msg')) as msg,
                            sum(total) over (order by order_by) as balance,
                           order_by,
                           amount,
                           discount,
                           tax
                    from ordered_data"""
        result = db.session.execute(text(sql))
        results_as_dict = result.mappings().all()
        return results_as_dict


    def __init__(self, user_id: int, location_id: int, start_date: datetime):
        self.user_id = user_id
        self.location_id = location_id
        self.start_date = start_date

    def save(self):
        db.session.add(self)

    def save_and_commit(self):
        self.save()
        db.session.commit()
