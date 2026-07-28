from datetime import datetime, date, timedelta
from typing import Optional, List

from pydantic import BaseModel, Field, HttpUrl, model_validator, field_validator

from plans_classes_service.plans.dtos.plans_requests import LocationPath
from gmsshared.src.util.enums import ClassByWeekDaysEnum, ClassFrequencyEnum


class ClassPath(LocationPath):
    class_id: Optional[int] = Field(None, description="ID of the session. Optional for opengym checkin")


class BookingPath(LocationPath):
    class_id: int = Field(..., title="Class ID")
    booking_id: int = Field(..., title="Booking ID", description="ID of booking.")


class BookingClassPath(ClassPath, BookingPath):
    pass


class SessionFilter(BaseModel):
    start_date: datetime = Field(..., description="Format: YYYY-MM-DD HH:MM:SS")
    end_date: Optional[datetime] = Field(None, description="Format: YYYY-MM-DD HH:MM:SS")
    member_id: Optional[int] = Field(
        None,
        description="If member_id is present, returns a list of classes eligible by member_id",
    )

    @field_validator("end_date")
    def endtime_less_than_starttime(cls, v, info):
        if v < info.data["start_date"]:
            raise Exception("end_date should be greater than start_date")

        if (v - info.data["start_date"]) == timedelta(weeks=2):
            raise Exception("end_date and start_date diff should not be greater than 2 weeks")
        return v


class MemberFilter(BaseModel):
    member_id: Optional[int] = Field(None, description="ID of the member to use on the query filter.")


class ClassFilter(BaseModel):
    class_time: Optional[datetime] = Field(None, description="Only either member_id or class_time, not both.")


class MemberClassFilter(BaseModel):
    member_id: Optional[int] = Field(None, description="Only either member_id or class_time, not both.")
    class_time: Optional[datetime] = Field(None, description="Only either member_id or class_time, not both.")


class BookingFilter(BaseModel):
    member_id: Optional[int] = Field(None, description="Member_id")
    start_date: Optional[datetime] = Field(None, description="Format: YYYY-MM-DD HH:MM:SS")
    end_date: Optional[datetime] = Field(None, description="Format: YYYY-MM-DD HH:MM:SS")


