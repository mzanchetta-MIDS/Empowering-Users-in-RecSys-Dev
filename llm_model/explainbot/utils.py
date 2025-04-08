import os
import psycopg2 as ps
import pandas as pd

# LLM Params
MODEL_NAME = "mistral.mistral-large-2402-v1:0"


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

## New
def fetch_books_data():
    """
    Fetches book details from the database and returns a DataFrame
    """
    conn = connect_to_db()
    if conn is None:
        raise RuntimeError("Database connection failed.")

    query = """
        WITH ranked_reviews AS (
            SELECT
                title,
                review_text,
                review_score,
                review_helpfulness,
                ROW_NUMBER() OVER (PARTITION BY title ORDER BY review_helpfulness DESC) AS RankNum
            FROM books_info
        ),
    
        top_reviews AS (
            SELECT
                title,
                CONCAT(review_text, ' (Score: ', review_score, ', Helpful: ', review_helpfulness, ')') AS formatted_review
            FROM ranked_reviews
            WHERE RankNum = 1
        )
    
        SELECT 
            b.title,
            b.author,
            b.publish_year,
            b.genre_consolidated,
            b.description,
            STRING_AGG(t.formatted_review, ' ') AS reviews
        FROM (
            SELECT DISTINCT title, author, publish_year, genre_consolidated, description
            FROM books_info
        ) b
        JOIN top_reviews t ON b.title = t.title
        GROUP BY 
            b.title, b.author, b.publish_year, b.genre_consolidated, b.description;
    """
    books_df = pd.read_sql_query(query, conn)

    conn.close()
    return books_df

# # OLD
# def fetch_books_data():
#     """
#     Fetches book details from the database and returns a DataFrame
#     """
#     conn = connect_to_db()
#     if conn is None:
#         raise RuntimeError("Database connection failed.")

#     query = """
#         SELECT title, author, publish_year, genre_consolidated, description
#         FROM book_titles;
#     """
#     books_df = pd.read_sql_query(query, conn)

#     conn.close()
#     return books_df
