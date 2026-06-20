import pytest

from src.error_classifier import classify_error

def test_success():
    assert classify_error({"success": True}) == "SUCCESS"

def test_bad_request():
    assert classify_error({"success": False, "status_code": 400}) == "BAD_REQUEST"

def test_forbidden():
    assert classify_error({"success": False, "status_code": 403}) == "FORBIDDEN"

def test_not_found():
    assert classify_error({"success": False, "status_code": 404}) == "NOT_FOUND"

def test_rate_limit():
    assert classify_error({"success": False, "status_code": 429}) == "RATE_LIMIT"

@pytest.mark.parametrize("status_code", [500, 502, 503, 504])
def test_server_error(status_code):
    result = {"success": False, "status_code": status_code}
    assert classify_error(result) == "SERVER_ERROR"

def test_network_error_from_timeout():
    result = {"success": False, "status_code": None, "error": "TIMEOUT_ERROR"}
    assert classify_error(result) == "NETWORK_ERROR"

def test_data_error_from_json_decode():
    result = {"success": False, "status_code": None, "error": "JSON_DECODE_ERROR"}
    assert classify_error(result) == "DATA_ERROR"

def test_unknown_error_fallback():
    result = {"success": False, "status_code": None, "error": None}
    assert classify_error(result) == "UNKNOWN_ERROR"