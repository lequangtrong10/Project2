from pathlib import Path
import sys
import asyncio
from datetime import datetime
import aiohttp
import pandas as pd

# ============================================================
# 1. PROJECT PATH SETUP
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# ============================================================
# 2. IMPORT MODULES
# ============================================================

from config.settings import CONFIG

from src.async_retry_handler import fetch_product_with_retry_async
from src.cleaner import clean_product
from src.product_validator import validate_product
from src.json_handler import read_json, write_json
from src.error_classifier import classify_error
from src.summary_report import build_summary
from src.summary_printer import print_summary
from src.batch_processor import split_into_batches, get_batch_file_name
from src.checkpoint import load_checkpoint, save_checkpoint
from src.progress_tracker import (
    load_processed_ids,
    save_processed_id,
    filter_unprocessed_ids,
)

# ============================================================
# 3. CONFIG
# ============================================================

CLEAN_FILE = BASE_DIR / CONFIG["input"]["clean_file"]

OUTPUT_DIR = BASE_DIR / CONFIG["output"]["base_dir"]
PRODUCTS_DIR = BASE_DIR / CONFIG["output"]["products_dir"]
FAILED_DIR = BASE_DIR / CONFIG["output"]["failed_dir"]
WARNINGS_DIR = BASE_DIR / CONFIG["output"]["warnings_dir"]
REPORTS_DIR = BASE_DIR / CONFIG["output"]["reports_dir"]

CHECKPOINT_FILE = REPORTS_DIR / "checkpoint.json"
PROCESSED_IDS_FILE = REPORTS_DIR / "processed_ids.txt"
SUMMARY_FILE = REPORTS_DIR / "summary.json"

SAMPLE_SIZE = CONFIG["runtime"]["sample_size"]
BATCH_SIZE = CONFIG["runtime"]["batch_size"]
CONCURRENCY = CONFIG["runtime"]["concurrency"]
TIMEOUT = CONFIG["runtime"]["timeout"]

MAX_RETRIES = CONFIG["runtime"]["max_retries"]
RETRY_SLEEP_SECONDS = CONFIG["runtime"]["retry_sleep_seconds"]

# ============================================================
# 4. LOAD PRODUCT IDS
# ============================================================

def load_product_ids():
    if not CLEAN_FILE.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {CLEAN_FILE}")

    df = pd.read_csv(CLEAN_FILE)

    if "id" not in df.columns:
        raise ValueError("products_clean.csv không có cột 'id'")

    # Chuyển cột id thành list Product ID
    original_ids = df["id"].astype(str).head(SAMPLE_SIZE).tolist()

    # Đọc danh sách Product ID đã xử lý từ processed_ids.txt
    processed_ids = load_processed_ids(PROCESSED_IDS_FILE)

    # Lọc ra các Product ID chưa xử lý để hỗ trợ resume khi chương trình bị dừng
    remaining_ids = filter_unprocessed_ids(original_ids, processed_ids)

    print(f"Total sample IDs     : {len(original_ids)}")
    print(f"Already processed IDs: {len(processed_ids)}")
    print(f"Remaining IDs        : {len(remaining_ids)}")

    return original_ids, remaining_ids

# ============================================================
# 5. PROCESS ASYNC RESULT
# ============================================================

def process_api_result(result):
    product_id = result["id"]
    error_type = classify_error(result)

    if not result["success"]:
        return {
            "product": None,
            "failed": {
                "id": product_id,
                "status_code": result["status_code"],
                "error": result["error"],
                "error_type": error_type,
                "attempts": result.get("attempts", 1),
            },
            "warning": None,
        }

    product = clean_product(result["data"])
    validation_result = validate_product(product)

    if not validation_result["is_valid"]:
        return {
            "product": None,
            "failed": {
                "id": product_id,
                "status_code": result["status_code"],
                "error": "INVALID_PRODUCT",
                "error_type": "INVALID_PRODUCT",
                "warnings": validation_result["warnings"],
                "attempts": result.get("attempts", 1),
            },
            "warning": None,
        }

    warning = None

    if validation_result["warnings"]:
        warning = {
            "id": product_id,
            "warnings": validation_result["warnings"],
        }

    return {
        "product": product,
        "failed": None,
        "warning": warning,
    }

# ============================================================
# 6. PROCESS ONE BATCH ASYNC
# ============================================================

