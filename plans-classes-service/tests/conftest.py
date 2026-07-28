from os import getenv

from pytest import fixture


@fixture
def step_context():
    return {"response": None}


@fixture
def base_url():
    host = getenv("BITBUCKET_DOCKER_HOST_INTERNAL", "127.0.0.1")
    if host == "mysql" or host == "localstack":
        host = "127.0.0.1"
    return f"http://{host}:5006/api/v1"
