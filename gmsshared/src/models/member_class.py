from datetime import datetime, date
from typing import Optional, Self, List, Tuple
from sqlalchemy import or_
from sqlalchemy import (
    DateTime, Column, ForeignKey, BigInteger, SmallInteger, Boolean, text, and_, String
)
from sqlalchemy.orm import backref
from sqlalchemy.sql import func
from sqlalchemy import or_, select
from gmsshared import db
from gmsshared.src.models.membership import Membership
from gmsshared.src.models.member_profile import MemberProfile
from gmsshared.src.models.location import Location
from gmsshared.src.models.session import Class
from gmsshared.src.models.user import User
from gmsshared.src.models.user_profile import UserProfile

class MemberClass(db.Model):
    id = Column(BigInteger, nullable=False, primary_key=True)
    location_id = Column(BigInteger, ForeignKey("location.id"), nullable=False)
    class_id = Column(BigInteger, ForeignKey("class.id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("member_profile.user_id"), nullable=False)
    membership_id = Column(BigInteger, ForeignKey("membership.id"), nullable=True)
    class_time = Column(DateTime, nullable=False)
    member_registered_time = Column(DateTime, nullable=False, server_default=func.now())
    member_waitlist = Column(SmallInteger, nullable=True, server_default='0')
    member_cancelled_time = Column(DateTime, nullable=True)
    member_checked_in_time = Column(DateTime, nullable=True)
    cancel_rebook_email_time = Column(DateTime, nullable=True)
    cancel_reason = Column(String(200), nullable=True)
    cancelled_by = Column(BigInteger, nullable=True)

    create_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(type_=DateTime, nullable=False, server_default=func.now(), onupdate=datetime.utcnow)

    no_show_credited = Column(type_=Boolean, nullable=True, server_default=text('false'))
    member = db.relationship(MemberProfile, backref="bookings")
    clazz = db.relationship('Class')
    membership = db.relationship(Membership, backref="bookings")
    location = db.relationship(Location)

    @classmethod
    def find_by_id(cls, location_id: int, class_id: int, booking_id: int) -> Optional[Self]:
        return cls.query.filter_by(location_id=location_id, class_id=class_id, id=booking_id).first()

    @classmethod
    def find_by_class_and_booking_id(cls, location_id: int, class_id: int, booking_id: int) -> Optional[Self]:
        return cls.query.filter_by(location_id=location_id, class_id=class_id, id=booking_id).first()

    @classmethod
    def find_by_class_and_class_time(cls, location_id: int, class_id: int, class_time: datetime, cancelled: bool=False) -> Optional[List[Self]]:
        if cancelled is None or cancelled == False:
            return cls.query.filter(and_(cls.location_id==location_id, cls.class_id==class_id, cls.class_time==class_time,
                                        cls.member_cancelled_time==None)).all()
        else:
            return cls.query.filter(and_(cls.location_id==location_id, cls.class_id==class_id, cls.class_time==class_time)).all()

    @classmethod
    def get_current_waitlist(cls, location_id: int, class_id: int, class_time: datetime):
        result = cls.query.filter(
            and_(
                cls.location_id == location_id,
                cls.class_id == class_id,
                cls.class_time == class_time,
                cls.member_waitlist > 0
            )
        ).with_entities(func.max(cls.member_waitlist)).scalar()

        return result if result is not None else 0

    @classmethod
    def fetch_member_from_waitlist(cls, location_id: int, class_id: int, class_time: datetime):
        member = cls.query.filter(
            and_(
                cls.location_id == location_id,
                cls.class_id == class_id,
                cls.class_time == class_time,
                cls.member_waitlist > 0
            )
        ).order_by(
            cls.member_waitlist.asc()
        ).first()
        return member

    @classmethod
    def find_by_class_and_date_range(cls, location_id: int, class_id: int, start_time: datetime | date,
                                     end_time: datetime | date, include_waitlist=True) -> Optional[List[Self]]:
        sql = f"""select * from member_class mc
                  where mc.location_id = {location_id} and mc.class_id = {class_id} 
                    and convert(mc.class_time, date) >= convert('{start_time}', date) 
                    and convert(mc.class_time, date) <= convert('{end_time}', date)
                    and mc.member_cancelled_time is null"""

        if not include_waitlist:
            sql += " and mc.member_waitlist = 0"

        return cls.query.from_statement(text(sql)).all()

    @classmethod
    def find_no_showed_bookings(cls):
        return cls.query.join(cls.location).filter(
            cls.class_time < func.now(),
            cls.no_show_credited == False,
            cls.member_checked_in_time.is_(None),
            cls.member_cancelled_time.is_(None),
            cls.membership_id.isnot(None),
            cls.location.has(
                and_(
                    Location.no_show_credit == True,
                    or_(
                        Location.no_show_enabled_datetime.is_(None),
                        Location.no_show_enabled_datetime <= cls.class_time
                    )
                )
            )
        ).all()


    @classmethod
    def find_waitlisted_members_by_class_and_date_range(cls, location_id: int, class_id: int, start_time: datetime | date,
                                     end_time: datetime | date):
        sql = f"""select * from member_class mc
                          where mc.location_id = {location_id} and mc.class_id = {class_id} 
                            and convert(mc.class_time, date) >= convert('{start_time}', date) 
                            and convert(mc.class_time, date) <= convert('{end_time}', date)
                            and mc.member_cancelled_time is null
                            and mc.member_waitlist > 0"""
        return cls.query.from_statement(text(sql)).all()

    @classmethod
    def find_by_date_range_and_member_id(cls, location_id: int, user_id: int, start_time: datetime = None, end_time: datetime = None) -> Optional[List[Self]]:
        if start_time is None:
            start_time = datetime.strptime('2024-01-01', '%Y-%m-%d')
        if end_time is None:
            end_time = datetime.strptime('2030-01-01', '%Y-%m-%d')
        return cls.query.filter(and_(cls.location_id==location_id, cls.class_time >= start_time,
                                        cls.class_time <= end_time, cls.user_id == user_id if user_id is not None else True)).all()

    @classmethod
    def find_bookings_by_class_and_time(cls, location_id: int, class_id: int, class_time: datetime) -> List[Self]:
        return cls.query.filter(and_(cls.location_id == location_id, cls.class_id == class_id,
                cls.class_time == class_time,
                cls.member_cancelled_time == None)).all()

    @classmethod
    def find_waitlisted_bookings_by_class_and_time(cls, location_id: int, class_id: int, class_time: datetime):
        return cls.query.filter(and_(cls.location_id == location_id, cls.class_id == class_id,
                                     cls.class_time == class_time, cls.member_waitlist >= 1,
                                     cls.member_cancelled_time == None)).all()

    @classmethod
    def find_by_class_and_member_id(cls, location_id: int, class_id: int, user_id: int) -> Optional[List[Self]]:
        return cls.query.filter(and_(cls.location_id==location_id, cls.class_id==class_id, cls.user_id==user_id)).all()

    @classmethod
    def find_all(cls, location_id: int, class_id: int) -> Optional[List[Self]]:
        return cls.query.filter(and_(cls.location_id==location_id, cls.class_id==class_id)).all()

    @classmethod
    def find_by_class_and_class_list(cls, location_id: int, class_id: int, class_list: Tuple) -> List[Self]:
        if len(class_list) == 1:
            where_clause = f"mc.class_time = '{class_list[0]}'"
        else:
            where_clause = f"mc.class_time in {class_list}"
        sql = f"""select * from member_class mc
                  where mc.location_id = {location_id} and mc.class_id = {class_id} and {where_clause}
                     and mc.member_cancelled_time is null"""
        return (cls.query.from_statement(text(sql)).all())

    @classmethod
    def find_attendance_by_class_time_and_date_range(cls, location_id: int, start_time: datetime = None, end_time: datetime = None) -> List[Self]:
        sql = (f"""
            select mc.class_id, 
            mc.class_time,
            count(case when mc.member_waitlist = 0 then mc.user_id end) as attendance_count,
            count(case when mc.member_waitlist > 0 then mc.user_id end) as waitlist_count,
            (
                select group_concat(user_id)
                from member_class m1
                where m1.class_id = mc.class_id
                and mc.class_time = m1.class_time
                and m1.member_waitlist = 0
                and m1.member_cancelled_time is null
            ) as attendee_list
            from member_class mc
            where mc.class_time between '{start_time}' and '{end_time}' 
            and mc.location_id = {location_id} 
            and mc.member_cancelled_time is null
            group by mc.class_id, mc.class_time
        """)
        result = db.session.execute(text(sql))
        results_as_dict = result.mappings().all()
        return results_as_dict

    def save(self):
        db.session.add(self)

    def save_and_commit(self):
        self.save()
        db.session.commit()

    @classmethod
    def bulk_update(cls, obj):
        db.session.add_all(obj)
        db.session.commit()
