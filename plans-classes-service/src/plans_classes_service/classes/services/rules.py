from datetime import datetime, timedelta
from typing import List

from gmsshared.src.util.enums import (
    ClassUpdateTypeEnum,
    SessionChangeTypeEnum,
    SessionActionTypeEnum,
    SessionChangeEmailTypeEnum,
)
from gmsshared.src.util.misc import fill_model

from gmsshared.run import create_app
from gmsshared import db
from gmsshared.src.models.session import Class
from gmsshared.src.util.validators import to_local
from gmsshared.src.util.validators import normalize_local_times
from gmsshared.src.util.enums import PlanStatusType

msg1 = "Clients will need to rebook due to changes in the date or time from their original commitment. An email will be sent to inform them of the changes and request that they rebook"
msg2 = "Sessions will be canceled because the recurrence period is being shortened or specific days are being removed from the schedule. Clients with existing bookings for these sessions will be notified of the cancellations"
msg3 = "Certain plans will no longer be eligible to book these sessions in the future. If a client with such a plan has already made a booking and you wish to cancel it, you will need to manually remove their booking"
msg4 = "The attendance cap will be reduced and enforced going forward. Current bookings may exceed this new cap. To align with the reduced cap, you will need to manually select and remove attendees from the sessions"

rule_name_1 = {
    "attr": "name",
    "recurring": False,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.UPDATE.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.UPDATE.value,
    "email": None,
    "message": None,
}
rule_name_2 = {
    "attr": "name",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.UPDATE.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.CREATE_SINGLE_AND_UPDATE_OLD_WITH_EXDATE.value,
    "email": None,
    "message": None,
}
rule_name_3 = {
    "attr": "name",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_FOLLOWING_EVENTS.value,
    "change_type": SessionChangeTypeEnum.UPDATE.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.CREATE_NEW_RECURRENCE.value,
    "email": None,
    "message": None,
}

rule_no_show_1 = {
    "attr": "no_show_credit",
    "recurring": False,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.UPDATE.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.UPDATE.value,
    "email": None,
    "message": None,
}
rule_no_show_2 = {
    "attr": "no_show_credit",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.UPDATE.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.CREATE_SINGLE_AND_UPDATE_OLD_WITH_EXDATE.value,
    "email": None,
    "message": None,
}
rule_no_show_3 = {
    "attr": "no_show_credit",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_FOLLOWING_EVENTS.value,
    "change_type": SessionChangeTypeEnum.UPDATE.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.CREATE_NEW_RECURRENCE.value,
    "email": None,
    "message": None,
}

rule_description_1 = {
    "attr": "description",
    "recurring": False,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.UPDATE.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.UPDATE.value,
    "email": None,
    "message": None,
}
rule_description_2 = {
    "attr": "description",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.UPDATE.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.CREATE_SINGLE_AND_UPDATE_OLD_WITH_EXDATE.value,
    "email": None,
    "message": None,
}
rule_description_3 = {
    "attr": "description",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_FOLLOWING_EVENTS.value,
    "change_type": SessionChangeTypeEnum.UPDATE.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.CREATE_NEW_RECURRENCE.value,
    "email": None,
    "message": None,
}

rule_class_type_1 = {
    "attr": "class_type_id",
    "recurring": False,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.UPDATE.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.UPDATE.value,
    "email": None,
    "message": None,
}
rule_class_type_2 = {
    "attr": "class_type_id",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.UPDATE.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.CREATE_SINGLE_AND_UPDATE_OLD_WITH_EXDATE.value,
    "email": None,
    "message": None,
}
rule_class_type_3 = {
    "attr": "class_type_id",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_FOLLOWING_EVENTS.value,
    "change_type": SessionChangeTypeEnum.UPDATE.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.CREATE_NEW_RECURRENCE.value,
    "email": None,
    "message": None,
}

