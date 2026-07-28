import datetime
import json

import pytest
import requests
from pytest import fixture
from pytest_bdd import scenario, given, when, then

now = datetime.datetime.now()
date_format = "%Y-%m-%d"
datetime_format = "%Y-%m-%d %H:%M"
location_id = 1
member_id = 1


@fixture
def expected_member():
    expected = {
        "address_city": "Central City",
        "address_country": "NEVERLAND",
        "address_state": "KEY ISLAND",
        "address_street": "Main Street",
        "address_zip": "55555",
        "birth_date": datetime.datetime(2000, 10, 1).strftime(date_format),
        "contact_type": "Lead",
        "dark_mode": None,
        "email": "janedoe@example.com",
        "emergency_first_name": "Mom",
        "emergency_last_name": "Doe",
        "emergency_phone_number": "555-4321",
        "emergency_relationship_type_id": 1,
        "emergency_relationship": None,
        "first_name": "Jane",
        "gender_type_id": 1,
        "guardian_first_name": "Pop",
        "guardian_last_name": "Doe",
        "guardian_phone_number": "555-4321",
        "last_check_in": now.strftime(datetime_format),
        "last_name": "Doe",
        "lifetime_value": 0,
        "location_id": 1,
        "member_id": 1,
        "membership_plans": None,
        "membership_status": "Active",
        "middle_name": "Mary",
        "objective_type_id": 1,
        "payment_status": "Past Due",
        "phone_number": None,
        "photo_url": "https://www.example.com/photo_url",
        "preferred_name": "Maria",
        "about": "No 'about' info for this user",
        "create_datetime": now.strftime(datetime_format),
    }
    yield expected


@fixture
def expected_posted_member(expected_member):
    del expected_member["last_check_in"]
    del expected_member["member_id"]
    del expected_member["payment_status"]
    del expected_member["photo_url"]
    del expected_member["contact_type"]
    del expected_member["lifetime_value"]
    expected_member["membership_plans"] = [0]
    expected_member["phone_number"] = "555-1234"
    expected_member["birth_date"] = datetime.datetime(2000, 10, 1).strftime("%Y-%m-%d")
    yield expected_member


@fixture
def required_tables(db_client):
    cursor = db_client.cursor()

    ref_relationship_insert = """INSERT INTO _ref_relationship_status_type (id, name, create_datetime, update_datetime) VALUES(%s, %s, %s, %s);"""
    ref_relationship_values = (1, "Parent", now, now)
    cursor.execute(ref_relationship_insert, ref_relationship_values)
    db_client.commit()

    ref_shirt_fit_type_insert = (
        """INSERT INTO _ref_shirt_fit_type (id, name, create_datetime, update_datetime) VALUES(%s, %s, %s, %s);"""
    )
    ref_shirt_fit_values = (1, "Fit", now, now)
    cursor.execute(ref_shirt_fit_type_insert, ref_shirt_fit_values)
    db_client.commit()

    ref_shirt_size_insert = (
        """INSERT INTO _ref_shirt_size_type (id, name, create_datetime, update_datetime) VALUES(%s, %s, %s, %s);"""
    )
    ref_shirt_size_values = (1, "M", now, now)
    cursor.execute(ref_shirt_size_insert, ref_shirt_size_values)
    db_client.commit()

    ref_member_status_type_insert = """INSERT INTO _ref_member_status_type (id, name, description, create_datetime, update_datetime) VALUES(%s, %s, %s, %s, %s);"""
    ref_member_status_values = (1, "Active", "Active", now, now)
    cursor.execute(ref_member_status_type_insert, ref_member_status_values)
    db_client.commit()

    ref_payment_status_type_insert = """INSERT INTO _ref_payment_status_type (id, name, description, create_datetime, update_datetime) VALUES(%s, %s, %s, %s, %s);"""
    ref_payment_status_values = (1, "Paid", "Paid", now, now)
    cursor.execute(ref_payment_status_type_insert, ref_payment_status_values)
    db_client.commit()

    ref_object_type_insert = """INSERT INTO _ref_objective_type (id, name, description, create_datetime, update_datetime) VALUES(%s, %s, %s, %s, %s);"""
    ref_object_type_values = (1, "Better", "Better", now, now)
    cursor.execute(ref_object_type_insert, ref_object_type_values)
    db_client.commit()

    ref_role_type_insert = """INSERT INTO _ref_role_type (id, name, description, create_datetime, update_datetime) VALUES(%s, %s, %s, %s, %s);"""
    ref_role_type_values = (6, "Member", "Member Role", now, now)
    cursor.execute(ref_role_type_insert, ref_role_type_values)
    db_client.commit()

    ref_location_type_insert = (
        """INSERT INTO _ref_location_type (id, name, create_datetime, update_datetime) VALUES(%s, %s, %s, %s);"""
    )
    ref_location_type_values = (1, "Location Type", now, now)
    cursor.execute(ref_location_type_insert, ref_location_type_values)
    db_client.commit()

    ref_timezone_type_insert = """INSERT INTO _ref_timezone_type (id, name, create_datetime, update_datetime, iana_tzdata) VALUES(%s, %s, %s, %s, %s);"""
    ref_timezone_type_values = (1, "Example Timezone", now, now, "America/New_York")
    cursor.execute(ref_timezone_type_insert, ref_timezone_type_values)
    db_client.commit()

    ref_registration_times_type_insert = """INSERT INTO _ref_registration_times_type (id, name, create_datetime, update_datetime) VALUES(%s, %s, %s, %s);"""
    ref_registration_times_type_values = (1, "Time Type Example", now, now)
    cursor.execute(ref_registration_times_type_insert, ref_registration_times_type_values)
    db_client.commit()

    gym_insert = """INSERT INTO gym (id, name, logo_url, company_name, company_website, location_type_id, timezone_type_id, session_or_class, registration_start_time_type_id, registration_start_time_value, registration_end_time_type_id, registration_end_value, late_cancellation_enforcement, late_cancellation_time_type_id, cancellation_penalty, no_show_penalties, no_show_time_penalty, waitlist_availability, create_datetime, update_datetime) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
    gym_values = (
        1,
        "Gym",
        "https://www.example.com/gym_logo.png",
        "GymOwners",
        "https://www.gymowners.com",
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        now,
        now,
    )
    cursor.execute(gym_insert, gym_values)
    db_client.commit()

    location_insert = """INSERT INTO location (id, name, address_1, address_2, city, state, zip, country, area_sft, active, `primary`, cs_phone, cs_email, create_datetime, update_datetime, other_gym_type, gym_id, location_type_id) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
    location_values = (
        1,
        "Location",
        "Address 1",
        "Address 2",
        "City",
        "State",
        "55555",
        "Country",
        0,
        1,
        1,
        "",
        "location@example.com",
        now,
        now,
        "",
        1,
        1,
    )
    cursor.execute(location_insert, location_values)
    db_client.commit()

    cursor.close()

    return True


