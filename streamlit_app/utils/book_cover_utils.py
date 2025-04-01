import streamlit as st
import pandas as pd
import logging
from utils.api_client import get_book_covers

# Base URL for S3 bucket
S3_BASE_URL = "https://w210recsys.s3.us-east-1.amazonaws.com/book_clean/"

# Default image to use when a match isn't found
DEFAULT_COVER = "book_covers/1_000_Questions_of_Who_You_Are_and_Your_View_on_Life.jpg"

@st.cache_data(ttl=3600, show_spinner=False)
def get_cover_lookup_table():
    """
    Get the book covers lookup table via the API with caching
    """
    covers = get_book_covers()
    if not covers:
        logging.warning("No book covers found via API")
        return pd.DataFrame()
    return pd.DataFrame(covers)

# def get_cover_image_url(book_title):
#     """
#     Look up a book cover image URL by title using exact matching
    
#     Args:
#         book_title: The title of the book
        
#     Returns:
#         URL to the book cover image, or the default cover if not found
#     """
#     # Get the lookup table
#     covers_df = get_cover_lookup_table()
    
#     print(f"DEBUG: Looking for cover for '{book_title}'")
    
#     if covers_df.empty:
#         print("DEBUG: Covers dataframe is empty!")
#         return f"{S3_BASE_URL}{DEFAULT_COVER}"
    
#     # Print a few titles from the database for comparison
#     print(f"DEBUG: First few titles in database: {covers_df['title'].head(3).tolist()}")
    
#     # Use exact matching
#     match = covers_df[covers_df['title'] == book_title]
#     print(f"DEBUG: Found {len(match)} matches for title")
    
#     if not match.empty:
#         image_path = match.iloc[0]['image_path']
#         full_url = f"{S3_BASE_URL}{image_path}" if image_path else f"{S3_BASE_URL}{DEFAULT_COVER}"
#         print(f"DEBUG: Using image URL: {full_url}")
#         return full_url
    
#     # Try with substring match as a fallback
#     print("DEBUG: No exact match found, trying substring match")
#     for idx, row in covers_df.iterrows():
#         db_title = row['title']
#         if book_title in db_title or db_title in book_title:
#             image_path = row['image_path']
#             full_url = f"{S3_BASE_URL}{image_path}" if image_path else f"{S3_BASE_URL}{DEFAULT_COVER}"
#             print(f"DEBUG: Found substring match: '{db_title}' -> {full_url}")
#             return full_url
        
#         # Only check the first 1000 rows for performance
#         if idx >= 1000:
#             break
    
#     # No match found, return default cover
#     print(f"DEBUG: No match found for '{book_title}', using default cover")
#     return f"{S3_BASE_URL}{DEFAULT_COVER}"

def get_cover_image_url(book_title):
    """
    Look up a book cover image URL by title using exact case-sensitive matching
    
    Args:
        book_title: The title of the book
        
    Returns:
        URL to the book cover image, or the default cover if not found
    """
    # Get the lookup table
    covers_df = get_cover_lookup_table()
    
    print(f"DEBUG: Looking for cover for '{book_title}'")
    
    if covers_df.empty:
        print("DEBUG: Covers dataframe is empty!")
        return f"{S3_BASE_URL}{DEFAULT_COVER}"
    
    # Use exact case-sensitive matching
    match = covers_df[covers_df['title'] == book_title]
    print(f"DEBUG: Found {len(match)} exact matches for title")
    
    if not match.empty:
        image_path = match.iloc[0]['image_path']
        full_url = f"{S3_BASE_URL}{image_path}" if image_path else f"{S3_BASE_URL}{DEFAULT_COVER}"
        print(f"DEBUG: Using image URL: {full_url}")
        return full_url
    
    # No match found, return default cover
    print(f"DEBUG: No exact match found for '{book_title}', using default cover")
    return f"{S3_BASE_URL}{DEFAULT_COVER}"

def test_image_display():
    """
    Return a test image URL to verify S3 accessibility
    """
    return "https://w210recsys.s3.us-east-1.amazonaws.com/book_clean/book_covers/To_Kill_a_Mockingbird.jpg"