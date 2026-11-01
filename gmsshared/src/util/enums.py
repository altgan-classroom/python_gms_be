from enum import Enum
from itertools import chain


class RoleEnum(Enum):
    OWNER = 1
    USER = 2
    COACH = 3
    MANAGER = 4
    STAFF = 5
    MEMBER = 6
    KIOSK = 7


class MemberStatusEnum(Enum):
    ACTIVE = 1
    FROZEN = 2
    CANCELLED = 3
    NON_RENEWED = 4
    ENDING_SOON = 5
    PENDING = 6


class MembershipStatusEnum(Enum):
    ACTIVE = 1
    CANCELLED = 2
    FROZEN = 3
    RENEWED = 4
    NOT_STARTED = 5


class MembershipTypeEnum(Enum):
    FULL_MEMBERSHIP = 1
    CHALLENGE = 2
    LIMITED_TIME_PASS = 3

class GenderEnum(Enum):
    MALE = 1
    FEMALE = 2

class RelationshipTypeEnum(Enum):
    SPOUSE = 1
    FAMILY = 2
    FRIEND = 3
    OTHER = 4


class LocationTypeEnum(Enum):
    PHYSICAL = 1
    VIRTUAL = 2
    BOTH = 3


class GymTypeEnum(Enum):
    OTHER = 1
    HEALTH_CLUB = 2
    GROUP_TRAINING = 3
    SEMI_PRIVATE = 4
    PERSONAL_TRAINING = 5
    MARTIAL_ARTS = 6
    SPIN_STUDIO = 7
    YOGA_PILATES = 8


class SessionClassEnum(Enum):
    SESSION = 1
    CLASS = 2


class AttendanceStatusEnum(str, Enum):
    BOOKED = "Booked"
    ATTENDED = "Attended"
    NO_SHOWED = "No Showed"
    CANCELLED = "Cancelled"


class ResponseStatusEnum(str, Enum):
    """GENERIC RESPONSE STATUS"""
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    SAVED = "SAVED"
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    DELETED = "DELETED"
    FOUND = "FOUND"
    CONFLICT = "CONFLICT"
    NOT_FOUND = "NOT_FOUND"
    INVALID_REQUEST = "INVALID_REQUEST"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"

    """AUTH RESPONSE STATUS"""
    INVALID_TOKEN = "INVALID_TOKEN"
    EXPIRED_TOKEN = "EXPIRED_TOKEN"
    ERROR_SETTING_PASSWORD = "ERROR_SETTING_PASSWORD"
    PASSWORD_SET = "PASSWORD_SET"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"

    """USER RELATED STATUS"""
    MEMBER_DOES_NOT_EXIST = "MEMBER_DOES_NOT_EXIST"
    USER_PROFILE_DOES_NOT_EXIST = "USER_PROFILE_DOES_NOT_EXIST"
    SENT_MAIL = "SENT_MAIL"

    """PLAN RELATED STATUS"""
    PLAN_DOES_NOT_EXIST = "PLAN_DOES_NOT_EXIST"
    ACTIVE_MEMBERSHIP_EXISTS = "ACTIVE_MEMBERSHIP_EXISTS"

    """BOOKING RELATED STATUS"""
    INVALID_MEMBERSHIP = "INVALID_MEMBERSHIP"
    TOTAL_LIMIT_REACHED = "TOTAL_LIMIT_REACHED"
    PERIOD_LIMIT_REACHED = "PERIOD_LIMIT_REACHED"
    SESSION_ATTENDANCE_CAP_REACHED = "SESSION_ATTENDANCE_CAP_REACHED"
    REGISTRATION_CLOSED = "REGISTRATION_CLOSED"
    NON_ACTIVE_MEMBERSHIP = "NON_ACTIVE_MEMBERSHIP"
    CHECK_IN_NOT_AVAILABLE_YET = "CHECK_IN_NOT_AVAILABLE_YET"
    CANCELLATION_CLOSED = "CANCELLATION_CLOSED"
    REGISTRATION_NOT_OPENED = "REGISTRATION_NOT_OPENED"
    REGISTRATION_TIME_INVALID = "REGISTRATION_TIME_INVALID"
    BLOCKED_BY_BALANCE = "BLOCKED_BY_BALANCE"


class PayrixResourceEnum(Enum):
    MERCHANT = 1
    CUSTOMER = 2
    TOKEN = 3
    TRANSACTION = 4

class DoorAccessResourceEnum(Enum):
    PLACE = 1
    DOOR = 2
    USER = 3
    GROUP = 4
    ROLE_ASSIGNMENT = 5
    CREDENTIAL = 6
    GROUP_LOCK = 7

class PayrixOnboardStatusEnum(Enum):
    NOT_READY = 1
    READY = 2
    BOARDED = 3
    MANUAL = 4
    DENIED = 5
    QUEUED = 98
    FAILED = 99

class DoorAccessOnboardStatusEnum(Enum):
    NOT_READY = 1
    READY = 2
    BOARDED = 3
    MANUAL = 4
    DENIED = 5
    QUEUED = 98
    FAILED = 99

