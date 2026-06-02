RETRYABLE_ERRORS = {
    "RATE_LIMIT",
    "SERVER_ERROR",
    "NETWORK_ERROR",
    "UNKNOWN_ERROR",
}

CONDITIONALLY_RETRYABLE_ERRORS = {
    "FORBIDDEN",
}


def should_retry(error_type, attempt, max_retries):
    if attempt >= max_retries:
        return False

    if error_type in RETRYABLE_ERRORS:
        return True

    if error_type in CONDITIONALLY_RETRYABLE_ERRORS:
        return True

    return False