rule_room_1 = {
    "attr": "room_id",
    "recurring": False,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.UPDATE.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.UPDATE.value,
    "email": None,
    "message": None,
}
rule_room_2 = {
    "attr": "room_id",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.UPDATE.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.CREATE_SINGLE_AND_UPDATE_OLD_WITH_EXDATE.value,
    "email": None,
    "message": None,
}
rule_room_3 = {
    "attr": "room_id",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_FOLLOWING_EVENTS.value,
    "change_type": SessionChangeTypeEnum.UPDATE.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.CREATE_NEW_RECURRENCE.value,
    "email": None,
    "message": None,
}

rule_attendance_1_add = {
    "attr": "attendance_cap",
    "recurring": False,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.ADD.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.UPDATE.value,
    "email": None,
    "message": None,
}
rule_attendance_2_add = {
    "attr": "attendance_cap",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.ADD.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.CREATE_SINGLE_AND_UPDATE_OLD_WITH_EXDATE.value,
    "email": None,
    "message": None,
}
rule_attendance_3_add = {
    "attr": "attendance_cap",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_FOLLOWING_EVENTS.value,
    "change_type": SessionChangeTypeEnum.ADD.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.CREATE_NEW_RECURRENCE.value,
    "email": None,
    "message": None,
}

rule_coach_1 = {
    "attr": "main_coach_id",
    "recurring": False,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.UPDATE.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.UPDATE.value,
    "email": None,
    "message": None,
}
rule_coach_2 = {
    "attr": "main_coach_id",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.UPDATE.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.CREATE_SINGLE_AND_UPDATE_OLD_WITH_EXDATE.value,
    "email": None,
    "message": None,
}
rule_coach_3 = {
    "attr": "main_coach_id",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_FOLLOWING_EVENTS.value,
    "change_type": SessionChangeTypeEnum.UPDATE.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.CREATE_NEW_RECURRENCE.value,
    "email": None,
    "message": None,
}

rule_asst_coach_1 = {
    "attr": "assistant_coach_id",
    "recurring": False,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.UPDATE.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.UPDATE.value,
    "email": None,
    "message": None,
}
rule_asst_coach_2 = {
    "attr": "assistant_coach_id",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.UPDATE.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.CREATE_SINGLE_AND_UPDATE_OLD_WITH_EXDATE.value,
    "email": None,
    "message": None,
}
rule_asst_coach_3 = {
    "attr": "assistant_coach_id",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_FOLLOWING_EVENTS.value,
    "change_type": SessionChangeTypeEnum.UPDATE.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.CREATE_NEW_RECURRENCE.value,
    "email": None,
    "message": None,
}

rule_allday_1 = {
    "attr": "all_day_event",
    "recurring": False,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.UPDATE.value,
    "cancel_bookings": True,
    "action": SessionActionTypeEnum.UPDATE.value,
    "email": SessionChangeEmailTypeEnum.REBOOK.value,
    "message": msg1,
}
rule_allday_2 = {
    "attr": "all_day_event",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.UPDATE.value,
    "cancel_bookings": True,
    "action": SessionActionTypeEnum.CREATE_SINGLE_AND_UPDATE_OLD_WITH_EXDATE.value,
    "email": SessionChangeEmailTypeEnum.REBOOK.value,
    "message": msg1,
}
rule_allday_3 = {
    "attr": "all_day_event",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_FOLLOWING_EVENTS.value,
    "change_type": SessionChangeTypeEnum.UPDATE.value,
    "cancel_bookings": True,
    "action": SessionActionTypeEnum.CREATE_NEW_RECURRENCE.value,
    "email": SessionChangeEmailTypeEnum.REBOOK.value,
    "message": msg1,
}

