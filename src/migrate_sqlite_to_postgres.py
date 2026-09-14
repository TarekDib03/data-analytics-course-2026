"""
Migrate SQLite databases (Chinook and project-db) into PostgreSQL,
each into its own schema within the analytics_course database.

Usage:
    python src/migrate_sqlite_to_postgres.py

Requires:
    pip install psycopg2-binary sqlalchemy pandas

Before running, create the target schemas once in pgAdmin's Query Tool:
    CREATE SCHEMA IF NOT EXISTS chinook;
    CREATE SCHEMA IF NOT EXISTS project_db;
"""

import os
import re
import sqlite3
from urllib.parse import quote_plus
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()  # reads variables from a local .env file (never committed to git)

# --- Configuration ---
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")   # set this in your local .env file
POSTGRES_HOST = "localhost"
POSTGRES_PORT = "5432"
POSTGRES_DB = "analytics_course"

if not POSTGRES_PASSWORD:
    raise ValueError(
        "POSTGRES_PASSWORD not found. Create a .env file in the repo root "
        "with a line like: POSTGRES_PASSWORD=your_actual_password"
    )

DATABASES_TO_MIGRATE = [
    {
        "sqlite_path": "data/raw/Chinook_Sqlite.sqlite",
        "target_schema": "chinook",
    },
    {
        "sqlite_path": "data/raw/project-db.db",
        "target_schema": "project_db",
    },
]


def standardize_column_name(col: str) -> str:
    """
    Convert any column name into consistent, Postgres-safe snake_case:
    'Category' -> 'category', 'Sub-Category' -> 'sub_category',
    'Ship Mode' -> 'ship_mode'.

    This matters more in Postgres than SQLite: Postgres folds *unquoted*
    identifiers to lowercase automatically, but a column created with any
    uppercase letters gets stored as a case-sensitive quoted identifier.
    Standardizing every column to lowercase snake_case up front avoids
    that mismatch entirely.
    """
    col = col.strip().lower()
    col = re.sub(r"[\s\-]+", "_", col)
    return col


def get_sqlite_table_names(sqlite_path: str) -> list[str]:
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables


def migrate_database(sqlite_path: str, target_schema: str, pg_engine):
    sqlite_conn = sqlite3.connect(sqlite_path)
    table_names = get_sqlite_table_names(sqlite_path)

    print(f"\nMigrating '{sqlite_path}' -> schema '{target_schema}' ({len(table_names)} tables found)")

    for table_name in table_names:
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql_query(query, sqlite_conn)
        df.columns = [standardize_column_name(c) for c in df.columns]
        df.to_sql(
            table_name.lower(),      # Postgres convention: lowercase table names
            pg_engine,
            schema=target_schema,
            if_exists="replace",
            index=False,
        )
        print(f"  -> {table_name} ({len(df)} rows) migrated to {target_schema}.{table_name.lower()}")
        print(f"     columns: {list(df.columns)}")

    sqlite_conn.close()


if __name__ == "__main__":
    import pandas as pd  # imported here so the module-level docstring stays clean

    pg_connection_string = (
        f"postgresql://{POSTGRES_USER}:{quote_plus(POSTGRES_PASSWORD)}"
        f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    pg_engine = create_engine(pg_connection_string)

    for db_config in DATABASES_TO_MIGRATE:
        migrate_database(db_config["sqlite_path"], db_config["target_schema"], pg_engine)

    print("\nMigration complete. Refresh pgAdmin to see the new schemas and tables.")
