import asyncio
import random

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

            if error_type == "RATE_LIMIT":
                base = retry_sleep_seconds * (2 ** (attempt - 1))
                sleep_time = base + random.uniform(0, base * 0.5)
            else:
                sleep_time = retry_sleep_seconds

            await asyncio.sleep(sleep_time)
            continue

        result["attempts"] = attempt
        result["error_type"] = error_type
        return result

    last_result["attempts"] = max_retries
    last_result["error_type"] = last_error_type

    return last_result