import pytest
from src.product_validator import validate_product

VALID_PRODUCT = {
    "id": 12345,
    "name": "Áo thun nam",
    "url_key": "ao-thun-nam-12345",
    "price": 199000,
    "description": "Áo thun cotton 100%",
    "images": ["https://example.com/img1.jpg"],
}

def make_product(**overrides):
    product = VALID_PRODUCT.copy()
    product.update(overrides)
    return product


class TestRequiredFields:

    @pytest.mark.parametrize("field", ["id", "name", "url_key"])
    def test_missing_required_field_as_none(self, field):
        product = make_product(**{field: None})
        result = validate_product(product)

        assert result["is_valid"] is False
        assert f"missing_required_field:{field}" in result["warnings"]

    @pytest.mark.parametrize("field", ["id", "name", "url_key"])
    def test_missing_required_field_as_empty_string(self, field):
        product = make_product(**{field: ""})
        result = validate_product(product)

        assert result["is_valid"] is False
        assert f"missing_required_field:{field}" in result["warnings"]

    @pytest.mark.parametrize("field", ["id", "name", "url_key"])
    def test_missing_required_field_key_absent(self, field):
        product = make_product()
        del product[field]
        result = validate_product(product)

        assert result["is_valid"] is False
        assert f"missing_required_field:{field}" in result["warnings"]

    def test_id_as_numeric_string_is_rejected(self):
        product = make_product(id="12345")
        result = validate_product(product)

        assert result["is_valid"] is False
        assert "missing_required_field:id" in result["warnings"]


class TestOptionalFields:

    def test_missing_price_still_valid(self):
        product = make_product(price=None)
        result = validate_product(product)

        assert result["is_valid"] is True
        assert "missing_price" in result["warnings"]

    def test_price_zero_is_not_flagged(self):
        product = make_product(price=0)
        result = validate_product(product)
        assert result["is_valid"] is True
        assert "missing_price" not in result["warnings"]

    def test_missing_description_still_valid(self):
        product = make_product(description="")
        result = validate_product(product)
        assert result["is_valid"] is True
        assert "missing_description" in result["warnings"]

    @pytest.mark.parametrize("images_value", [None, [], ""])
    def test_missing_images_still_valid(self, images_value):
        product = make_product(images=images_value)
        result = validate_product(product)
        assert result["is_valid"] is True
        assert "missing_images" in result["warnings"]

    def test_images_with_content_no_warning(self):
        product = make_product(images=["https://example.com/a.jpg"])
        result = validate_product(product)
        assert "missing_images" not in result["warnings"]


class TestFullyValidProduct:
    def test_no_warnings_when_everything_present(self):
        result = validate_product(VALID_PRODUCT)
        assert result["is_valid"] is True
        assert result["warnings"] == []

class TestCombinedCases:
    def test_missing_required_and_optional_together(self):
        product = make_product(id=None, description="")
        result = validate_product(product)

        assert result["is_valid"] is False
        assert "missing_required_field:id" in result["warnings"]
        assert "missing_description" in result["warnings"]
        assert len(result["warnings"]) == 2

    def test_whitespace_only_required_field_is_now_caught(self):
        product = make_product(name="   ")
        result = validate_product(product)

        assert result["is_valid"] is False
        assert "missing_required_field:name" in result["warnings"]