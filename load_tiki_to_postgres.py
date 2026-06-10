import json
from json import JSONDecodeError
from pathlib import Path

import psycopg2
from psycopg2.extras import Json

from db_config import load_config


PRODUCT_DIR = Path("data/output/products")


def read_json_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    except FileNotFoundError:
        print(f"[FILE ERROR] File not found: {file_path}")
        return None

    except PermissionError:
        print(f"[FILE ERROR] Permission denied: {file_path}")
        return None

    except JSONDecodeError as error:
        print(f"[FILE ERROR] Invalid JSON: {file_path} | {error}")
        return None


def insert_product(cur, product, source_file):
    sql = """
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

    try:
        product_id = product["id"]

        cur.execute(
            sql,
            (
                product_id,
                product.get("name"),
                product.get("url_key"),
                product.get("price"),
                product.get("description"),
                Json(product.get("images", [])),
                source_file,
            ),
        )

        return True

    except KeyError as error:
        print(f"[DATA ERROR] Missing required field {error} in {source_file}")
        return False

    except psycopg2.Error as error:
        print(
            f"[DB INSERT ERROR] source_file={source_file}, "
            f"product_id={product.get('id')}, error={error}"
        )
        return False


def load_products_to_postgres():
    product_files = sorted(PRODUCT_DIR.glob("products_*.json"))

    total_files = 0
    total_products = 0
    failed_files = 0
    failed_products = 0

    if not product_files:
        print(f"[FILE ERROR] No product files found in {PRODUCT_DIR}")
        return

    try:
        config = load_config()

    except Exception as error:
        print(f"[CONFIG ERROR] Cannot load database config: {error}")
        return

    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                for file_path in product_files:
                    total_files += 1

                    products = read_json_file(file_path)

                    if products is None:
                        failed_files += 1
                        continue

                    if not isinstance(products, list):
                        print(f"[DATA ERROR] Expected list JSON: {file_path}")
                        failed_files += 1
                        continue

                    for product in products:
                        success = insert_product(cur, product, file_path.name)

                        if success:
                            total_products += 1
                        else:
                            failed_products += 1
                            conn.rollback()

                    conn.commit()
                    print(f"Loaded {file_path.name}")

    except psycopg2.OperationalError as error:
        print(f"[DB CONNECTION ERROR] Cannot connect to PostgreSQL: {error}")

    except psycopg2.Error as error:
        print(f"[DB ERROR] PostgreSQL error: {error}")

    except Exception as error:
        print(f"[UNEXPECTED ERROR] {error}")

    finally:
        print("========================================")
        print("LOAD SUMMARY")
        print("========================================")
        print(f"Files processed : {total_files}")
        print(f"Files failed    : {failed_files}")
        print(f"Products loaded : {total_products}")
        print(f"Products failed : {failed_products}")


if __name__ == "__main__":
    load_products_to_postgres()  
