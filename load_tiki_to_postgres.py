import json
from pathlib import Path

import psycopg2
from psycopg2.extras import Json

from db_config import load_config


PRODUCT_DIR = Path("data/output/products")


def load_products_to_postgres():
    insert_sql = """
        INSERT INTO tiki_products (
            product_id,
            name,
            url_key,
            price,
            description,
            images,
            source_file
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (product_id)
        DO UPDATE SET
            name = EXCLUDED.name,
            url_key = EXCLUDED.url_key,
            price = EXCLUDED.price,
            description = EXCLUDED.description,
            images = EXCLUDED.images,
            source_file = EXCLUDED.source_file;
    """

    total_files = 0
    total_products = 0
    failed_products = 0

    product_files = sorted(PRODUCT_DIR.glob("products_*.json"))

    if not product_files:
        print(f"No product files found in {PRODUCT_DIR}")
        return

    config = load_config()

    with psycopg2.connect(**config) as conn:
        with conn.cursor() as cur:
            for file_path in product_files:
                total_files += 1

                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        products = json.load(file)

                    for product in products:
                        try:
                            cur.execute(
                                insert_sql,
                                (
                                    product.get("id"),
                                    product.get("name"),
                                    product.get("url_key"),
                                    product.get("price"),
                                    product.get("description"),
                                    Json(product.get("images", [])),
                                    file_path.name,
                                ),
                            )
                            total_products += 1

                        except Exception as error:
                            failed_products += 1
                            print(
                                f"[ROW ERROR] file={file_path.name}, "
                                f"id={product.get('id')}, error={error}"
                            )

                    conn.commit()
                    print(f"Loaded {file_path.name}")

                except Exception as error:
                    conn.rollback()
                    print(f"[FILE ERROR] {file_path}: {error}")

    print("========================================")
    print("LOAD SUMMARY")
    print("========================================")
    print(f"Files processed : {total_files}")
    print(f"Products loaded : {total_products}")
    print(f"Products failed : {failed_products}")


if __name__ == "__main__":
    load_products_to_postgres()
