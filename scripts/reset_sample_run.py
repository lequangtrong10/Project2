from pathlib import Path
import shutil


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "data" / "output"

FILES_TO_DELETE = [
    OUTPUT_DIR / "reports" / "checkpoint_sample.json",
    OUTPUT_DIR / "reports" / "processed_ids_sample.txt",
    OUTPUT_DIR / "reports" / "summary_batches_sample.json",

    OUTPUT_DIR / "reports" / "checkpoint_async.json",
    OUTPUT_DIR / "reports" / "processed_ids_async.txt",
    OUTPUT_DIR / "reports" / "summary_async.json",
]

DIRS_TO_CLEAN = [
    OUTPUT_DIR / "products",
    OUTPUT_DIR / "failed",
    OUTPUT_DIR / "warnings",
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