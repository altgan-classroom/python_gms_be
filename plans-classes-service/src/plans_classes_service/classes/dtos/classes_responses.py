from datetime import datetime, date
from typing import Optional, List, Any

from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    BeforeValidator,
    AfterValidator,
    field_validator,
)
from typing_extensions import Annotated

from gmsshared.src.util.validators import (
    validate_door, validate_plans,
    to_local,
    validate_recurrence_end_date,
    validate_class_access_group_formats,
    validate_class_access_groups,
    validate_class
)
from plans_classes_service.classes.dtos.classes_requests import AccessTimes

class SessionResponse(BaseModel):
    location_id: int = Field(..., description="ID of the location where the session(s) take(s) place.")
    room_id: int = Field(..., description="ID of the Room where the session(s) take(s) place.")
    class_id: int = Field(..., alias="id", description="ID of the session.")
    name: str = Field(..., description="Name of the session.")
    description: Optional[str] = Field(None, description="Description of the session.")
    main_coach_id: Optional[int] = Field(None, description="ID of the main coach for the session.")
    assistant_coach_id: Optional[int] = Field(None, description="ID of the assistant coach for the session.")
    class_type_id: int = Field(..., description="ID for the type of session.")
    attendance_cap: int = Field(..., description="Maximum attendance capacity for the session.")
    current_attendance: int = Field(
        None,
        description="Current attendance for the session, related to attendance capacity.",
    )
    current_waitlist: int = Field(None, description="Current members in waitlist for the session")
    all_day_event: bool
    start_time: Annotated[datetime | str, AfterValidator(to_local)] = Field(...)
    end_time: Annotated[Optional[datetime | str], AfterValidator(to_local)] = Field(...)
    session_start_time: Optional[Any] = Field(None, description="Start time of the session.")
    session_end_time: Optional[Any] = Field(None, description="End time of the session.")
    by_weekday: Optional[str] = Field(
        None,
        description='Comma separated string of weekdays for a weekly recurrence. Ex: "MO,TU,WE,TH,FR,SA,SU"',
    )
    recurrence_end_date: Annotated[Optional[date], BeforeValidator(validate_recurrence_end_date)] = Field(
        None, description="Recurrrence end date"
    )
    frequency: Optional[int] = Field(
        None,
        description="Frequency of the session. 1=Hourly, 2=Daily, 3=Weekly, 4=Monthly. Only 3=Weekly is honored for now",
    )
    recurring: bool = Field(False, description="Indicates whether the session is recurring or not.")
    private_training: Optional[bool] = Field(
        False, description="Indicates whether the session is private training or not."
    )
    location_type_id: int = Field(..., description="ID for the type of location (physical, virtual, both...).")
    class_url: Optional[HttpUrl | str] = None
    waitlist: Optional[bool] = Field(None, description="Indicates whether the session has a waitlist or not.")
    no_show_credit: Optional[bool] = Field(None, description="Indicates whether no show credit is enabled or not")
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
    plans: Annotated[List[int], BeforeValidator(validate_plans)] = Field(
        [], description="Plans (memberships) linked to this session."
    )
    class_access_groups : Annotated[List[int], BeforeValidator(validate_class_access_groups)] = Field(
        [], description="Class access groups linked to this session.")
    attendees: List[int] = Field([], description="IDs of attendees (members) linked to this session")
    class_cancellation_time: Optional[datetime] = Field(
        None,
        description="Time when session was cancelled. If different from null, session won't be available anymore.",
    )
    booking_allowed: bool = Field(
        None,
        description="Shows if member is allowed to book this class, based on current membership, capacity, and so on.",
    )
    booking_allowed_reason_type_id: Optional[int] = Field(None, description="ID for the type of reason member can't book a class")

    class Config:
        from_attributes = True

    @field_validator("session_start_time")
    def derive_session_start(cls, v, info):
        return str(datetime.strptime(info.data["start_time"], "%Y-%m-%d %H:%M").time())

    @field_validator("session_end_time")
    def derive_session_end(cls, v, info):
        return str(datetime.strptime(info.data["end_time"], "%Y-%m-%d %H:%M").time())


class SessionList(BaseModel):
    classes: List[SessionResponse]


class BookingResponse(BaseModel):
    booking_id: Optional[int] = Field(None, description="ID of the booking", alias="id")
    cancellation_time: Annotated[datetime | str | None, AfterValidator(to_local)] = Field(
        None,
        description="Time the booking was cancelled",
        alias="member_cancelled_time",
    )
    location_id: int = Field(..., description="Location ID")
    class_id: int = Field(..., description="Class ID")
    user_id: int = Field(..., description="ID of the member")
    first_name: Optional[str] = Field(None, description="First Name of the member")
    last_name: Optional[str] = Field(None, description="Last Name of the member")
    in_waitlist: int = Field(
        0,
        description="Indicates whether member is in waitlist",
        alias="member_waitlist",
    )
    member_checked_in_time: Annotated[datetime | str | None, AfterValidator(to_local)] = Field(
        None, description="Time at which the member is checked in"
    )
    member_registered_time: Annotated[datetime | str, AfterValidator(to_local)] = Field(
        ..., description="Time at which the member was registered for session"
    )
    class_time: Annotated[datetime | str, AfterValidator(to_local)] = Field(
        ..., description="Time at which the session takes place"
    )
    cancel_reason: Optional[str] = Field(None, description="Cancellation reason")

    class Config:
        from_attributes = True

class ClassAccessGroupResponse(BaseModel):
    id: int
    name: str
    active: bool
    class_access_group_formats: Annotated[List[int], BeforeValidator(validate_class_access_group_formats)] = Field(
        [], description="Class access groups formats linked to this session."
    )
    plans: Annotated[List[int], BeforeValidator(validate_plans)] = Field(
        [], description="Plans (memberships) linked to this session."
    )
    classes: Annotated[List[int], BeforeValidator(validate_class)] = Field(
        [], description="Classes linked to class access group"
    )

    doors: Annotated[List[int], BeforeValidator(validate_door)] = Field(
        [], description="Doors linked to class access group", alias="class_access_group_doors"
    )
    door_access_access_times_flag: Optional[bool] = Field(None, description="Access Times toggle")
    door_access_access_times: Optional[List[Optional[AccessTimes]]] = Field(None, description="List of access times")


class ClassAccessGroupList(BaseModel):
    class_accesses: List[ClassAccessGroupResponse]