class CreateClassRequest(BaseModel):
    location_id: int = Field(..., description="ID of the location")
    location_type_id: int = Field(
        ...,
        description="ID for type of the location (i.e. physical, virtual, both...).",
    )
    room_id: int = Field(..., description="ID of the room where the session takes place.")
    name: str = Field(..., description="Name of the session.")
    description: Optional[str] = Field(None, description="Description of the session.")
    main_coach_id: Optional[int] = Field(None, description="ID of the main coach of the session.")
    assistant_coach_id: Optional[int] = Field(None, description="ID of the assistant coach of the session.")
    class_type_id: int = Field(
        ...,
        description="ID for type of the session (i.e. bootcamp, cardio, crossfit, etc).",
    )
    registration_start_time_type_id: Optional[int] = Field(
        None,
        description="ID for the type of time for starting registration (i.e. immediately, at start time, minutes, etc).",
    )
    registration_start_time_value: Optional[int] = Field(
        None,
        description="Value of registration start time (related to type), i.e. 2 (weeks before...).",
    )
    registration_end_time_type_id: Optional[int] = Field(
        None,
        description="ID for the type of time for ending registration (i.e. immediately, at start time, etc).",
    )
    registration_end_time_value: Optional[int] = Field(
        None,
        description="Value of registration end time (related to type), i.e. 3 (hours before...).",
    )
    late_cancellation_time_type_id: Optional[int] = Field(
        None,
        description="ID for the type of time for late cancellation (i.e. immediately, at start time, etc).",
    )
    late_cancellation_time_value: Optional[int] = Field(
        None,
        description="Value of late cancellation time (related to type), i.e. 1 (hours before...).",
    )
    attendance_cap: int = Field(..., description="Max capacity of attendants for this class.")
    all_day_event: bool = Field(..., description="Informs if event is available for all day.")
    start_time: datetime = Field(..., description="Datetime of beginning of sessions")
    end_time: datetime = Field(None, description="Datetime of end of sessions")
    by_weekday: Optional[str] = Field(
        None,
        description='Comma separated string of weekdays for a weekly recurrence. Ex: "MO,TU,WE,TH,FR,SA,SU"',
    )
    recurrence_end_date: Optional[date] = Field(None, description="Recurrrence end date")
    frequency: Optional[int] = Field(
        ClassFrequencyEnum.WEEKLY.value,
        description="Frequency of the session. 1=Hourly, 2=Daily, 3=Weekly, 4=Monthly. Only 3=Weekly is honored for now",
    )
    recurring: bool = Field(..., description="Informs if session is available as a recurring event.")
    private_training: bool = Field(
        False,
        description="Informs if session is available as a private training. Default is False",
    )
    class_url: Optional[HttpUrl] = None
    waitlist: Optional[bool] = Field(
        None,
        description="Informs if waitlist is available for session (after fully booked).",
    )
    no_show_credit: Optional[bool] = Field(None, description="Informs if no show credit is enabled or not")
    plans: List[int] = Field([], description="List of ID related to plans linked to this session.")
    member_id: Optional[int] = Field(
        None,
        description="Member_id is optional and only needed if Private Training is true",
    )
    class_access_groups: Optional[List[int]] = []

    @field_validator("frequency")
    def only_weekly_frequency_allowed(cls, v, info):
        if v != ClassFrequencyEnum.WEEKLY.value:
            raise Exception(f"only weekly ({ClassFrequencyEnum.WEEKLY.value}) is allowed at this time")
        if ("by_weekday" not in info.data) or (info.data["by_weekday"] is None):
            raise Exception("by_weekday not defined")
        by_weekday = info.data["by_weekday"].split(",") if "by_weekday" in info.data else None
        if v == ClassFrequencyEnum.WEEKLY.value and (by_weekday is None):
            raise Exception("by_weekday is required when frequency is set")
        if (
            v == ClassFrequencyEnum.WEEKLY.value
            and len(by_weekday) == 0
            or len(set([d.value for d in ClassByWeekDaysEnum]).intersection(by_weekday)) == 0
        ):
            raise Exception("at least one day in by_weekday is required when frequency is set")
        return v

    @field_validator("recurring")
    def need_either_endtime_or_frequency(cls, v, info):
        if not v:
            info.data["frequency"] = None
            info.data["by_weekday"] = None
        if (not v) and ("end_time" in info.data and info.data["end_time"] is None) or ("end_time" not in info.data):
            raise Exception("end_time not defined")
        if v:
            if ("frequency" in info.data and info.data["frequency"] is None) or ("frequency" not in info.data):
                raise Exception("frequency not defined")
            if ("by_weekday" not in info.data) or (info.data["by_weekday"] is None):
                raise Exception("by_weekday not defined")
            by_weekday = info.data["by_weekday"].split(",") if "by_weekday" in info.data else None
            if len(by_weekday) == 0 or len(set([d.value for d in ClassByWeekDaysEnum]).intersection(by_weekday)) == 0:
                raise Exception("at least one day in by_weekday is required for a recurring session")
        return v

    @field_validator("end_time")
    def endtime_less_than_starttime(cls, v, info):
        if ("start_time" in info.data) and v <= info.data["start_time"]:
            raise Exception("end_time should be greater than start_time")
        return v

    @field_validator("recurrence_end_date")
    def attach_time_to_recurrence_end_date(cls, v, info):
        session_time = info.data["end_time"]
        if v is not None:
            return datetime.combine(v, session_time.time())
        return v

    @field_validator("member_id")
    def private_training_requires_member_id(cls, v, info):
        private_training = info.data["private_training"]
        if private_training and v is None:
            raise Exception("member_id cannot be null for private training")
        return v


