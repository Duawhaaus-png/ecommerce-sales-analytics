import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import URL
PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")

def get_engine():
    connection_url = URL.create(
        drivername = "postgresql+psycopg",
        username = os.environ["DB_USER"],
        password = os.environ["DB_PASSWORD"],
        host = os.environ.get("DB_HOST","localhost"),
        port = int(os.environ.get("DB_PORT","5432")),
        database = os.environ["DB_NAME"],
    )
    return create_engine(connection_url)
def transform_products(conn):
    conn.execute(text("""
        INSERT INTO silver.products (
            product_id, title, category, brand, 
            price, discount_pct, rating,stock,sku, 
            availability, dwh_create_date
        )
        SELECT 
            (raw_data ->> 'id'):: INTEGER,
            NULLIF(TRIM(raw_data ->> 'title'), ''),
            NULLIF(TRIM(raw_data ->> 'category'), ''),
            NULLIF(TRIM(raw_data ->> 'brand'), ''),
            NULLIF(TRIM(raw_data ->> 'price'), ''):: NUMERIC,
            NULLIF(TRIM(raw_data ->> 'discountPercentage'), ''):: NUMERIC,
            NULLIF(TRIM(raw_data ->> 'rating'), ''):: NUMERIC,
            NULLIF(TRIM(raw_data ->> 'stock'), ''):: NUMERIC,
            NULLIF(TRIM(raw_data ->> 'sku'), ''),
            NULLIF(TRIM(raw_data ->> 'availabilityStatus'), ''),
            CURRENT_TIMESTAMP
        FROM bronze.raw_products
        WHERE raw_data ->> 'id' ~ '^[0-9]+$'
        ON CONFLICT (product_id) DO UPDATE SET
            title = EXCLUDED.title,
            category = EXCLUDED.category,
            brand = EXCLUDED.brand,
            price = EXCLUDED.price,
            discount_pct = EXCLUDED.discount_pct,
            rating = EXCLUDED.rating,
            stock = EXCLUDED.stock,
            sku = EXCLUDED.sku,
            availability = EXCLUDED.availability,
            dwh_create_date = EXCLUDED.dwh_create_date
    """))
    print("Silver products transformed")

def transform_users(conn):
    conn.execute(text("""
        INSERT INTO silver.users (
            user_id, first_name, last_name, username, age,
            gender,email, dwh_create_date)
        SELECT
            (raw_data ->> 'id'):: INTEGER,
            NULLIF(TRIM(raw_data ->> 'firstName'), ''),
            NULLIF(TRIM(raw_data ->> 'lastName'), ''),
            NULLIF(TRIM(raw_data ->> 'username'), ''),
            (raw_data ->> 'age'):: INTEGER,
            NULLIF(TRIM(raw_data ->> 'gender'), ''),
            NULLIF(TRIM(raw_data ->> 'email'), ''), 
            CURRENT_TIMESTAMP
        FROM bronze.raw_users
        WHERE raw_data ->> 'id' ~ '^[0-9]+$'
        ON CONFLICT(user_id) DO UPDATE SET 
            first_name = EXCLUDED.first_name,
            last_name = EXCLUDED.last_name,
            username = EXCLUDED.username,
            age = EXCLUDED.age,
            gender = EXCLUDED.gender,
            email = EXCLUDED.email,
            dwh_create_date = CURRENT_TIMESTAMP
    """))
    print("Silver users transformed")
def transform_carts(conn):
    conn.execute(text("""
        INSERT INTO silver.carts(
            cart_id, user_id, total, discounted_total,
            total_products, total_quantity, dwh_create_date)
        SELECT 
            (raw_data ->> 'id'):: INTEGER,
            (raw_data ->> 'userId'):: INTEGER,
            (raw_data ->> 'total'):: NUMERIC,
            (raw_data ->> 'discountedTotal'):: NUMERIC,
            (raw_data ->> 'totalProducts'):: INTEGER,
            (raw_data ->> 'totalQuantity'):: INTEGER,
            CURRENT_TIMESTAMP
        FROM bronze.raw_carts
        WHERE raw_data ->> 'id' ~ '^[0-9]+$'
        ON CONFLICT (cart_id) DO UPDATE SET 
            user_id = EXCLUDED.user_id,
            total = EXCLUDED.total,
            discounted_total = EXCLUDED.discounted_total,
            total_products = EXCLUDED.total_products,
            total_quantity = EXCLUDED.total_quantity,
            dwh_create_date = CURRENT_TIMESTAMP
    """))
    print("Silver carts transformed")
    conn.execute(text("""
        INSERT INTO silver.cart_items(
            cart_id, product_id, quantity, 
            unit_price,line_total,dwh_create_date)
        SELECT DISTINCT ON (
            c.raw_data ->> 'id',
            item ->> 'id'
            )
            (c.raw_data ->> 'id')::INTEGER,
            (item ->> 'id')::INTEGER,
            (item->> 'quantity'):: INTEGER,
            (item ->> 'price'):: NUMERIC,
            (item ->> 'total'):: NUMERIC,
            CURRENT_TIMESTAMP
            FROM bronze.raw_carts c
            CROSS JOIN LATERAL 
                jsonb_array_elements(c.raw_data -> 'products') AS p(item)
            WHERE c.raw_data ->> 'id' ~ '^[0-9]+$' AND item ->> 'id' ~ '^[0-9]+$'
            ORDER BY c.raw_data ->> 'id', item ->> 'id'
            ON CONFLICT (cart_id, product_id) DO UPDATE SET 
                quantity = EXCLUDED.quantity,
                unit_price = EXCLUDED.unit_price,
                line_total = EXCLUDED.line_total,
                dwh_create_date = CURRENT_TIMESTAMP
    """))
    print("Silver cart_items transformed")
def main():
    engine = get_engine()

    try:
        with engine.begin() as conn:
            transform_users(conn)
            transform_products(conn)
            transform_carts(conn)
        print("Silver transformation completed successfully")
    finally:
        engine.dispose()
if __name__ == "__main__":
    main()

