from pydantic import BaseModel, StrictInt, ValidationError, field_validator


class Product(BaseModel):
    id: StrictInt
    name: str
    url_key: str

    @field_validator("name", "url_key")
    @classmethod
    def required_string_not_blank(cls, value: str) -> str:
        if value.strip() == "":
            raise ValueError("blank")
        return value


def validate_product(product: dict) -> dict:
    required_warnings = []
    try:
        Product(**product)
    except ValidationError as exc:
        seen = set()
        for error in exc.errors():
            field = error["loc"][0] if error["loc"] else "unknown"
            warning = f"missing_required_field:{field}"
            if warning not in seen:
                required_warnings.append(warning)
                seen.add(warning)

    optional_warnings = []

    if product.get("price") is None:
        optional_warnings.append("missing_price")

    if not product.get("description"):
        optional_warnings.append("missing_description")

    if not product.get("images"):
        optional_warnings.append("missing_images")

    warnings = required_warnings + optional_warnings
    is_valid = len(required_warnings) == 0

    return {"is_valid": is_valid, "warnings": warnings}