import json
from json import JSONDecodeError
from pathlib import Path

import psycopg2
from psycopg2.extras import Json, execute_values

from config.settings import CONFIG
from db_config import load_config

BASE_DIR = Path(__file__).resolve().parent
PRODUCT_DIR = BASE_DIR / CONFIG["output"]["products_dir"]

INSERT_SQL = """
    INSERT INTO tiki_products (
        product_id,
        name,
        url_key,
        price,
        description,
        images,
        source_file
    )
    VALUES %s
    ON CONFLICT (product_id)
    DO UPDATE SET
        name = EXCLUDED.name,
        url_key = EXCLUDED.url_key,
        price = EXCLUDED.price,
        description = EXCLUDED.description,
        images = EXCLUDED.images,
        source_file = EXCLUDED.source_file;
"""


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


def build_insert_rows(products, source_file):
    rows = []
    skipped = 0

    for product in products:
        product_id = product.get("id")

        if product_id is None:
            print(f"[DATA ERROR] Missing required field 'id' in {source_file}")
            skipped += 1
            continue

        rows.append(
            (
                product_id,
                product.get("name"),
                product.get("url_key"),
                product.get("price"),
                product.get("description"),
                Json(product.get("images", [])),
                source_file,
            )
        )

    return rows, skipped


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

                    rows, skipped = build_insert_rows(products, file_path.name)
                    failed_products += skipped

                    if not rows:
                        print(f"Loaded {file_path.name}: 0/{len(products)} rows (all skipped)")
                        continue

                    try:
                        execute_values(cur, INSERT_SQL, rows, page_size=1000)
                        conn.commit()
                        total_products += len(rows)
                        print(f"Loaded {file_path.name}: {len(rows)} rows")

                    except psycopg2.Error as error:
                        conn.rollback()
                        failed_products += len(rows)
                        failed_files += 1
                        print(
                            f"[DB INSERT ERROR] source_file={file_path.name}, "
                            f"rows_attempted={len(rows)}, error={error}"
                        )

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