rule_start_date_1 = {
    "attr": "start_date",
    "recurring": False,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.UPDATE.value,
    "cancel_bookings": True,
    "action": SessionActionTypeEnum.UPDATE.value,
    "email": SessionChangeEmailTypeEnum.REBOOK.value,
    "message": msg1,
}
rule_start_date_2 = {
    "attr": "start_date",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.UPDATE.value,
    "cancel_bookings": True,
    "action": SessionActionTypeEnum.CREATE_SINGLE_AND_UPDATE_OLD_WITH_EXDATE.value,
    "email": SessionChangeEmailTypeEnum.REBOOK.value,
    "message": msg1,
}
rule_start_date_3 = {
    "attr": "start_date",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_FOLLOWING_EVENTS.value,
    "change_type": SessionChangeTypeEnum.UPDATE.value,
    "cancel_bookings": True,
    "action": SessionActionTypeEnum.CREATE_NEW_RECURRENCE.value,
    "email": SessionChangeEmailTypeEnum.REBOOK.value,
    "message": msg1,
}

rule_start_time_1 = {
    "attr": "start_time",
    "recurring": False,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.UPDATE.value,
    "cancel_bookings": True,
    "action": SessionActionTypeEnum.UPDATE.value,
    "email": SessionChangeEmailTypeEnum.REBOOK.value,
    "message": msg1,
}
rule_start_time_2 = {
    "attr": "start_time",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.UPDATE.value,
    "cancel_bookings": True,
    "action": SessionActionTypeEnum.CREATE_SINGLE_AND_UPDATE_OLD_WITH_EXDATE.value,
    "email": SessionChangeEmailTypeEnum.REBOOK.value,
    "message": msg1,
}
rule_start_time_3 = {
    "attr": "start_time",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_FOLLOWING_EVENTS.value,
    "change_type": SessionChangeTypeEnum.UPDATE.value,
    "cancel_bookings": True,
    "action": SessionActionTypeEnum.CREATE_NEW_RECURRENCE.value,
    "email": SessionChangeEmailTypeEnum.REBOOK.value,
    "message": msg1,
}

rule_end_time_1 = {
    "attr": "end_time",
    "recurring": False,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.UPDATE.value,
    "cancel_bookings": True,
    "action": SessionActionTypeEnum.UPDATE.value,
    "email": SessionChangeEmailTypeEnum.REBOOK.value,
    "message": msg1,
}
rule_end_time_2 = {
    "attr": "end_time",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.UPDATE.value,
    "cancel_bookings": True,
    "action": SessionActionTypeEnum.CREATE_SINGLE_AND_UPDATE_OLD_WITH_EXDATE.value,
    "email": SessionChangeEmailTypeEnum.REBOOK.value,
    "message": msg1,
}
rule_end_time_3 = {
    "attr": "end_time",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_FOLLOWING_EVENTS.value,
    "change_type": SessionChangeTypeEnum.UPDATE.value,
    "cancel_bookings": True,
    "action": SessionActionTypeEnum.CREATE_NEW_RECURRENCE.value,
    "email": SessionChangeEmailTypeEnum.REBOOK.value,
    "message": msg1,
}

rule_weekday_1_add = {
    "attr": "by_weekday",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.ADD.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.CREATE_SINGLE_AND_UPDATE_OLD_WITH_EXDATE.value,
    "email": None,
    "message": None,
}
rule_weekday_2_add = {
    "attr": "by_weekday",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_FOLLOWING_EVENTS.value,
    "change_type": SessionChangeTypeEnum.ADD.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.CREATE_NEW_RECURRENCE.value,
    "email": None,
    "message": None,
}

rule_recurrence_end_1_add = {
    "attr": "recurrence_end_date",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.ADD.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.CREATE_SINGLE_AND_UPDATE_OLD_WITH_EXDATE.value,
    "email": None,
    "message": None,
}
rule_recurrence_end_2_add = {
    "attr": "recurrence_end_date",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_FOLLOWING_EVENTS.value,
    "change_type": SessionChangeTypeEnum.ADD.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.CREATE_NEW_RECURRENCE.value,
    "email": None,
    "message": None,
}

rule_plans_1_add = {
    "attr": "plans",
    "recurring": False,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.ADD.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.UPDATE.value,
    "email": None,
    "message": None,
}
rule_plans_2_add = {
    "attr": "plans",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.ADD.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.CREATE_SINGLE_AND_UPDATE_OLD_WITH_EXDATE.value,
    "email": None,
    "message": None,
}
rule_plans_3_add = {
    "attr": "plans",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_FOLLOWING_EVENTS.value,
    "change_type": SessionChangeTypeEnum.ADD.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.CREATE_NEW_RECURRENCE.value,
    "email": None,
    "message": None,
}

