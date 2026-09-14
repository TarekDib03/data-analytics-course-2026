"""
Build project-db.db from raw source files.

Run this once (or any time you need to regenerate the database from scratch)
before running any notebooks that depend on project-db.db:

    python src/build_project_db.py

Sources combined:
  - data/raw/project-db.txt   -> creates departments, regions, employees tables
  - data/raw/Sales.csv        -> creates the sales table
  - data/raw/Customers.csv    -> creates the customers table
"""

import sqlite3
import re
import pandas as pd

DB_PATH = "data/raw/project-db.db"
SQL_SCRIPT_PATH = "data/raw/project-db.txt"
SALES_CSV_PATH = "data/raw/Sales.csv"
CUSTOMERS_CSV_PATH = "data/raw/Customers.csv"


def standardize_column_name(col: str) -> str:
    """
    Convert a raw column name into a consistent snake_case format:
    'Customer ID' -> 'customer_id', 'Sub-Category' -> 'sub_category'.

    Lowercases everything, then replaces any run of spaces/hyphens/
    underscores with a single underscore.
    """
    col = col.strip().lower()
    col = re.sub(r"[\s\-]+", "_", col)
    return col


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [standardize_column_name(c) for c in df.columns]
    return df


def build_database():
    conn = sqlite3.connect(DB_PATH)

    # Step 1: run the raw SQL script to create departments, regions, employees
    with open(SQL_SCRIPT_PATH, "r") as f:
        sql_script = f.read()
    conn.executescript(sql_script)
    print("Created departments, regions, and employees tables from project-db.txt")

    # Step 2: load and standardize the Sales CSV, then write to 'sales' table
    sales_df = pd.read_csv(SALES_CSV_PATH)
    sales_df = standardize_columns(sales_df)
    sales_df.to_sql("sales", conn, if_exists="replace", index=False)
    print(f"Loaded sales table with columns: {list(sales_df.columns)}")

    # Step 3: load and standardize the Customers CSV, then write to 'customers' table
    customers_df = pd.read_csv(CUSTOMERS_CSV_PATH)
    customers_df = standardize_columns(customers_df)
    customers_df.to_sql("customers", conn, if_exists="replace", index=False)
    print(f"Loaded customers table with columns: {list(customers_df.columns)}")

    conn.close()
    print(f"\nDatabase built successfully at {DB_PATH}")


if __name__ == "__main__":
    build_database()
