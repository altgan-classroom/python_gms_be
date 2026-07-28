from datetime import datetime, timedelta
from typing import Optional, Self, List

from dateutil.rrule import rrulestr
from sqlalchemy import (
    Boolean, DateTime, Column, Integer, String, ForeignKey, BigInteger, and_, Date, text
)
from sqlalchemy.orm import Relationship
from sqlalchemy.sql import func

from gmsshared import db
from gmsshared.src.models._ref_registration_times_type import _RefRegistrationTimesType
from gmsshared.src.models._ref_class_type import _RefClassType
from gmsshared.src.models._ref_timezone_type import _RefTimezoneType
from gmsshared.src.models.location import Location
from gmsshared.src.models.room import Room
from gmsshared.src.models.user import User
from gmsshared.src.util.enums import ClassByWeekDaysEnum, ClassFrequencyEnum
from gmsshared.src.util.validators import to_local, to_utc

class_plan = db.Table("class_plan",
                      Column("class_id", BigInteger, ForeignKey("class.id"), primary_key=True),
                      Column("plan_id", BigInteger, ForeignKey("plan.id"), primary_key=True))


class Class(db.Model):
    id = Column(BigInteger, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(255), nullable=True)
    attendance_cap = Column(Integer, nullable=False)
    all_day_event = Column(Boolean, nullable=False, server_default=str(int(False)))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    recurring = Column(Boolean, nullable=False, server_default=str(int(False)))
    private_training = Column(Boolean, nullable=True, server_default=str(int(False)))
    frequency = Column(Integer, nullable=True)
    by_weekday = Column(String(60), nullable=True)
    recurrence_end_date = Column(DateTime, nullable=True)
    exdate = Column(String(512), nullable=True)
    class_url = Column(String(255), nullable=True)
    waitlist = Column(Boolean, nullable=True, server_default=str(int(True)))
    no_show_credit = Column(Boolean, nullable=True, default=False)
    create_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(type_=DateTime, nullable=False, server_default=func.now(), onupdate=datetime.utcnow)

    # A Class can belong to a Location
    location_id = Column(BigInteger, ForeignKey("location.id"), nullable=False)

    # A Class will be conducted in a room
    room_id = Column(BigInteger, ForeignKey("room.id"), nullable=False)

    # A Class can have a main coach
    main_coach_id = Column(BigInteger, ForeignKey("user.id"), nullable=True)
    main_coach = Relationship("User", foreign_keys=[main_coach_id])

    # A Class can have an assistant coach
    assistant_coach_id = Column(BigInteger, ForeignKey("user.id"), nullable=True)
    assistant_coach = Relationship(User, foreign_keys=[assistant_coach_id])

    # A Class can be of a certain type
    location_type_id = Column(Integer, ForeignKey("_ref_location_type.id"), nullable=False)

    # A Class can be of a certain type
    class_type_id = Column(Integer, ForeignKey("_ref_class_type.id"), nullable=False)

    # A Class will have a registration start time type
    registration_start_time_type_id = Column(Integer, ForeignKey("_ref_registration_times_type.id"), nullable=True)
    registration_start_time_value = Column(Integer, nullable=True)

    # A Class will have a registration end time type
    registration_end_time_type_id = Column(Integer, ForeignKey("_ref_registration_times_type.id"), nullable=True)
    registration_end_time_value = Column(Integer, nullable=True)

    # A Class will have a late cancellation time type
    late_cancellation_time_type_id = Column(Integer, ForeignKey("_ref_registration_times_type.id"), nullable=True)
    late_cancellation_time_value = Column(Integer, nullable=True)

    plans = Relationship("Plan", secondary=class_plan, backref="classes")

    class_cancellation_time = Column(type_=DateTime, nullable=True, server_default=None)

    @property
    def duration(self):
        return (self.end_time - self.start_time).seconds

    @property
    def sess_start_time(self):
        return self.start_time.time()

    @property
    def sess_end_time(self):
        return self.end_time.time()

    def events_list(self, start_date: datetime, end_date: datetime) -> List[datetime]:
        if self.start_time >= start_date:
            start = self.start_time
        else:
            start = start_date

        if self.recurrence_end_date is not None and self.recurrence_end_date < end_date:
            end = self.recurrence_end_date
        elif self.recurrence_end_date is not None and self.recurrence_end_date > end_date:
            end = end_date
        else:
            end = end_date

        if self.recurring:
            # First convert UTC to local time because weekdays need to align with local dates
            start, end = datetime.strptime(to_local(start), "%Y-%m-%d %H:%M"), datetime.strptime(to_local(end), "%Y-%m-%d %H:%M")
            stime = datetime.strptime(to_local(self.start_time), "%Y-%m-%d %H:%M")

            rule = f"FREQ={ClassFrequencyEnum(self.frequency).name};BYDAY={self.by_weekday}"
            rr = rrulestr(rule, dtstart=start)
            rr._until = end
            dates_list = list(rr)

            class_list = [datetime.combine(class_date.date(), stime.time()) for class_date in dates_list]
            exdates = self.exdate.split(',') if self.exdate is not None else []
            local_exdates = [datetime.combine(datetime.strptime(y, '%Y-%m-%d'), stime.time()) for y in exdates]

            event_list = sorted(list(set(class_list) - set(local_exdates)))
            # We are done generating recurrence events, convert local back to UTC
            event_list = [to_utc(event) for event in event_list]

            return event_list

        if start <= self.start_time and end >= self.start_time:
            return [self.start_time]

        return []

    def is_class_valid(self, class_time: datetime) -> bool:
        return class_time in self.events_list(class_time, class_time)

    def add_exdate(self, class_time: datetime) -> None:
        exdate = [] if ((self.exdate is None) or (self.exdate == '')) else self.exdate.split(',')
        # Make sure we exclude the right date by converting to_local first
        date_to_exclude = datetime.strftime(datetime.strptime(to_local(class_time), "%Y-%m-%d %H:%M"), '%Y-%m-%d')
        exdate.append(date_to_exclude)
        exdate.remove('None') if 'None' in exdate else None
        self.exdate = ','.join(set(exdate))

    @classmethod
    def find_by_id(cls, id: int) -> Optional[Self]:
        return cls.query.filter_by(id=id).first()

    @classmethod
    def find_by_location(cls, location_id: int) -> List[dict]:
        return cls.query.filter_by(location_id=location_id, class_cancellation_time=None).all()

    @classmethod
    def find_by_location_and_start_date(cls, location_id: int, start_date: datetime) -> List[dict]:
        return cls.query.filter(and_(
            cls.location_id == location_id, cls.start_time <= start_date, cls.class_cancellation_time == None))

    @classmethod
    def find_by_location_and_date(cls, location_id: int, start: datetime.date, end: datetime.date) -> List[Self]:
        sql = f"""select * from class s where s.location_id = {location_id} 
                      and ('{start}' between s.start_time and if(ifnull(s.recurring, 0) = 0, s.end_time, ifnull(s.recurrence_end_date, '2030-01-01')))
                      and class_cancellation_time is null
                  union
                  select * from class s where s.location_id = {location_id} 
                      and (s.start_time between '{start}' and '{end}')
                      and class_cancellation_time is null"""
        return (cls.query.from_statement(text(sql)).all())

    @classmethod
    def find_by_location_and_class(cls, location_id: int, class_id: int) -> Optional[Self]:
        return cls.query.filter_by(location_id=location_id, id=class_id, class_cancellation_time=None).first()

    def save(self):
        db.session.add(self)

    def save_and_commit(self):
        self.save()
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
