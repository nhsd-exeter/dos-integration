from os import environ

import pytest

FILE_PATH = "application.common.circuit"


def test_get_circuit_is_open_none(dynamodb_table_create, dynamodb_client):
    from application.common.circuit import get_circuit_is_open

    assert get_circuit_is_open("BLABLABLA") is None


def test_put_and_get_circuit_is_open(dynamodb_table_create, dynamodb_client):
    from application.common.circuit import get_circuit_is_open, put_circuit_is_open

    put_circuit_is_open("TESTCIRCUIT", True)

    assert get_circuit_is_open("TESTCIRCUIT")


def test_put_circuit_exception(dynamodb_table_create, dynamodb_client):
    from application.common.circuit import put_circuit_is_open

    temp_table = environ["CHANGE_EVENTS_TABLE_NAME"]
    del environ["CHANGE_EVENTS_TABLE_NAME"]
    with pytest.raises(Exception):  # noqa: PT011,B017
        put_circuit_is_open("TESTCIRCUIT", True)

    environ["CHANGE_EVENTS_TABLE_NAME"] = temp_table


def test_get_circuit_exception(dynamodb_table_create, dynamodb_client):
    from application.common.circuit import get_circuit_is_open

    temp_table = environ["CHANGE_EVENTS_TABLE_NAME"]
    del environ["CHANGE_EVENTS_TABLE_NAME"]
    with pytest.raises(Exception):  # noqa: PT011,B017
        get_circuit_is_open("TESTCIRCUIT")

    environ["CHANGE_EVENTS_TABLE_NAME"] = temp_table
