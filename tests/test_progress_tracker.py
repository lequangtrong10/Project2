from src.progress_tracker import (
    load_processed_ids,
    save_processed_id,
    filter_unprocessed_ids,
)

def test_filter_unprocessed_ids():
    original_ids = ["1", "2", "3", "4", "5"]
    processed_ids = {"2", "4"}
    remaining = filter_unprocessed_ids(original_ids, processed_ids)
    assert remaining == ["1", "3", "5"]

def test_filter_unprocessed_ids_converts_int_ids_to_str():
    original_ids = [1, 2, 3]
    processed_ids = {"2"}
    remaining = filter_unprocessed_ids(original_ids, processed_ids)
    assert remaining == ["1", "3"]

def test_load_processed_ids_returns_empty_set_when_file_missing(tmp_path):
    processed_file = tmp_path / "khong_ton_tai.txt"
    result = load_processed_ids(processed_file)
    assert result == set()

def test_save_then_load_processed_ids(tmp_path):
    processed_file = tmp_path / "processed.txt"
    save_processed_id(processed_file, "111")
    save_processed_id(processed_file, "222")
    save_processed_id(processed_file, "333")
    result = load_processed_ids(processed_file)
    assert result == {"111", "222", "333"}

def test_save_processed_id_creates_parent_dir(tmp_path):
    processed_file = tmp_path / "nested" / "deeper" / "processed.txt"
    save_processed_id(processed_file, "1")
    assert processed_file.exists()

def test_load_processed_ids_skips_blank_lines(tmp_path):
    processed_file = tmp_path / "processed.txt"
    processed_file.write_text("111\n\n222\n   \n333\n", encoding="utf-8")
    result = load_processed_ids(processed_file)
    assert result == {"111", "222", "333"}