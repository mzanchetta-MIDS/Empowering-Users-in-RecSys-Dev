# utils/data_utils.py

import streamlit as st
from utils.api_client import get_genres, get_authors, get_books, get_recommendations 
import logging
import requests

logger = logging.getLogger(__name__)

# @st.cache_data(ttl=3600, show_spinner=False)
# def get_unique_books():
#     """
#     Get all unique books from the API.
#     Falls back to hardcoded values if API call fails.
#     """
#     books = get_books()
#     if not books:
#         # Fallback to hardcoded books if API call fails
#         return [
#             "To Kill a Mockingbird - Harper Lee",
#             "1984 - George Orwell",
#             "Pride and Prejudice - Jane Austen",
#             "The Great Gatsby - F. Scott Fitzgerald",
#             "Moby Dick - Herman Melville"
#         ]
#     return books

@st.cache_data(ttl=3600, show_spinner=False)
def get_unique_books():
    """
    Get all unique books from the API.
    Falls back to hardcoded values if API call fails.
    Also updates the session state with book metadata if available.
    """
    books = get_books()

    if books and isinstance(books, dict):
        book_list = books.get("books", [])
        metadata_list = books.get("metadata", [])

        # Ensure metadata cache is initialized
        if "book_metadata" not in st.session_state:
            st.session_state.book_metadata = {}

        for book in metadata_list:
            # Standardized key format
            cache_key = f"{book['title']} - {book['author']}"

            st.session_state.book_metadata[cache_key] = {
                "title": book["title"],
                "author": book["author"],
                "genre": book.get("genre", "Unknown Genre")
            }

        return book_list

    # Fallback if API call fails or structure is unexpected
    return [
        "To Kill a Mockingbird - Harper Lee",
        "1984 - George Orwell",
        "Pride and Prejudice - Jane Austen",
        "The Great Gatsby - F. Scott Fitzgerald",
        "Moby Dick - Herman Melville"
    ]

    

@st.cache_data(ttl=3600, show_spinner=False)
def get_unique_genres():
    """
    Get all unique genres from the API.
    Falls back to hardcoded values if API call fails.
    """
    genres = get_genres()
    if not genres:
        # Fallback to hardcoded genres if API call fails
        return [
            "Fiction", "Non-Fiction", "Mystery", "Fantasy",
            "Science Fiction", "Romance", "History"
        ]
    return genres

@st.cache_data(ttl=3600, show_spinner=False)
def get_unique_authors():
    """
    Get all unique authors from the API.
    Falls back to hardcoded values if API call fails.
    """
    authors = get_authors()
    if not authors:
        # Fallback to hardcoded authors if API call fails
        return [
            "J.K. Rowling", "Stephen King", "Jane Austen",
            "Agatha Christie", "Neil Gaiman", "George R.R. Martin"
        ]
    return authors

@st.cache_data(ttl=3600, show_spinner=False)
def get_sample_recommendations():
    """
    Get recommendations from the API based on user profile.
    Falls back to hardcoded values if API call fails.
    """
    recommendations = get_recommendations()
    if not recommendations:
        # Fallback to hardcoded recommendations if API call fails
        return [
            {
                "title": "The Haunted Lighthouse",
                "author": "Stephen King",
                "description": (
                    "A chilling tale of an abandoned lighthouse haunted by past tragedies, "
                    "perfect for lovers of suspense and horror."
                ),
                "explanation": (
                    "Recommended because you enjoyed horror with strong atmospheric tension."
                ),
            },
            {
                "title": "Pride and Prejudice",
                "author": "Jane Austen",
                "description": (
                    "The story follows the main character Elizabeth Bennet as she deals with issues "
                    "of manners, upbringing, morality, education, and marriage."
                ),
                "explanation": (
                    "Based on your interest in classic literature and romantic themes."
                ),
            },
            {
                "title": "The Fellowship of the Ring",
                "author": "J.R.R. Tolkien",
                "description": (
                    "The first volume in the epic adventure of Frodo Baggins and the Fellowship "
                    "on their quest to destroy the One Ring."
                ),
                "explanation": (
                    "You indicated an interest in fantasy worlds with rich storytelling."
                ),
            }
        ]
    return recommendations


