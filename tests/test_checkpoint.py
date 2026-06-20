from src.checkpoint import (
    DEFAULT_CHECKPOINT,
    load_checkpoint,
    save_checkpoint,
    reset_checkpoint,
)
def test_checkpoint_save_and_load(tmp_path):
    checkpoint_file = tmp_path / "checkpoint.json"
    save_checkpoint(
        checkpoint_file=checkpoint_file,
        last_completed_batch=10,
        processed_products=1000,
    )
    checkpoint = load_checkpoint(checkpoint_file)
    assert checkpoint["last_completed_batch"] == 10
    assert checkpoint["processed_products"] == 1000

def test_save_checkpoint_fills_updated_at(tmp_path):
    checkpoint_file = tmp_path / "checkpoint.json"

    result = save_checkpoint(
        checkpoint_file=checkpoint_file,
        last_completed_batch=1,
        processed_products=50,
    )
    assert result["updated_at"] is not None

def test_load_checkpoint_returns_default_when_file_missing(tmp_path):
    checkpoint_file = tmp_path / "khong_ton_tai.json"

    checkpoint = load_checkpoint(checkpoint_file)

    assert checkpoint == DEFAULT_CHECKPOINT

def test_save_checkpoint_creates_parent_dir(tmp_path):
    checkpoint_file = tmp_path / "nested" / "deeper" / "checkpoint.json"

    save_checkpoint(
        checkpoint_file=checkpoint_file,
        last_completed_batch=1,
        processed_products=1,
    )

    assert checkpoint_file.exists()

def test_reset_checkpoint_removes_file(tmp_path):
    checkpoint_file = tmp_path / "checkpoint.json"
    save_checkpoint(checkpoint_file=checkpoint_file, last_completed_batch=1, processed_products=1)
    assert checkpoint_file.exists()

    reset_checkpoint(checkpoint_file)

    assert not checkpoint_file.exists()

def test_reset_checkpoint_when_file_missing_does_not_raise(tmp_path):
    checkpoint_file = tmp_path / "khong_ton_tai.json"

    reset_checkpoint(checkpoint_file)