class UpdateClassRequest(CreateClassRequest):
    class_id: int = Field(..., description="ID of the session")
    class_cancellation_time: Optional[datetime] = Field(
        None,
        description="Time when session was cancelled. If different from null, session won't be available anymore.",
    )
    update_type: Optional[int] = Field(1, description="Only this event = 1 (default), This and following events = 2")
    class_time: Optional[datetime] = Field(
        None, description="The datetime of the event from which the update is happening"
    )


class DeleteClassQuery(BaseModel):
    class_cancellation_time: Optional[datetime] = Field(
        None,
        description="Time when session was cancelled. If different from null, session won't be available anymore.",
    )
    update_type: Optional[int] = Field(
        1,
        description="Only this event = 1 (default), This and following events = 2, All events =3",
    )
    class_time: datetime = Field(None, description="The datetime of the event from which the delete is happening")


class Booking(BaseModel):
    location_id: int = Field(..., description="ID of the location where the session takes place")
    class_id: Optional[int] = Field(None, description="ID of the session to be booked")
    member_id: int = Field(..., description="ID of the member on waitlist, requesting this session")


class BookClassRequest(Booking):
    class_time: Optional[datetime] = Field(
        None,
        description="The datetime for the session (class) the member is registering for",
    )
    direct_check_in: Optional[bool] = Field(
        default=False,
        description="Use this flag to indicate if the members is directly checked in without registration",
    )
    opengym_checkin: Optional[bool] = Field(None, description="OpenGym Checkin")
    force_register: Optional[bool] = Field(
        default=False,
        description="Use this flag to register/direct check_in for class even if reached weekly session limit ",
    )

    @model_validator(mode="after")
    def validate_class_id_for_opengym(self):
        if not self.opengym_checkin:
            if self.class_id is None:
                raise ValueError("class_id is mandatory when opengym_checkin is False or not set")
            if self.class_time is None:
                raise ValueError("class_time is mandatory when opengym_checkin is False or not set")
        return self


class UpdateBookingRequest(BaseModel):
    in_waitlist: bool = Field(
        None,
        title="in waitlist",
        description="Describes whether a member is in waitlist",
        alias="member_waitlist",
    )
    member_checked_in_time: Optional[datetime] = Field(
        None,
        title="member check in time",
        description="Time at which the member is checked for session. Note:\
                                                    NULL value will remove any previous checked-in time saved.",
    )
    member_cancelled_time: Optional[datetime] = Field(
        None,
        title="member session cancel time",
        description="Time at which the member cancelled attendance to this\
                                                    session. Note: NULL value will remove any previous checked-in time \
                                                    saved.",
    )
    cancel_reason: Optional[str] = Field(None, description="Reason for cancellation")


class AccessTimes(BaseModel):
    weekday: Optional[int] = Field(None, description="Day of the week (MON=1, TUE=2... SUN=7)")
    start_time: Optional[str]  = Field(None, description="Start time in 24 hr format")
    end_time: Optional[str] = Field(None, description="End time in 24 hr format")


class CreateClassAccessGroupRequest(BaseModel):
    location_id: int = Field(..., description="ID of the location")
    name: str = Field(..., description="Session access name")
    active: Optional[bool] = True
    plan_formats: Optional[List[int]] = Field(description="List of ID related to plan formats", default=[])
    doors: Optional[List[int]] = Field(description="List of ID related to doors", default=[])
    door_access_access_times_flag: Optional[bool] = Field(False, description="Access Times toggle")
    door_access_access_times: Optional[List[AccessTimes]] = Field(None, description="List of access times")


class UpdateClassAccessGroupRequest(CreateClassAccessGroupRequest):
    id: int = Field(..., description="ID of the class")
    plans: Optional[List[int]] = Field(description="List of ID related to plans", default=[])