class DoorAccessVendorEnum(Enum):
    KISI = 1

class DoorAccessEventTypeEnum(Enum):
    UNLOCK = 1

class HttpRequestTypeEnum(Enum):
    GET = 1
    POST = 2
    PUT = 3
    DELETE = 4
    PATCH = 5

class DoorAccessStatusEnum(Enum):
    PENDING = 0
    SUCCESS = 1
    FAILED = 2
    PROCESSING = 9

class DoorAccessDigitalKeyStatusEnum(Enum):
    PENDING = 0
    ACTIVE = 1
    INVALID = 2

class DoorAccessCardTypeEnum(Enum):
    MIFARE_DESFIRE = "mifare_desfire"

class PayrixTransactionStatusEnum(Enum):
    PENDING = 0
    APPROVED = 1
    FAILED = 2
    CAPTURED = 3
    SETTLED = 4
    RETURNED = 5
    FORGIVEN = 6
    CANCELLED = 7


class PayrixTransactionTypeEnum(Enum):
    NONE = 0
    CC_SALE = 1
    CC_AUTH = 2
    CC_CAPTURE = 3
    CC_REVERSE = 4
    CC_REFUND = 5
    ACH_SALE = 7
    ACH_REFUND = 8
    ACH_REDEPOSIT = 11
    ACH_ACCT_VERIFY = 12


class PayrixPaymentMethodEnum(Enum):
    AMEX = 1
    VISA = 2
    MASTERCARD = 3
    DINERSCLUB = 4
    DISCOVER = 5
    DEBITCARD = 7
    CHECKING = 8
    SAVINGS = 9
    CORP_CHECKING = 10
    CORP_SAVINGS = 11


class PaymentTransactionTypeEnum(Enum):
    SALE = 1
    REFUND = 2
    RETRY_SALE = 3


class PaymentCategoryEnum(Enum):
    CANCELLATION_FEE = 1
    LATE_FEE = 2
    NOSHOW_FEE = 3
    OTHER = 4
    MEMBERSHIP = 5

class ProductCategoryTypeEnum(Enum):
    MEMBERSHIP = 1
    RETAIL = 2
    FEES = 3

class InvoiceTypeEnum(Enum):
    INVOICE = 1
    CREDIT_MEMO = 2
    WRITEOFF = 3

class InvoiceItemStatusTypeEnum(Enum):
    PENDING = 1
    PROCESSED = 2
    CANCELLED = 3

class AssetTypeEnum(str, Enum):
    AVATAR = "avatar"
    ALL = "all"


class ImageFileTypeEnum(str, Enum):
    JPG = "jpg"
    JPEG = "jpeg"
    PNG = "png"


class BillingTypeEnum(Enum):
    RECURRING = 1
    PAID_IN_FULL = 2
    SESSION_PACKS = 3
    FREE = 4


class DurationTypeEnum(Enum):
    DAYS = 1
    WEEKS = 2
    MONTHS = 3
    YEARS = 4
    DAY = 5
    WEEK = 6
    MONTH = 7
    YEAR = 8


class PaymentStatusEnum(str, Enum):
    CURRENT = "Paid to Date"
    PAST_DUE = "Past Due"
    NONE_ON_FILE = "None on file"


class ContactTypeEnum(str, Enum):
    LEAD = "Lead"
    TRIAL_MEMBER = "Trial Member"
    MEMBER = "Member"
    FROZEN = "Frozen"
    CANCELLED = "Cancelled"
    ACTIVE = "Active"
    CLIENT = "Client"
    EXITED = "Exited"

class SalesReportTypeEnum(str, Enum):
    # SALES
    NEW_MEMBERSHIP_SALES = "NEWSALES"
    NEW_CONTACTS = "NEWCONTACTS"


class OperationsReportTypeEnum(str, Enum):
    # OPERATIONS
    CHALLENGE_CONVERSION_BY_COHORT_DETAIL = "BASICCONVERSIONS"
    CHALLENGE_CONVERSION_BY_COHORT_SUMMARY = "BASICCONVERSIONSSUMMARY"
    WEDNESDAY_ATTENDANCE_REPORT = "WEEKLYATT"
    RECURRING_MEMBER_CHURN = "BASICCHURN"
    CONTACT_ATTENDANCE_PER_MONTH = "ATTPERMONTH"
    CONTACT_ATTENDANCE_HISTORY = "ATTENDANCEHISTORY"
    MEMBER_SESSIONS_ATTENDANCE = "MEMBSESSATT"
    LOCATION_MEMBERSHIP_COUNT = "LOCMEMBCOUNT"
    AT_RISK_ATTENDANCE = "ATRISKATT"


class FinancialReportTypeEnum(str, Enum):
    # FINANCIAL
    NET_REVENUE = "NETREVENUE"
    MTD_REVENUE = "MTDREVENUE"
    LAST_MONTH_REVENUE = "LASTMONTH"
    FORECASTED_REVENUE ="FORECASTED"
    REVENUE_SUMMARY = "REVENUE_SUMMARY"
    BALANCE_AND_FUTURE_CONTRACT_VALUE = "BALANCEFUTURECONTRACT"