rule_class_access_groups_1_add = {
    "attr": "class_access_groups",
    "recurring": False,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.ADD.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.UPDATE.value,
    "email": None,
    "message": None,
}
rule_class_access_groups_2_add = {
    "attr": "class_access_groups",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.ADD.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.CREATE_SINGLE_AND_UPDATE_OLD_WITH_EXDATE.value,
    "email": None,
    "message": None,
}
rule_class_access_groups_3_add = {
    "attr": "class_access_groups",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_FOLLOWING_EVENTS.value,
    "change_type": SessionChangeTypeEnum.ADD.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.CREATE_NEW_RECURRENCE.value,
    "email": None,
    "message": None,
}


rule_weekday_1_subtract = {
    "attr": "by_weekday",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.SUBTRACT.value,
    "cancel_bookings": True,
    "action": SessionActionTypeEnum.CREATE_SINGLE_AND_UPDATE_OLD_WITH_EXDATE.value,
    "email": SessionChangeEmailTypeEnum.CANCEL.value,
    "message": msg2,
}
rule_weekday_2_subtract = {
    "attr": "by_weekday",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_FOLLOWING_EVENTS.value,
    "change_type": SessionChangeTypeEnum.SUBTRACT.value,
    "cancel_bookings": True,
    "action": SessionActionTypeEnum.CREATE_NEW_RECURRENCE.value,
    "email": SessionChangeEmailTypeEnum.CANCEL.value,
    "message": msg2,
}

rule_recurrence_end_1_subtract = {
    "attr": "recurrence_end_date",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.SUBTRACT.value,
    "cancel_bookings": True,
    "action": SessionActionTypeEnum.CREATE_SINGLE_AND_UPDATE_OLD_WITH_EXDATE.value,
    "email": SessionChangeEmailTypeEnum.CANCEL.value,
    "message": msg2,
}
rule_recurrence_end_2_subtract = {
    "attr": "recurrence_end_date",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_FOLLOWING_EVENTS.value,
    "change_type": SessionChangeTypeEnum.SUBTRACT.value,
    "cancel_bookings": True,
    "action": SessionActionTypeEnum.CREATE_NEW_RECURRENCE.value,
    "email": SessionChangeEmailTypeEnum.CANCEL.value,
    "message": msg2,
}

rule_plans_1_subtract = {
    "attr": "plans",
    "recurring": False,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.SUBTRACT.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.UPDATE.value,
    "email": None,
    "message": msg3,
}
rule_plans_2_subtract = {
    "attr": "plans",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.SUBTRACT.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.CREATE_SINGLE_AND_UPDATE_OLD_WITH_EXDATE.value,
    "email": None,
    "message": msg3,
}
rule_plans_3_subtract = {
    "attr": "plans",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_FOLLOWING_EVENTS.value,
    "change_type": SessionChangeTypeEnum.SUBTRACT.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.CREATE_NEW_RECURRENCE.value,
    "email": None,
    "message": msg3,
}


rule_class_access_groups_1_subtract = {
    "attr": "class_access_groups",
    "recurring": False,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.SUBTRACT.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.UPDATE.value,
    "email": None,
    "message": msg3,
}
rule_class_access_groups_2_subtract = {
    "attr": "class_access_groups",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.SUBTRACT.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.CREATE_SINGLE_AND_UPDATE_OLD_WITH_EXDATE.value,
    "email": None,
    "message": msg3,
}
rule_class_access_groups_3_subtract = {
    "attr": "class_access_groups",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_FOLLOWING_EVENTS.value,
    "change_type": SessionChangeTypeEnum.SUBTRACT.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.CREATE_NEW_RECURRENCE.value,
    "email": None,
    "message": msg3,
}


