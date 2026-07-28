"""Flask CLI/Application entry point."""
from flask import Flask
from flask_migrate import Migrate

from . import db, get_config

from gmsshared.src.models.user import User
from gmsshared.src.models._ref_role_type import _RefRoleType
from gmsshared.src.models._ref_permission_type import _RefPermissionType
from gmsshared.src.models.gym import Gym
from gmsshared.src.models._ref_gym_type import _RefGymType
from gmsshared.src.models._ref_member_status_type import _RefMemberStatusType
from gmsshared.src.models.member_profile import MemberProfile
from gmsshared.src.models.user_profile import UserProfile
from gmsshared.src.models._ref_plan_type import _RefPlanType
from gmsshared.src.models._ref_duration_type import _RefDurationType
from gmsshared.src.models._ref_billing_type import _RefBillingType
from gmsshared.src.models._ref_payment_status_type import _RefPaymentStatusType
from gmsshared.src.models._ref_plan_status_type import _RefPlanStatusType
from gmsshared.src.models.plan import Plan
from gmsshared.src.models._ref_objective_type import _RefObjectiveType
from gmsshared.src.models._ref_gender_type import _RefGenderType
from gmsshared.src.models._ref_relationship_type import _RefRelationshipType
from gmsshared.src.models.location import Location
from gmsshared.src.models._ref_relationship_status_type import _RefRelationshipStatusType
from gmsshared.src.models._ref_shirt_fit_type import _RefShirtFitType
from gmsshared.src.models._ref_shirt_size_type import _RefShirtSizeType
from gmsshared.src.models._ref_location_type import _RefLocationType
from gmsshared.src.models._ref_timezone_type import _RefTimezoneType
from gmsshared.src.models.room import Room
from gmsshared.src.models._ref_registration_times_type import _RefRegistrationTimesType
from gmsshared.src.models._ref_class_type import _RefClassType
from gmsshared.src.models.session import Class
from gmsshared.src.models.member_class import MemberClass
from gmsshared.src.models._ref_payrix_onboard_status_type import _RefPayrixOnboardStatusType
from gmsshared.src.models.payrix_log import PayrixLog
from gmsshared.src.models._ref_payrix_resource_type import _RefPayrixResourceType
from gmsshared.src.models._ref_payment_method_type import _RefPaymentMethodType
from gmsshared.src.models.member_payment_method import MemberPaymentMethod
from gmsshared.src.models._ref_membership_status_type import _RefMembershipStatusType
from gmsshared.src.models.membership import Membership
from gmsshared.src.models.member_payment_schedule import MemberPaymentSchedule
from gmsshared.src.models.member_payment_history import MemberPaymentHistory
from gmsshared.src.models._ref_payrix_transaction_status_type import _RefPayrixTransactionStatusType
from gmsshared.src.models.member_payment_schedule_temp import MemberPaymentScheduleTemp
from gmsshared.src.models._ref_payment_category_type import _RefPaymentCategoryType
from gmsshared.src.models._ref_payrix_transaction_type import _RefPayrixTransactionType
from gmsshared.src.models._ref_payment_transaction_type import _RefPaymentTransactionType
from gmsshared.src.models._ref_membership_type import _RefMembershipType
from gmsshared.src.models.membership_session import MembershipSession
from gmsshared.src.models.payrix_updates_log import PayrixUpdatesLog
from gmsshared.src.models.batch_processing_log import BatchProcessingLog
from gmsshared.src.models._ref_revenue_share import _RefRevenueShare
from gmsshared.src.models.member_opengym import MemberOpenGym
from gmsshared.src.models.report import Report
from gmsshared.src.models.update_log import UpdateLog
from gmsshared.src.models._ref_product_category_type import _RefProductCategoryType
from gmsshared.src.models._ref_invoice_type import _RefInvoiceType
from gmsshared.src.models.invoice import Invoice
from gmsshared.src.models.invoice_item import InvoiceItem
from gmsshared.src.models.member_payment_history_v2 import MemberPaymentHistory_v2
from gmsshared.src.models.membership_freeze import MembershipFreeze
from gmsshared.src.models._acct_chart_of_accounts import _AcctChartOfAccounts
from gmsshared.src.models._acct_ledger import _AcctLedger
from gmsshared.src.models._ref_payrix_disbursement_status_type import _RefPayrixDisbursementStatusType
from gmsshared.src.models.payrix_disbursement import PayrixDisbursement
from gmsshared.src.models.class_access_group import ClassAccessGroup


migrate = Migrate()


def create_app():
    # The neutral `db` builds its engine from config at import time, so there's no
    # db.init_app / Flask-Migrate wiring here. Returns a bare Flask app for code that
    # still wants an app context (e.g. rules.py); db.session works without one.
    app = Flask("gmsshared")
    app.config.from_object(get_config())
    return app


app = create_app()


@app.shell_context_processor
def shell():
    return {
        "db": db,
    }
