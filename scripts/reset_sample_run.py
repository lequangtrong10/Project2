from pathlib import Path
import shutil
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from config.settings import CONFIG
REPORTS_DIR = BASE_DIR / CONFIG["output"]["reports_dir"]
PRODUCTS_DIR = BASE_DIR / CONFIG["output"]["products_dir"]
FAILED_DIR = BASE_DIR / CONFIG["output"]["failed_dir"]
WARNINGS_DIR = BASE_DIR / CONFIG["output"]["warnings_dir"]

FILES_TO_DELETE = [
    # Active crawler output files
    REPORTS_DIR / "checkpoint.json",
    REPORTS_DIR / "processed_ids.txt",
    REPORTS_DIR / "summary.json",
    REPORTS_DIR / "recovered_products.json",
    REPORTS_DIR / "final_failed.json",
    REPORTS_DIR / "retry_summary.json",

    # Legacy/Outdated filenames (for backward compatibility)
    REPORTS_DIR / "checkpoint_sample.json",
    REPORTS_DIR / "processed_ids_sample.txt",
    REPORTS_DIR / "summary_batches_sample.json",
    REPORTS_DIR / "checkpoint_async.json",
    REPORTS_DIR / "processed_ids_async.txt",
    REPORTS_DIR / "summary_async.json",
]

DIRS_TO_CLEAN = [
    PRODUCTS_DIR,
    FAILED_DIR,
    WARNINGS_DIR,
]


def delete_file(file_path):
    if file_path.exists():
        file_path.unlink()
        print(f"Deleted file: {file_path}")


def clean_directory(dir_path):
    if not dir_path.exists():
        return

    for item in dir_path.iterdir():
        if item.is_file():
            item.unlink()
            print(f"Deleted file: {item}")
        elif item.is_dir():
            shutil.rmtree(item)
            print(f"Deleted folder: {item}")


def reset_sample_run():
    print("Reset output files...")

    for file_path in FILES_TO_DELETE:
        delete_file(file_path)

    for dir_path in DIRS_TO_CLEAN:
        clean_directory(dir_path)

    print("Reset completed.")


if __name__ == "__main__":
    reset_sample_run()