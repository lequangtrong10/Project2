from bs4 import BeautifulSoup
import html
import re


def clean_description(raw_description):
    """
    Làm sạch mô tả sản phẩm từ HTML thành plain text.
    """
    if raw_description is None:
        return ""

    # Decode HTML entities: &nbsp;, &amp;,...
    text = html.unescape(str(raw_description))

    # Remove HTML tags
    soup = BeautifulSoup(text, "html.parser")
    text = soup.get_text(separator=" ")

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


def extract_image_urls(images):
    """
    Lấy danh sách base_url từ field images của Tiki.
    """
    if not isinstance(images, list):
        return []

    image_urls = []

    for image in images:
        if isinstance(image, dict) and image.get("base_url"):
            image_urls.append(image["base_url"])

    return image_urls


def clean_product(raw_data):
    """
    Lấy các field cần thiết từ raw API response.
    """
    return {
        "id": raw_data.get("id"),
        "name": raw_data.get("name"),
        "url_key": raw_data.get("url_key"),
        "price": raw_data.get("price"),
        "description": clean_description(raw_data.get("description")),
        "images": extract_image_urls(raw_data.get("images")),
    }