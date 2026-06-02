REQUIRED_FIELDS = ["id", "name", "url_key"]


def validate_product(product):
    """
    Kiểm tra chất lượng dữ liệu sản phẩm sau khi clean.

    Return:
        {
            "is_valid": bool,
            "warnings": list[str]
        }
    """
    warnings = []

    # Field bắt buộc
    for field in REQUIRED_FIELDS:
        if product.get(field) in [None, ""]:
            warnings.append(f"missing_required_field:{field}")

    # Field quan trọng nhưng có thể thiếu
    if product.get("price") is None:
        warnings.append("missing_price")

    if not product.get("description"):
        warnings.append("missing_description")

    if not product.get("images"):
        warnings.append("missing_images")

    is_valid = all(
        not warning.startswith("missing_required_field")
        for warning in warnings
    )

    return {
        "is_valid": is_valid,
        "warnings": warnings
    }