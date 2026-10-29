/*
===============================================================================
DDL Script: Create Silver Tables
===============================================================================
Script Purpose:
    This script creates tables in the 'silver' schema, dropping existing tables 
    if they already exist.
	  Run this script to re-define the DDL structure of 'bronze' Tables
===============================================================================
*/

CREATE SCHEMA IF NOT EXISTS silver;

IF OBJECT_ID('silver.products', 'U') IS NOT NULL
    DROP TABLE silver.products;

-- 1. Products: thông tin sản phẩm đã chuẩn hóa
CREATE TABLE silver.products (
    product_id       INTEGER PRIMARY KEY,
    title            TEXT,
    category         TEXT,
    brand            TEXT,
    price            NUMERIC(12, 2),
    discount_pct     NUMERIC(8, 2),
    rating           NUMERIC(4, 2),
    stock            INTEGER,
    sku              TEXT,
    availability     TEXT,
    dwh_create_date       TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

IF OBJECT_ID('silver.users', 'U') IS NOT NULL
    DROP TABLE silver.users;
-- 2. Users: thông tin người dùng
CREATE TABLE silver.users (
    user_id          INTEGER PRIMARY KEY,
    first_name       TEXT,
    last_name        TEXT,
    username TEXT,
    age              INTEGER,
    gender           TEXT,
    email            TEXT,
    dwh_create_date       TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

IF OBJECT_ID('silver.carts', 'U') IS NOT NULL
    DROP TABLE silver.carts;

-- 3. Carts: thông tin giỏ hàng
CREATE TABLE IF NOT EXISTS silver.carts (
    cart_id          INTEGER PRIMARY KEY,
    user_id          INTEGER,
    total            NUMERIC(12, 2),
    discounted_total NUMERIC(12, 2),
    total_products   INTEGER,
    total_quantity   INTEGER,
    dwh_create_date       TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

IF OBJECT_ID('silver.cart_items', 'U') IS NOT NULL
    DROP TABLE silver.cart_items;

-- 4. Cart items: mỗi sản phẩm trong một giỏ hàng
CREATE TABLE silver.cart_items (
    cart_id          INTEGER,
    product_id       INTEGER,
    quantity         INTEGER,
    unit_price       NUMERIC(12, 2),
    line_total       NUMERIC(12, 2),
    dwh_create_date       TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    primary key(cart_id, product_id)
);
