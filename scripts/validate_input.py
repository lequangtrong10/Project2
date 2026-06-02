from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "input" / "products-0-200000.csv"

REPORT_DIR = BASE_DIR / "reports"
REPORT_DIR.mkdir(exist_ok=True)

CLEAN_FILE = REPORT_DIR / "products_clean.csv"
DUPLICATE_FILE = REPORT_DIR / "duplicate_ids.csv"
INVALID_FILE = REPORT_DIR / "invalid_ids.csv"
REPORT_FILE = REPORT_DIR / "validation_report.txt"


def validate_input():
    # 1. Kiểm tra file tồn tại
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {INPUT_FILE}")

    # 2. Đọc CSV
    df = pd.read_csv(INPUT_FILE)

    # 3. Kiểm tra cột id
    if "id" not in df.columns:
        raise ValueError("File CSV không có cột 'id'")

    total_rows = len(df)

    # 4. Chuẩn hóa dữ liệu
    df["id"] = df["id"].astype(str).str.strip()

    # 5. ID rỗng
    empty_mask = (df["id"] == "") | (df["id"].isna())

    # 6. ID không phải số
    numeric_mask = df["id"].str.fullmatch(r"\d+")

    invalid_mask = empty_mask | (~numeric_mask)

    invalid_df = df[invalid_mask].copy()

    # 7. Lấy dữ liệu hợp lệ
    valid_df = df[~invalid_mask].copy()

    # 8. Duplicate
    duplicate_mask = valid_df.duplicated(subset=["id"], keep="first")

    duplicate_df = valid_df[duplicate_mask].copy()

    # Giữ lần xuất hiện đầu tiên
    clean_df = valid_df.drop_duplicates(
        subset=["id"],
        keep="first"
    )

    # 9. Ghi file
    clean_df.to_csv(CLEAN_FILE, index=False)

    duplicate_df.to_csv(DUPLICATE_FILE, index=False)

    invalid_df.to_csv(INVALID_FILE, index=False)

    # 10. Thống kê
    report = (
        f"INPUT VALIDATION REPORT\n"
        f"{'-'*40}\n"
        f"Total Rows        : {total_rows}\n"
        f"Valid IDs         : {len(clean_df)}\n"
        f"Duplicate IDs     : {len(duplicate_df)}\n"
        f"Invalid IDs       : {len(invalid_df)}\n"
    )

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(report)

    print(report)
    print("Validation completed.")
    print(f"Clean file      : {CLEAN_FILE}")
    print(f"Duplicate file  : {DUPLICATE_FILE}")
    print(f"Invalid file    : {INVALID_FILE}")


if __name__ == "__main__":
    validate_input()