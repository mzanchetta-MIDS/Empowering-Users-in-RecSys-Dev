import psycopg2 as ps
import pandas as pd

# Database connection parameters - with the correct password
host_name = "booksdataclean.cu9jy7bp7ol8.us-east-1.rds.amazonaws.com"
dbname = 'booksfull'
port = '5432'
username = 'postgres'
password = 'S3EW5y9MhZzBBYXlCjE6'

def connect_to_db(host_name, dbname, port, username, password):
    try:
        conn = ps.connect(host=host_name, database=dbname, user=username, password=password, port=port)
    except ps.OperationalError as e:
        raise e
    else:
        print("Connected!")
        return conn

def test_connection():
    """Test database connection and pull some sample data"""
    try:
        print("Attempting to connect to the database...")
        
        # Connect to the database
        conn = connect_to_db(host_name, dbname, port, username, password)
        
        # Create a cursor
        cursor = conn.cursor()
        
        # Get list of tables
        print("\nGetting list of tables...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        print(f"Tables in the database: {[table[0] for table in tables]}")
        
        # Get basic info about books_titles table
        print("\nGetting books_titles structure...")
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'books_titles'
        """)
        columns = cursor.fetchall()
        print("books_titles columns:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]}")
        
        # Get basic info about books_info table
        print("\nGetting books_info structure...")
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'books_info'
        """)
        columns = cursor.fetchall()
        print("books_info columns:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]}")
        
        # Sample data: Get some genres
        print("\nSample genres (top 10):")
        cursor.execute("""
            SELECT DISTINCT category 
            FROM books_info 
            WHERE category IS NOT NULL 
            ORDER BY category 
            LIMIT 10
        """)
        genres = cursor.fetchall()
        for genre in genres:
            print(f"  - {genre[0]}")
        
        # Sample data: Get some authors
        print("\nSample authors (top 10):")
        cursor.execute("""
            SELECT DISTINCT authors 
            FROM books_titles 
            WHERE authors IS NOT NULL 
            ORDER BY authors 
            LIMIT 10
        """)
        authors = cursor.fetchall()
        for author in authors:
            print(f"  - {author[0]}")
        
        # Sample data: Get some books
        print("\nSample books (top 5):")
        cursor.execute("""
            SELECT title, authors 
            FROM books_titles 
            WHERE title IS NOT NULL AND authors IS NOT NULL 
            ORDER BY title 
            LIMIT 5
        """)
        books = cursor.fetchall()
        for book in books:
            print(f"  - {book[0]} by {book[1]}")
        
        # Close the cursor and connection
        cursor.close()
        conn.close()
        print("\nConnection closed successfully.")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Check if your IP is allowed in the RDS security group")
        print("2. Ensure the RDS instance is publicly accessible")
        print("3. Verify your local network doesn't block port 5432")
        print("4. Double-check the connection parameters")

if __name__ == "__main__":
    test_connection()