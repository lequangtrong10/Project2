import json
from pathlib import Path


def write_json(data, output_file):
    """
    Ghi dữ liệu ra file JSON.
    """
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def read_json(input_file):
    """
    Đọc file JSON.
    """
    input_file = Path(input_file)

    if not input_file.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {input_file}")

    with open(input_file, "r", encoding="utf-8") as f:
        return json.load(f)