from pathlib import Path


def load_processed_ids(processed_file):
    """
    Đọc danh sách product_id đã xử lý.

    Return:
        set[str]
    """
    processed_file = Path(processed_file)

    if not processed_file.exists():
        return set()

    with open(processed_file, "r", encoding="utf-8") as f:
        return {
            line.strip()
            for line in f
            if line.strip()
        }


def save_processed_id(processed_file, product_id):
    """
    Lưu một product_id đã xử lý xong.
    Ghi dạng append để không phải ghi lại toàn bộ file.
    """
    processed_file = Path(processed_file)
    processed_file.parent.mkdir(parents=True, exist_ok=True)

    with open(processed_file, "a", encoding="utf-8") as f:
        f.write(f"{product_id}\n")


def filter_unprocessed_ids(product_ids, processed_ids):
    """
    Loại bỏ các ID đã xử lý khỏi danh sách đầu vào.
    """
    return [
        str(product_id)
        for product_id in product_ids
        if str(product_id) not in processed_ids
    ]