@scenario("../features/crud_operations.feature", "User Profile Data Returned")
def test_get_member():
    pass


@given("An user profile exists in the database")
def create_user_in_db(db_client, required_tables):
    if not required_tables:
        pytest.fail("Error when creating required tables")

    cursor = db_client.cursor()

    user_profile_insert = """INSERT INTO user_profile (id, first_name, last_name, middle_name, preferred_name, photo_url, birth_date, address_street, address_city, address_state, address_zip, address_country, phone_number, emergency_first_name, emergency_last_name, emergency_phone_number, guardian_first_name, guardian_last_name, guardian_phone_number, gender_type_id, emergency_relationship_type_id, relationship_status_type_id, have_children, shirt_size_type_id, shirt_fit_type_id, create_datetime, update_datetime) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
    user_profile_values = (
        1,
        "Jane",
        "Doe",
        "Mary",
        "Maria",
        "https://www.example.com/photo_url",
        datetime.datetime(2000, 10, 1).date(),
        "Main Street",
        "Central City",
        "KEY ISLAND",
        "55555",
        "NEVERLAND",
        "555-1234",
        "Mom",
        "Doe",
        "555-4321",
        "Pop",
        "Doe",
        "555-4321",
        1,
        1,
        1,
        "Nope",
        1,
        1,
        now,
        now,
    )
    cursor.execute(user_profile_insert, user_profile_values)
    db_client.commit()

    user_insert = """INSERT INTO user (id, email, password_hash, active, last_login, verified, verified_on, create_datetime, update_datetime, role_type_id, user_profile_id) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
    user_values = (1, "janedoe@example.com", "hash", 1, now, 1, now, now, now, 6, 1)
    cursor.execute(user_insert, user_values)
    db_client.commit()

    member_profile_insert = """INSERT INTO member_profile (user_id, location_id, member_status_type_id, payment_status_type_id, objective_type_id, start_date, last_check_in, cp_phone_calls, cp_email, cp_sms, cp_in_app_message, favourite_gym_clothing_website, favourite_website, favourite_restaurant, create_datetime, update_datetime) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
    member_profile_values = (1, 1, 1, 1, 1, now, now, 1, 1, 1, 1, "", "", "", now, now)
    cursor.execute(member_profile_insert, member_profile_values)
    db_client.commit()

    cursor.close()


@when("using the GET endpoint for members")
def get_member(step_context, base_url):
    response = requests.get(f"{base_url}/members/locations/{location_id}/members/{member_id}")
    step_context["get_members_response"] = response


@then("We receive a response containing the member information")
def assert_member(step_context, expected_member):
    response: requests.Response = step_context["get_members_response"]
    assert response.status_code == 200
    content = json.loads(response.content)
    assert content["message"] == "Profile found"
    assert content["status"] == "FOUND"
    for k, v in content["data"].items():
        if k == "last_check_in":
            actual = datetime.datetime.strptime(v, datetime_format).date()
            assert actual == datetime.datetime.strptime(expected_member[k], datetime_format).date()
        else:
            assert v == expected_member[k]


@scenario("../features/crud_operations.feature", "User Profile Data Created and Returned")
def test_post_and_get_member():
    pass


@given("User data is POSTED")
def post_user_data(base_url, required_tables, expected_posted_member):
    # if not required_tables:
    #     pytest.fail("Error when creating required tables")
    # url = f"{base_url}/members/locations/{location_id}/members"
    # response = requests.post(url=url, json=expected_posted_member)
    # assert response.content == ""
    # assert response.status_code == 200
    pass


@when("GETTING the created user data")
def get_user_data(step_context, base_url):
    pass


@then("The same posted data is returned")
def assert_user_data(step_context):
    pass