class ReportTypeEnum(str, Enum):
    _ignore_ = 'member cls'
    cls = vars()
    for member in chain(
            list(SalesReportTypeEnum),
            list(OperationsReportTypeEnum),
            list(FinancialReportTypeEnum)):
        cls[member.name] = member.value
    del member, cls


class MembershipCancelReasonTypeEnum(Enum):
    VACATION = 1
    MEDICAL = 2


class MembershipFreezeReasonEnum(Enum):
    VACATION = 1
    MEDICAL = 2
    EXPIRED = 3


class MembershipCancelReasonEnum(Enum):
    COST = 1
    MOVING = 2
    LOCATION = 3
    HEALTH_CHALLENGES = 4
    TOO_BUSY = 5
    DISSATISFACTION_WITH_OFFERINGS = 6
    LACK_OF_ACCOUNTABILITY = 7
    UNCOMFORTABLE_WITH_WORKOUTS = 8
    MEMBERSHIP_CHANGE = 9
    OTHER = 10


class PlanStatusType(Enum):
    ACTIVE = 1
    GRANDFATHERED = 2
    CANCELLED = 3

class PlanTypeEnum(Enum):
    SEMIPRIVATE = 1
    LARGEGROUP = 2
    PERSONALTRAINING = 3
    OPENGYM = 4
    OTHER = 5

class ClassUpdateTypeEnum(Enum):
    ONLY_ONE_EVENT = 1
    ONLY_FOLLOWING_EVENTS = 2
    ALL_EVENTS = 3

class ClassByWeekDaysEnum(Enum):
    SU = "SU"
    MO = "MO"
    TU = "TU"
    WE = "WE"
    TH = "TH"
    FR = "FR"
    SA = "SA"

class ClassFrequencyEnum(Enum):
    HOURLY = 1
    DAILY = 2
    WEEKLY = 3
    MONTHLY = 4

class SessionActionTypeEnum(Enum):
    UPDATE = 1
    CREATE_SINGLE_AND_UPDATE_OLD_WITH_EXDATE = 2
    CREATE_NEW_RECURRENCE = 3

class SessionChangeTypeEnum(Enum):
    UPDATE = 1
    ADD = 2
    SUBTRACT = 3

class SessionChangeEmailTypeEnum(Enum):
    REBOOK = 1
    CANCEL = 2

class CheckinTypeEnum(Enum):
    CLASS_CHECKIN = 1
    OPENGYM_CHECKIN = 2
    BOTH_CLASS_OPENGYM = 3

class RegistrationTimesType(Enum):
    IMMEDIATELY = 1
    AT_START_TIME = 2
    MINUTES_BEFORE = 3
    HOURS_BEFORE = 4
    WEEKS_BEFORE = 5
    DAYS_BEFORE = 6

class PayrixDisbursementStatusType(Enum):
    REQUESTED = 1
    PROCESSING = 2
    PROCESSED = 3
    FAILED = 4
    DENIED = 5
    RETURNED = 6

class CharterOfAccountsTypeEnum(Enum):
    SERVICE_REVENUE = 1001
    SALES_TAX = 1002
    MERCHANT_PROCESS_REC = 1003
    ACCOUNTS_REC = 1004
    EXP_CHAREGEBACKS = 1005
    EXP_BAD_DEBT = 1006
    DISCOUNT_REVENUE = 1007
    CASH = 1008
    LATE_FEE_REVENUE = 1009
    NO_SHOW_FEE_REVENUE = 1010
    CANCEL_FEE_REVENUE = 1011

class InvoiceStatusTypeEnum(Enum):
    PENDING = 1
    PAID = 2
    PAST_DUE = 3
    VOID = 4


class RequestTokenType(Enum):
    SIGNUP = 1
    FORGOT_PASSWORD = 2
    PROFILE_SETUP = 3

class MembershipNextActionTypeEnum(Enum):
    FREEZE = 1
    CANCEL = 2
    RENEW = 3
    END = 4

class BookingRejectionReasonEnum(Enum):
    SESSION_ATTENDANCE_CAP_REACHED = 1
    INVALID_MEMBERSHIP = 2
    REGISTRATION_NOT_OPENED = 3
    REGISTRATION_CLOSED = 4
    ALREADY_REGISTERED = 5
    BLOCKED_BY_BALANCE = 6

class WeekDaysEnum(Enum):
    Monday = 1
    Tuesday = 2
    Wednesday = 3
    Thursday = 4
    Friday = 5
    Saturday = 6
    Sunday = 7

class SessionActivityTypeEnum(Enum):
    SESSIONS_ADDED = 1
    SESSIONS_REMOVED = 2
    SESSION_ATTENDED = 3
    SESSION_CANCELLED = 4
    SESSION_BOOKED = 5
    SESSION_NO_SHOW = 6
    SESSION_LIMIT_STARTED = 7
    SESSION_LIMIT_EXPIRED = 8
    SESSION_LIMIT_REFRESHED = 9

class ClassAccessGroupChangeTypeEnum(Enum):
    GROUP = 1
    DOORS = 2
    ACCESS_TIMES = 3