rule_attendance_1_subtract = {
    "attr": "attendance_cap",
    "recurring": False,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.SUBTRACT.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.UPDATE.value,
    "email": None,
    "message": msg4,
}
rule_attendance_2_subtract = {
    "attr": "attendance_cap",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.SUBTRACT.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.CREATE_SINGLE_AND_UPDATE_OLD_WITH_EXDATE.value,
    "email": None,
    "message": msg4,
}
rule_attendance_3_subtract = {
    "attr": "attendance_cap",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_FOLLOWING_EVENTS.value,
    "change_type": SessionChangeTypeEnum.SUBTRACT.value,
    "cancel_bookings": False,
    "action": SessionActionTypeEnum.CREATE_NEW_RECURRENCE.value,
    "email": None,
    "message": msg4,
}

rule_waitlist_1 = {
    "attr": "waitlist",
    "recurring": False,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.UPDATE.value,
    "cancel_bookings": True,
    "action": SessionActionTypeEnum.UPDATE.value,
    "email": None,
    "message": "",
}

rule_waitlist_2 = {
    "attr": "waitlist",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_ONE_EVENT.value,
    "change_type": SessionChangeTypeEnum.UPDATE.value,
    "cancel_bookings": True,
    "action": SessionActionTypeEnum.CREATE_SINGLE_AND_UPDATE_OLD_WITH_EXDATE.value,
    "email": None,
    "message": "",
}

rule_waitlist_3 = {
    "attr": "waitlist",
    "recurring": True,
    "update_type": ClassUpdateTypeEnum.ONLY_FOLLOWING_EVENTS.value,
    "change_type": SessionChangeTypeEnum.UPDATE.value,
    "cancel_bookings": True,
    "action": SessionActionTypeEnum.CREATE_NEW_RECURRENCE.value,
    "email": None,
    "message": "",
}


rules_set = [
    rule_name_1,
    rule_name_2,
    rule_name_3,
    rule_no_show_1,
    rule_no_show_2,
    rule_no_show_3,
    rule_description_1,
    rule_description_2,
    rule_description_3,
    rule_class_type_1,
    rule_class_type_2,
    rule_class_type_3,
    rule_class_type_3,
    rule_room_1,
    rule_room_2,
    rule_room_3,
    rule_attendance_1_add,
    rule_attendance_2_add,
    rule_attendance_3_add,
    rule_coach_1,
    rule_coach_2,
    rule_coach_3,
    rule_asst_coach_1,
    rule_asst_coach_2,
    rule_asst_coach_3,
    rule_allday_1,
    rule_allday_2,
    rule_allday_3,
    rule_start_date_1,
    # rule_start_date_2, rule_start_date_3,
    rule_start_time_1,
    rule_start_time_2,
    rule_start_time_3,
    rule_end_time_1,
    rule_end_time_2,
    rule_end_time_3,
    # rule_weekday_1_add,
    rule_weekday_2_add,
    # rule_recurrence_end_1_add,
    rule_recurrence_end_2_add,
    rule_plans_1_add,
    rule_plans_2_add,
    rule_plans_3_add,
    # rule_weekday_1_subtract,
    rule_weekday_2_subtract,
    # rule_recurrence_end_1_subtract,
    rule_recurrence_end_2_subtract,
    rule_plans_1_subtract,
    rule_plans_2_subtract,
    rule_plans_3_subtract,
    rule_attendance_1_subtract,
    rule_attendance_2_subtract,
    rule_attendance_3_subtract,
    rule_waitlist_1,
    rule_waitlist_2,
    rule_waitlist_3,
    rule_class_access_groups_1_subtract,
    rule_class_access_groups_2_subtract,
    rule_class_access_groups_3_subtract,
    rule_class_access_groups_1_add,
    rule_class_access_groups_2_add,
    rule_class_access_groups_3_add
]


