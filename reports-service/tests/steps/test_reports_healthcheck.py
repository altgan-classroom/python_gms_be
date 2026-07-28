import json
import requests
from subprocess import Popen, PIPE
from time import sleep
from pytest import fail
from pytest_bdd import scenario, given, when, then


@scenario("../features/healthcheck.feature", "Health endpoint is checked")
def test_reports_healthcheck():
    pass


@given("Reports service is running")
def check_reports_service():
    container_name = "reports-service"
    cmd = f"docker ps --filter name={container_name} --format {'{{.Names}}'}"
    process = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    stdout, _ = process.communicate()
    assert container_name in stdout.decode()
    cmd = f"docker inspect --format={'{{.State.Running}}'} {container_name}"
    process = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    stdout, _ = process.communicate()
    container_running_retries = 0
    while "true" not in stdout.decode():
        if container_running_retries > 10:
            fail(f"Container {container_name} not running")
        container_running_retries += 1
        sleep(5)


@when("Health endpoint is called")
def call_reports_health_endpoint(step_context, base_url):
    response = requests.get(f"{base_url}/reports/health")
    step_context["response"] = json.loads(response.content)


@then("We receive a response stating the Reports service is healthy")
def reports_health_endpoint(step_context):
    expected = {
        "data": {},
        "message": "Reports health is good",
        "status": "SUCCESS",
    }
    assert step_context.get("response") == expected
