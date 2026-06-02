import asyncio

from src.async_api_client import fetch_product_async
from src.error_classifier import classify_error
from src.retry_handler import should_retry


async def fetch_product_with_retry_async(
    session,
    product_id,
    max_retries=3,
    retry_sleep_seconds=1,
    timeout=10,
):
    last_result = None
    last_error_type = None

    for attempt in range(1, max_retries + 1):
        result = await fetch_product_async(
            session=session,
            product_id=product_id,
            timeout=timeout,
        )

        error_type = classify_error(result)

        last_result = result
        last_error_type = error_type

        if result["success"]:
            result["attempts"] = attempt
            result["error_type"] = "SUCCESS"
            return result

        if should_retry(error_type, attempt, max_retries):
            await asyncio.sleep(retry_sleep_seconds)
            continue

        result["attempts"] = attempt
        result["error_type"] = error_type
        return result

    last_result["attempts"] = max_retries
    last_result["error_type"] = last_error_type
    return last_result