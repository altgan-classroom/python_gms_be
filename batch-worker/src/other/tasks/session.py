import json

from gmsshared.src.models.batch_processing_log import BatchProcessingLog
from gmsshared.src.models.member_class import MemberClass
from gmsshared.src.util.datetime_util import utc_now
from gmsshared.src.util.enums import BillingTypeEnum
from gmsshared.src.util.misc import row2dict
from ... import scheduled_worker


@scheduled_worker.task(name="credit_noshows", task_acks_late=True, ignore_result=False)
def credit_noshows():
    BatchProcessingLog.insert(process_name="Credit No Shows", message="Starting...")
    no_showed_bookings = MemberClass.find_no_showed_bookings()
    for booking in no_showed_bookings:
        try:
            if (
                booking.membership and booking.membership.plan.billing_type_id == BillingTypeEnum.SESSION_PACKS.value
                and booking.clazz.end_time < utc_now().replace(tzinfo=None)
            ):
                BatchProcessingLog.insert(
                    "Credit No Shows",
                    f"Crediting Session Pack to Booking: {booking.id}",
                    booking.location_id,
                    booking.user_id,
                    booking.membership.id,
                    data=json.dumps(row2dict(booking, include=[])),
                )
                booking.membership.sessions_count += 1
                booking.no_show_credited = True
                booking.membership.save_and_commit()
                booking.save_and_commit()
        except Exception as e:
            BatchProcessingLog.insert(
                "Credit No Shows",
                f"Crediting Session Pack: {booking.id}",
                booking.location_id,
                booking.user_id,
                booking.membership.id,
                data=json.dumps(row2dict(booking, include=[])),
                error=str(e),
            )
            continue