async def process_batch_async(batch_ids, batch_index):
    print(f"\nProcessing async batch {batch_index} | total IDs: {len(batch_ids)}")

    products = []
    failed = []
    warnings = []

    semaphore = asyncio.Semaphore(CONCURRENCY)

    async with aiohttp.ClientSession() as session:

        async def fetch_one(product_id):
            async with semaphore:
                return await fetch_product_with_retry_async(
                    session=session,
                    product_id=product_id,
                    max_retries=MAX_RETRIES,
                    retry_sleep_seconds=RETRY_SLEEP_SECONDS,
                    timeout=TIMEOUT,
                )

        tasks = [
            fetch_one(product_id)
            for product_id in batch_ids
        ]

        results = await asyncio.gather(*tasks)

    for result in results:
        product_id = result["id"]
        processed_result = process_api_result(result)

        if processed_result["failed"]:
            failed.append(processed_result["failed"])
            save_processed_id(PROCESSED_IDS_FILE, product_id)
            continue

        products.append(processed_result["product"])
        save_processed_id(PROCESSED_IDS_FILE, product_id)

        if processed_result["warning"]:
            warnings.append(processed_result["warning"])

    products_file = PRODUCTS_DIR / get_batch_file_name(batch_index, prefix="products")
    failed_file = FAILED_DIR / get_batch_file_name(batch_index, prefix="failed")
    warnings_file = WARNINGS_DIR / get_batch_file_name(batch_index, prefix="warnings")

    write_json(products, products_file)
    write_json(failed, failed_file)
    write_json(warnings, warnings_file)

    print(
        f"Batch {batch_index} completed: "
        f"success={len(products)}, failed={len(failed)}, warnings={len(warnings)}"
    )

    return products, failed, warnings

# ============================================================
# 7. BUILD SUMMARY FROM ALL OUTPUT FILES
# ============================================================

def read_all_json_files(folder, pattern):
    items = []

    for file_path in sorted(folder.glob(pattern)):
        data = read_json(file_path)

        if isinstance(data, list):
            items.extend(data)

    return items


def build_summary_from_output():
    products = read_all_json_files(PRODUCTS_DIR, "products_*.json")
    failed = read_all_json_files(FAILED_DIR, "failed_*.json")
    warnings = read_all_json_files(WARNINGS_DIR, "warnings_*.json")

    return products, failed, warnings

# ============================================================
# 8. RUN ASYNC BATCH PIPELINE
# ============================================================

async def run_batches_async():
    original_ids, _ = load_product_ids()

    processed_ids = load_processed_ids(PROCESSED_IDS_FILE)

    batches = list(split_into_batches(original_ids, BATCH_SIZE))

    checkpoint = load_checkpoint(CHECKPOINT_FILE)

    print(f"Loaded checkpoint: {checkpoint}")
    print(f"Batch size        : {BATCH_SIZE}")
    print(f"Concurrency       : {CONCURRENCY}")

    start_time = datetime.now()

    for batch_index, batch_ids in enumerate(batches, start=1):
        # Lọc ID chưa xử lý ngay trong batch gốc để resume đúng vị trí
        batch_remaining_ids = filter_unprocessed_ids(batch_ids, processed_ids)

        if not batch_remaining_ids:
            print(f"Skip batch {batch_index} because all IDs already processed.")
            continue

        products, failed, warnings = await process_batch_async(
            batch_remaining_ids,
            batch_index
        )

        processed_ids = load_processed_ids(PROCESSED_IDS_FILE)
        processed_products = len(processed_ids)

        save_checkpoint(
            checkpoint_file=CHECKPOINT_FILE,
            last_completed_batch=batch_index,
            processed_products=processed_products,
        )

        print(f"Checkpoint saved: batch {batch_index}")

    end_time = datetime.now()

    # Đọc lại toàn bộ output để summary phản ánh tổng thể, không chỉ phần resume
    all_products, all_failed, all_warnings = build_summary_from_output()

    if not all_products and not all_failed and not all_warnings:
        print("No output data found. Existing output will not be overwritten.")
        return

    processed_count = len(load_processed_ids(PROCESSED_IDS_FILE))
    final_checkpoint = load_checkpoint(CHECKPOINT_FILE)

    summary = build_summary(
        input_count=len(original_ids),
        products=all_products,
        failed=all_failed,
        warnings=all_warnings,
        start_time=start_time,
        end_time=end_time,
    )

    write_json(summary, SUMMARY_FILE)

    print_summary(
        summary=summary,
        checkpoint=final_checkpoint,
        processed_count=processed_count,
    )

    print("\nAsync batch run completed.")
    print(f"Summary saved to: {SUMMARY_FILE}")

# ============================================================
# 9. ENTRY POINT
# ============================================================

if __name__ == "__main__":
    asyncio.run(run_batches_async())