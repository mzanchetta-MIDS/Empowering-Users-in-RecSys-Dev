import os
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch
import psycopg2 as ps
import pandas as pd

# LLM Params
MODEL_NAME = "meta-llama/Llama-3.1-8B-Instruct"

# SQL Params
DB_CONFIG = {
    "host": "booksdataclean.cu9jy7bp7ol8.us-east-1.rds.amazonaws.com",
    "dbname": "booksfull",
    "port": "5432",
    "user": "postgres",
    "password": "S3EW5y9MhZzBBYXlCjE6",
}

def load_model(model_name=MODEL_NAME):
    """
    Downloads and loads the model into memory
    """
    HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

    if not HUGGINGFACE_TOKEN:
        raise ValueError("HUGGINGFACE_TOKEN is not set. Please set it as an environment variable.")

    print(f"Loading model {model_name} into RAM...")

    tokenizer = AutoTokenizer.from_pretrained(model_name, token=HUGGINGFACE_TOKEN)
    tokenizer.pad_token = tokenizer.eos_token

    # Handle CPU vs GPU
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Only use quantization if on GPU
    quantization_config = None
    if device == "cuda":
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16
        )

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto" if device == "cuda" else None,
        quantization_config=quantization_config if device == "cuda" else None,
        token=HUGGINGFACE_TOKEN
    )

    model.to(device)  # Move model to CPU/GPU
    print(f"Model loaded into {device.upper()} successfully.")
    return tokenizer, model, device


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