def match_by_weekday(rule: dict, old: Class, new: Class):
    change_type = rule["change_type"]
    if (
        len([x for x in new.by_weekday.split(",") if x not in old.by_weekday.split(",")]) > 0
        and change_type == SessionChangeTypeEnum.ADD.value
    ):
        return rule
    elif (
        len([x for x in old.by_weekday.split(",") if x not in new.by_weekday.split(",")]) > 0
        and change_type == SessionChangeTypeEnum.SUBTRACT.value
    ):
        return rule
    else:
        return None


def match_attendance_cap(rule: dict, old: Class, new: Class):
    change_type = rule["change_type"]
    if old.attendance_cap > new.attendance_cap and change_type == SessionChangeTypeEnum.SUBTRACT.value:
        return rule
    elif old.attendance_cap < new.attendance_cap and change_type == SessionChangeTypeEnum.ADD.value:
        return rule
    else:
        return None


def match_plans(rule: dict, old: Class, new: Class):
    change_type = rule["change_type"]
    if len(old.plans) >= len(new.plans) and change_type == SessionChangeTypeEnum.SUBTRACT.value:
        removed_plans = [plan for plan in old.plans if plan not in new.plans]
        if any(plan.plan_status_type_id != PlanStatusType.CANCELLED.value for plan in removed_plans):
            return rule
        else:
            return None
    elif len(old.plans) < len(new.plans) and change_type == SessionChangeTypeEnum.ADD.value:
        return rule
    else:
        return None

def match_class_access_groups(rule:dict, old: Class, new: Class):
    change_type = rule["change_type"]
    if len(old.class_access_groups) >= len(new.class_access_groups) and change_type == SessionChangeTypeEnum.SUBTRACT.value:
        removed_cag = [cag for cag in old.class_access_groups if cag not in new.class_access_groups]
        if removed_cag:
            return rule
        return None
    elif len(old.class_access_groups) < len(new.class_access_groups) and change_type == SessionChangeTypeEnum.ADD.value:
        return rule
    else:
        return None

def match_recurrence_end_date(rule: dict, old: Class, new: Class):
    change_type = rule["change_type"]
    if (
        old.recurrence_end_date is None
        and new.recurrence_end_date is not None
        and change_type == SessionChangeTypeEnum.SUBTRACT.value
    ):
        return rule
    elif (
        old.recurrence_end_date is not None
        and new.recurrence_end_date is None
        and change_type == SessionChangeTypeEnum.ADD.value
    ):
        return rule
    elif (
        (old.recurrence_end_date is not None and new.recurrence_end_date is not None)
        and datetime.strptime(to_local(new.recurrence_end_date), "%Y-%m-%d %H:%M").date()
        > datetime.strptime(to_local(old.recurrence_end_date), "%Y-%m-%d %H:%M").date()
        and change_type == SessionChangeTypeEnum.ADD.value
    ):
        return rule
    elif (
        (old.recurrence_end_date is not None and new.recurrence_end_date is not None)
        and datetime.strptime(to_local(new.recurrence_end_date), "%Y-%m-%d %H:%M").date()
        < datetime.strptime(to_local(old.recurrence_end_date), "%Y-%m-%d %H:%M").date()
        and change_type == SessionChangeTypeEnum.SUBTRACT.value
    ):
        return rule
    else:
        return None


