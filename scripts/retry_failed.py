from pathlib import Path
import sys
import asyncio
from datetime import datetime
import aiohttp

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from config.settings import CONFIG
from src.async_retry_handler import fetch_product_with_retry_async
from src.cleaner import clean_product
from src.product_validator import validate_product
from src.json_handler import read_json, write_json
from src.error_classifier import classify_error
from src.summary_report import build_summary
from src.summary_printer import print_summary


OUTPUT_DIR = BASE_DIR / CONFIG["output"]["base_dir"]
FAILED_DIR = BASE_DIR / CONFIG["output"]["failed_dir"]
REPORTS_DIR = BASE_DIR / CONFIG["output"]["reports_dir"]

RECOVERED_FILE = REPORTS_DIR / "recovered_products.json"
FINAL_FAILED_FILE = REPORTS_DIR / "final_failed.json"
RETRY_SUMMARY_FILE = REPORTS_DIR / "retry_summary.json"

CONCURRENCY = CONFIG["runtime"]["concurrency"]
TIMEOUT = CONFIG["runtime"]["timeout"]
MAX_RETRIES = CONFIG["runtime"]["max_retries"]
RETRY_SLEEP_SECONDS = CONFIG["runtime"]["retry_sleep_seconds"]


def load_failed_ids():
    failed_ids = []

    failed_files = sorted(FAILED_DIR.glob("failed_*.json"))

    for file_path in failed_files:
        failed_items = read_json(file_path)

        for item in failed_items:
            product_id = str(item.get("id")).strip()

            if product_id:
                failed_ids.append(product_id)

    return list(dict.fromkeys(failed_ids))


async def retry_failed_ids():
    failed_ids = load_failed_ids()

    print(f"Failed IDs to retry: {len(failed_ids)}")

    recovered_products = []
    final_failed = []

    start_time = datetime.now()

    semaphore = asyncio.Semaphore(CONCURRENCY)

    async with aiohttp.ClientSession() as session:

        async def retry_one(product_id):
            async with semaphore:
                return await fetch_product_with_retry_async(
                    session=session,
                    product_id=product_id,
                    max_retries=MAX_RETRIES,
                    retry_sleep_seconds=RETRY_SLEEP_SECONDS,
                    timeout=TIMEOUT,
                )

        tasks = [retry_one(product_id) for product_id in failed_ids]
        results = await asyncio.gather(*tasks)

    for result in results:
        product_id = result["id"]
        error_type = classify_error(result)

        if not result["success"]:
            final_failed.append({
                "id": product_id,
                "status_code": result["status_code"],
                "error": result["error"],
                "error_type": error_type,
                "attempts": result.get("attempts", 1),
            })
            continue

        product = clean_product(result["data"])
        validation_result = validate_product(product)

        if not validation_result["is_valid"]:
            final_failed.append({
                "id": product_id,
                "status_code": result["status_code"],
                "error": "INVALID_PRODUCT",
                "error_type": "INVALID_PRODUCT",
                "warnings": validation_result["warnings"],
                "attempts": result.get("attempts", 1),
            })
            continue

        recovered_products.append(product)

    end_time = datetime.now()

    summary = build_summary(
        input_count=len(failed_ids),
        products=recovered_products,
        failed=final_failed,
        warnings=[],
        start_time=start_time,
        end_time=end_time,
    )

    write_json(recovered_products, RECOVERED_FILE)
    write_json(final_failed, FINAL_FAILED_FILE)
    write_json(summary, RETRY_SUMMARY_FILE)

    print_summary(summary)

    print("\nRetry failed completed.")
    print(f"Recovered products: {RECOVERED_FILE}")
    print(f"Final failed      : {FINAL_FAILED_FILE}")
    print(f"Retry summary     : {RETRY_SUMMARY_FILE}")


if __name__ == "__main__":
    asyncio.run(retry_failed_ids())