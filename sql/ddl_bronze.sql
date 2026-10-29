/*
===============================================================================
DDL Script: Create Bronze Tables
===============================================================================
Script Purpose:
    This script creates tables in the 'bronze' schema, dropping existing tables 
    if they already exist.
	  Run this script to re-define the DDL structure of 'bronze' Tables
===============================================================================
*/

IF OBJECT_ID('bronze.raw_carts', 'U') IS NOT NULL
    DROP TABLE bronze.raw_carts;
create table bronze.raw_carts(
	cart_id INT primary key,
	raw_data JSONB not null,
	loaded_at TIMESTAMPTZ default current_timestamp 
);

IF OBJECT_ID('bronze.raw_products', 'U') IS NOT NULL
    DROP TABLE bronze.raw_products;

create table bronze.raw_products(
	product_id INT primary key,
	raw_data JSONB not null,
	loaded_at TIMESTAMPTZ default current_timestamp 
);

IF OBJECT_ID('bronze.raw_users', 'U') IS NOT NULL
    DROP TABLE bronze.raw_users;

create table bronze.raw_users(
	user_id INT primary key,
	raw_data JSON not null,
	loaded_at TIMESTAMPTZ default current_timestamp 
);