def match_rule(rule: dict, old: Class, new: Class):
    rule_attr, rule_recurring, rule_update_type, rule_change_type = (
        rule["attr"],
        rule["recurring"],
        rule["update_type"],
        rule["change_type"],
    )

    if rule_attr != "start_date":
        old_attr, new_attr = (
            old.__getattribute__(rule_attr),
            new.__getattribute__(rule_attr),
        )
    old_recurring = old.__getattribute__("recurring")
    update_type = new.__getattribute__("update_type")

    # Make sure all rule properties match the session properties
    if rule_recurring == old_recurring and rule_update_type == update_type:
        if rule_attr == "waitlist" and old.waitlist != new.waitlist:
            return rule

        # For by_weekday
        if rule_attr == "by_weekday":
            return match_by_weekday(rule, old, new)

        # For start_date, only for non-recurring sessions
        if rule_attr in ["start_date"]:
            old_attr, new_attr = (
                old.__getattribute__("start_time"),
                new.__getattribute__("start_time"),
            )
            if old_attr.date() != new_attr.date() and rule_change_type == SessionChangeTypeEnum.UPDATE.value:
                return rule
            else:
                return None

        # For start_time and end_time, compare the times, only for recurring sessions
        if (
            rule_attr in ["start_time", "end_time"]
            and old_attr.time() != normalize_local_times(old_attr, new_attr).time()
            and rule_change_type == SessionChangeTypeEnum.UPDATE.value
        ):
            return rule

        # For start_time and end_time, compare the times, only for recurring sessions
        if rule_attr in ["recurrence_end_date"]:
            return match_recurrence_end_date(rule, old, new)

        if rule_attr == "attendance_cap":
            return match_attendance_cap(rule, old, new)

        if rule_attr == "plans":
            return match_plans(rule, old, new)

        if rule_attr == "class_access_groups":
            return match_class_access_groups(rule, old, new)

        # Because we already processed rules for the following, skip them
        if rule_attr not in [
            "by_weekday",
            "start_date",
            "start_time",
            "end_time",
            "attendance_cap",
            "recurrence_end_date"
        ]:
            if old_attr != new_attr and rule_change_type == SessionChangeTypeEnum.UPDATE.value:
                return rule

        return None
    return None


def match_rules(old: Class, new: Class):
    rules = []
    for rule in rules_set:
        rule = match_rule(rule, old, new)
        if rule:
            rules.append(rule)
    return rules


def get_msgs(rules: List):
    msgs = []
    for rule in rules:
        if rule["message"] is not None:
            msgs.append(rule["message"])
    return sorted(list(set(msgs)))


def get_action(rules: List):
    actions = []
    for rule in rules:
        if rule["action"] is not None:
            actions.append(rule["action"])

    if SessionActionTypeEnum.CREATE_NEW_RECURRENCE.value in actions:
        return SessionActionTypeEnum.CREATE_NEW_RECURRENCE.value
    elif SessionActionTypeEnum.CREATE_SINGLE_AND_UPDATE_OLD_WITH_EXDATE.value in actions:
        return SessionActionTypeEnum.CREATE_SINGLE_AND_UPDATE_OLD_WITH_EXDATE.value
    elif SessionActionTypeEnum.UPDATE.value in actions:
        return SessionActionTypeEnum.UPDATE.value
    else:
        return None


def get_booking_action(rules: List):
    booking_actions = []
    for rule in rules:
        if rule["cancel_bookings"] is not None:
            booking_actions.append(rule["cancel_bookings"])

    if True in booking_actions:
        return True
    else:
        return False


def get_email_action(rules: List):
    email_actions = []
    for rule in rules:
        if rule["email"] is not None:
            email_actions.append(rule["email"])

    if SessionChangeEmailTypeEnum.CANCEL.value in email_actions:
        return SessionChangeEmailTypeEnum.CANCEL.value
    elif SessionChangeEmailTypeEnum.REBOOK.value in email_actions:
        return SessionChangeEmailTypeEnum.REBOOK.value
    else:
        return None


def get_changed_attr(rules: List):
    changed_attr = []
    for rule in rules:
        if rule["attr"] is not None:
            changed_attr.append((rule["attr"], rule["change_type"]))
    return sorted(list(set(changed_attr)))


if __name__ == "__main__":
    with create_app().app_context():
        with db.session() as sess:
            old = Class.find_by_location_and_class(2, 212)
            new = Class()
            fill_model(old, new, exclude=["plans"], ignore_nulls=True)
            new.name = "New name"
            new.update_type_id = ClassUpdateTypeEnum.ONLY_FOLLOWING_EVENTS.value
            new.by_weekday = "MO,TU,WE,TH,FR,SA"
            new.start_time = old.start_time + timedelta(days=1)
            new.all_day_event = True

            rules = match_rules(old, new)
            pass
