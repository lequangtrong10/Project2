from src.cleaner import clean_description, extract_image_urls, clean_product

class TestCleanDescription:
    def test_none_returns_empty_string(self):
        assert clean_description(None) == ""

    def test_strips_html_tags(self):
        raw = "<p>Hello <b>World</b></p>"
        assert clean_description(raw) == "Hello World"

    def test_decodes_html_entities(self):
        raw = "Cha &amp; con trai"
        result = clean_description(raw)
        assert "&amp;" not in result
        assert "&" in result

    def test_normalizes_whitespace(self):
        raw = "Dong   mot\n\nDong   hai"
        result = clean_description(raw)
        assert "  " not in result


class TestExtractImageUrls:
    def test_not_a_list_returns_empty(self):
        assert extract_image_urls(None) == []
        assert extract_image_urls("not a list") == []
        assert extract_image_urls({"base_url": "x"}) == []

    def test_extracts_base_url_from_valid_images(self):
        images = [
            {"base_url": "https://example.com/1.jpg"},
            {"base_url": "https://example.com/2.jpg"},
        ]
        assert extract_image_urls(images) == [
            "https://example.com/1.jpg",
            "https://example.com/2.jpg",
        ]

    def test_skips_malformed_entries(self):
        images = [
            {"base_url": "https://example.com/1.jpg"},
            {"no_base_url": "x"},
            "not_a_dict",
            {"base_url": ""},
        ]
        assert extract_image_urls(images) == ["https://example.com/1.jpg"]


class TestCleanProduct:
    def test_basic_passthrough_fields(self):
        raw_product = {"id": 123, "name": "Laptop", "price": 10000000}
        result = clean_product(raw_product)
        assert result["id"] == 123
        assert result["name"] == "Laptop"
        assert result["price"] == 10000000

    def test_missing_fields_become_none_or_empty(self):
        result = clean_product({"id": 1})
        assert result["url_key"] is None
        assert result["description"] == ""
        assert result["images"] == []

    def test_full_pipeline_cleans_description_and_images(self):
        raw_product = {
            "id": 1,
            "name": "Test",
            "url_key": "test",
            "price": 100,
            "description": "<p>Mo ta <b>san pham</b></p>",
            "images": [{"base_url": "https://example.com/a.jpg"}],
        }
        result = clean_product(raw_product)
        assert result["description"] == "Mo ta san pham"
        assert result["images"] == ["https://example.com/a.jpg"]