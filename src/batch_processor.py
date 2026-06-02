def split_into_batches(items, batch_size):
    """
    Chia danh sách items thành nhiều batch nhỏ.

    Ví dụ:
        items = [1, 2, 3, 4, 5]
        batch_size = 2

        Kết quả:
        [[1, 2], [3, 4], [5]]
    """

    if batch_size <= 0:
        raise ValueError("batch_size phải lớn hơn 0")

    for start_index in range(0, len(items), batch_size):
        yield items[start_index:start_index + batch_size]


def get_batch_file_name(batch_index, prefix="products", extension="json"):
    """
    Tạo tên file output theo batch.

    Ví dụ:
        batch_index = 1
        => products_0001.json
    """

    return f"{prefix}_{batch_index:04d}.{extension}"