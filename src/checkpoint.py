from pathlib import Path
from datetime import datetime
import json


DEFAULT_CHECKPOINT = {
    "last_completed_batch": 0,
    "processed_products": 0,
    "updated_at": None
}


def load_checkpoint(checkpoint_file):
    """
    Đọc checkpoint hiện tại.

    Nếu chưa có checkpoint thì trả về trạng thái mặc định.
    """
    checkpoint_file = Path(checkpoint_file)

    if not checkpoint_file.exists():
        return DEFAULT_CHECKPOINT.copy()

    with open(checkpoint_file, "r", encoding="utf-8") as f:
        return json.load(f)


def save_checkpoint(checkpoint_file, last_completed_batch, processed_products):
    """
    Lưu checkpoint sau khi hoàn thành một batch.
    """
    checkpoint_file = Path(checkpoint_file)
    checkpoint_file.parent.mkdir(parents=True, exist_ok=True)

    checkpoint = {
        "last_completed_batch": last_completed_batch,
        "processed_products": processed_products,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(checkpoint_file, "w", encoding="utf-8") as f:
        json.dump(checkpoint, f, ensure_ascii=False, indent=2)

    return checkpoint


def reset_checkpoint(checkpoint_file):
    """
    Xóa checkpoint để chạy lại từ đầu.
    """
    checkpoint_file = Path(checkpoint_file)

    if checkpoint_file.exists():
        checkpoint_file.unlink()