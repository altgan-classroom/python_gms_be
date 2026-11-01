from gmsshared.src.models.class_access_group import ClassAccessGroup
from gmsshared.src.models.member_profile import MemberProfile
from gmsshared.src.models.location import Location
from gmsshared.src.models.membership import Membership

from gmsshared.src.util.enums import BillingTypeEnum
from gmsshared.src.util.enums import MembershipStatusEnum
from gmsshared.src.util.enums import BillingTypeEnum, DoorAccessVendorEnum
from gmsshared.src.util.singleton_requests import get_client


def get_location_vendor_info(location: Location):
    if not (location.door_access_location_auth and location.door_access_vendor.api_url):
        return None, None, None

    # For Kisi, we use api_key
    if location.door_access and location.door_access_auth_status and location.door_access_vendor_id == DoorAccessVendorEnum.KISI.value:
        api_url = location.door_access_vendor.api_url
        api_key = location.door_access_location_auth[0].field_value
        requests = get_client(name=location.id, max_requests = 5, time_window = 1, wait_on_rate_limit = True)
        return api_url, api_key, requests

    return None, None, None

def get_members_in_class_access_group(location_id, class_access_group_id):
    class_access_group_members = []
    class_access_group = ClassAccessGroup.find_by_id(location_id, class_access_group_id)

    plans = [plan.id for plan in class_access_group.plans]
    memberships = Membership.find_active_memberships_by_plans(location_id, plans)

    for membership in memberships:
        if not (membership.plan.billing_type_id == BillingTypeEnum.SESSION_PACKS.value and membership.sessions_count <= 0):
            class_access_group_members.append(membership.member)

    return class_access_group_members

def get_class_access_groups_for_member(location_id, member_id):
    member_class_access_groups = set()
    member_profile = MemberProfile.find_by_id(location_id, member_id)
    member_plans = [membership.plan for membership in member_profile.memberships
                    if membership.membership_status_type_id == MembershipStatusEnum.ACTIVE.value]

    for plan in member_plans:
        member_class_access_groups.update(plan.class_access_groups)
    return list(member_class_access_groups)
