# src/db_utils.py
import psycopg2 as ps
import pandas as pd
from typing import List
import logging

# Database connection parameters
DB_CONFIG = {
    "host": "booksdataclean.cu9jy7bp7ol8.us-east-1.rds.amazonaws.com",
    "dbname": "booksfull",
    "port": "5432",
    "username": "postgres",
    "password": "S3EW5y9MhZzBBYXlCjE6"
}

def connect_to_db(host_name=None, dbname=None, port=None, username=None, password=None):
    """
    Connect to the PostgreSQL database
    
    Args:
        host_name: Database host
        dbname: Database name
        port: Database port
        username: Database username
        password: Database password
        
    Returns:
        connection: PostgreSQL database connection
    """
    # Use parameters or default to config values
    host_name = host_name or DB_CONFIG["host"]
    dbname = dbname or DB_CONFIG["dbname"]
    port = port or DB_CONFIG["port"]
    username = username or DB_CONFIG["username"]
    password = password or DB_CONFIG["password"]
    
    try:
        conn = ps.connect(
            host=host_name,
            database=dbname,
            user=username,
            password=password,
            port=port
        )
        logging.info("Database connection established successfully")
        return conn
    except ps.OperationalError as e:
        logging.error(f"Error connecting to database: {str(e)}")
        raise e

def query_to_list(query, conn) -> List:
    """
    Execute a query and return results as a list
    
    Args:
        query: SQL query string
        conn: Database connection
        
    Returns:
        List of query results
    """
    try:
        temp_list = []
        temp_df = pd.read_sql_query(query, conn)
        for i in range(len(temp_df)):
            temp_list.append(temp_df.iloc[i, 0])
        return temp_list
    except Exception as e:
        logging.error(f"Error executing query: {str(e)}")
        raise e

def query_to_df(query, conn) -> pd.DataFrame:
    """
    Execute a query and return results as a DataFrame
    
    Args:
        query: SQL query string
        conn: Database connection
        
    Returns:
        DataFrame of query results
    """
    try:
        return pd.read_sql_query(query, conn)
    except Exception as e:
        logging.error(f"Error executing query: {str(e)}")
        raise e

def get_unique_genres() -> List[str]:
    """
    Get unique genres from the database using genre_consolidated
    
    Returns:
        List of unique genres, alphabetically sorted
    """
    conn = None
    cursor = None
    try:
        conn = connect_to_db()
        query = """
        SELECT DISTINCT genre_consolidated 
        FROM books_info 
        WHERE genre_consolidated IS NOT NULL 
        ORDER BY genre_consolidated
        """
        genres = query_to_list(query, conn)
        return genres
    except Exception as e:
        logging.error(f"Error retrieving genres: {str(e)}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_unique_authors() -> List[str]:
    """
    Get unique authors from the database
    
    Returns:
        List of unique authors, alphabetically sorted
    """
    conn = None
    cursor = None
    try:
        conn = connect_to_db()
        query = """
        SELECT DISTINCT author 
        FROM books_info 
        WHERE author IS NOT NULL 
        and author NOT IN ('','1873-1954 Colette','5th Edition')
        and author NOT LIKE '%Publish%'
        ORDER BY author
        """
        authors = query_to_list(query, conn)
        return authors
    except Exception as e:
        logging.error(f"Error retrieving authors: {str(e)}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_unique_books() -> List[str]:
    """
    Get unique books with their authors from the database
    
    Returns:
        List of books in "Title - Author" format, alphabetically sorted by title
    """
    conn = None
    cursor = None
    try:
        conn = connect_to_db()
        query = """
        SELECT DISTINCT title, author 
        FROM books_info 
        ORDER BY title
        """
        df = query_to_df(query, conn)
        # Format as "Title - Author"
        books = [f"{row['title']} - {row['author']}" for _, row in df.iterrows()]
        return books
    except Exception as e:
        logging.error(f"Error retrieving books: {str(e)}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_genre_embeddings() -> pd.DataFrame:
    """
    Get genre embeddings from the database
    
    Returns:
        DataFrame with genre names and their 3D embeddings
    """
    conn = None
    cursor = None
    try:
        conn = connect_to_db()
        query = """
        SELECT genre_name, embedding_x, embedding_y, embedding_z 
        FROM genre_embeddings
        """
        genre_embeddings_df = query_to_df(query, conn)
        logging.info(f"Retrieved {len(genre_embeddings_df)} genre embeddings from database")
        return genre_embeddings_df
    except Exception as e:
        logging.error(f"Error retrieving genre embeddings: {str(e)}")
        return pd.DataFrame()  # Return empty DataFrame on error
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_book_covers_lookup() -> pd.DataFrame:
    """
    Get book cover information from the database
    
    Returns:
        DataFrame with book cover information (title, book_id, image_path, etc.)
    """
    conn = None
    cursor = None
    try:
        conn = connect_to_db()
        query = """
        SELECT title, book_id, preview_link, image_url, image_path, status
        FROM book_covers
        WHERE image_path IS NOT NULL
        """
        covers_df = query_to_df(query, conn)
        logging.info(f"Retrieved {len(covers_df)} book covers from database")
        return covers_df
    except Exception as e:
        logging.error(f"Error retrieving book covers: {str(e)}")
        return pd.DataFrame()  # Return empty DataFrame on error
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()