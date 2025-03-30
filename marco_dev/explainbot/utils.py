import os
import psycopg2 as ps
import pandas as pd

# LLM Params
MODEL_NAME = "mistral.mistral-7b-instruct-v0:2"
AWS_ACCESS_KEY_ID='AKIAVNMWFXLUQGG7LNFL'
AWS_SECRET_ACCESS_KEY='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'

# SQL Params
DB_CONFIG = {
    "host": "booksdataclean.cu9jy7bp7ol8.us-east-1.rds.amazonaws.com",
    "dbname": "booksfull",
    "port": "5432",
    "user": "postgres",
    "password": "S3EW5y9MhZzBBYXlCjE6",
}

def connect_to_db():
    """Establishes a connection to the PostgreSQL database"""
    try:
        conn = ps.connect(
            host=DB_CONFIG["host"],
            database=DB_CONFIG["dbname"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            port=DB_CONFIG["port"]
        )
        print("Connected to the database successfully!")
        return conn
    except ps.OperationalError as e:
        print(f"Database connection error: {e}")
        return None


def fetch_books_data():
    """
    Fetches book details from the database and returns a DataFrame
    """
    conn = connect_to_db()
    if conn is None:
        raise RuntimeError("Database connection failed.")

    query = """
        SELECT title, author, publish_year, genre_consolidated, description
        FROM book_titles;
    """
    books_df = pd.read_sql_query(query, conn)

    conn.close()
    return books_df
