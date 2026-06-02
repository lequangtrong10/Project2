def classify_error(result):
    """
    Phân loại lỗi từ api_client.py
    """

    if result["success"]:
        return "SUCCESS"

    status_code = result.get("status_code")
    error = result.get("error")

    if status_code == 400:
        return "BAD_REQUEST"

    if status_code == 403:
        return "FORBIDDEN"

    if status_code == 404:
        return "NOT_FOUND"

    if status_code == 429:
        return "RATE_LIMIT"

    if status_code in [500, 502, 503, 504]:
        return "SERVER_ERROR"

    if error == "TIMEOUT_ERROR":
        return "NETWORK_ERROR"

    if error == "JSON_DECODE_ERROR":
        return "DATA_ERROR"

    return "UNKNOWN_ERROR"