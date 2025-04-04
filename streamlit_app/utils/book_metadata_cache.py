import streamlit as st
import logging

logger = logging.getLogger(__name__)



# def get_book_metadata(title):
#     """
#     Get metadata for a book by title from the session state cache.
#     Raises an error if the book isn't found in the metadata cache.
    
#     Args:
#         title: Book title or "Title - Author" string
        
#     Returns:
#         Dict with title, author, and genre
        
#     Raises:
#         KeyError: If the book isn't found in the metadata cache
#     """
#     # Check if metadata is already in session state with exact key
#     if title in st.session_state.book_metadata:
#         return st.session_state.book_metadata[title]
    
#     # Extract title if in "Title - Author" format
#     pure_title = title
#     if " - " in title:
#         pure_title = title.split(" - ", 1)[0].strip()
    
#     # Try to find the pure title in the metadata cache
#     if pure_title in st.session_state.book_metadata:
#         return st.session_state.book_metadata[pure_title]
    
#     # If we get here, the book wasn't found
#     raise KeyError(f"Book '{title}' not found in metadata cache. This book may not exist in the database.")

def get_book_metadata(title):
    if "book_metadata" not in st.session_state:
        st.session_state.book_metadata = {}

    if title in st.session_state.book_metadata:
        return st.session_state.book_metadata[title]

    raise KeyError(f"Book '{title}' not found in metadata cache.")


    
def update_book_metadata(title, metadata):
  """
  Update the book metadata cache with new information.
  """
  if not isinstance(metadata, dict):
      logger.error(f"Invalid metadata format for '{title}': {metadata}")
      return
  
  required_keys = ["title", "author", "genre"]
  if not all(k in metadata for k in required_keys):
      logger.error(f"Missing required keys in metadata for '{title}': {metadata}")
      # Add any missing keys with default values
      for key in required_keys:
          if key not in metadata:
              if key == "title":
                  metadata[key] = title
              else:
                  metadata[key] = f"Unknown {key.capitalize()}"
  
  # Update the cache
  st.session_state.book_metadata[title] = metadata

  