import json
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


# Project root: ecommerce-sales-analytics/
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "raw"

load_dotenv(PROJECT_ROOT / ".env")


def get_engine():
    required = ["DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD"]

    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise ValueError(f"Missing environment variables: {missing}")

    connection_url = URL.create(
        drivername="postgresql+psycopg",
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.environ["DB_NAME"],
    )

    return create_engine(connection_url)


def load_json_file(filename):
    file_path = DATA_DIR / filename

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_records(engine, table_name, id_column, records):
    # table_name and id_column are fixed constants defined below.
    query = text(f"""
        INSERT INTO bronze.{table_name}
            ({id_column}, raw_data)
        VALUES
            (:record_id, CAST(:raw_data AS JSONB))
        ON CONFLICT ({id_column})
        DO UPDATE SET
            raw_data = EXCLUDED.raw_data,
            loaded_at = CURRENT_TIMESTAMP
    """)

    rows = [
        {
            "record_id": record["id"],
            "raw_data": json.dumps(record, ensure_ascii=False),
        }
        for record in records
    ]

    with engine.begin() as connection:
        if rows:
            connection.execute(query, rows)

    print(f"Loaded {len(rows)} records into bronze.{table_name}")


def main():
    engine = get_engine()

    try:
        products_data = load_json_file("products.json")
        carts_data = load_json_file("carts.json")
        users_data = load_json_file("users.json")

        load_records(
            engine, "raw_products", "product_id",
            products_data["products"]
        )
        load_records(
            engine, "raw_carts", "cart_id",
            carts_data["carts"]
        )
        load_records(
            engine, "raw_users", "user_id",
            users_data["users"]
        )

        print("Bronze loading completed!")

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
