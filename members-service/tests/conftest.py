from os import getenv

from pytest import fixture

DATABASE = "gms"


@fixture
def step_context():
    return {"response": None}


@fixture
def base_url():
    host = getenv("BITBUCKET_DOCKER_HOST_INTERNAL", "127.0.0.1")
    if host == "mysql" or host == "localstack":
        host = "127.0.0.1"
    return f"http://{host}:5005/api/v1"


@fixture
def db_client():
    import pymysql

    conn = pymysql.connect(host="127.0.0.1", user="root", password="password", database=DATABASE)
    yield conn
    conn.close()


def pytest_bdd_before_scenario(request, feature, scenario):
    import pymysql

    db_client = pymysql.connect(host="127.0.0.1", user="root", password="password", database=DATABASE)
    cursor = db_client.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    for table in tables:
        table_name = table[0]
        cursor.execute(f"TRUNCATE TABLE {table_name}")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    db_client.commit()
    cursor.close()
    db_client.close()
