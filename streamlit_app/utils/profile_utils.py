# utils/profile_utils.py
import streamlit as st
import json
import os
from utils.api_client import submit_user_profile


PROFILE_PATH = "user_profiles.json"  # We will change this to a DB/API later

def initialize_user_profile():
    """
    Ensure st.session_state.user_profile exists with the necessary keys.
    """
    if "profile_completed" not in st.session_state:
        st.session_state.profile_completed = False

    if "user_profile" not in st.session_state:
        st.session_state.user_profile = {
            "genres": [],
            "disliked_genres": [],
            "genre_preferences": {},  
            "authors": [],
            "favorite_books": []
        }

def save_genres(selected_genres, disliked_genres=""):
    """
    Saves the selected genres and disliked genres.
    Maintains any existing genre_preferences.
    """
    # Get current genre preferences
    current_preferences = st.session_state.user_profile.get("genre_preferences", {})
    
    # Update the genres list
    st.session_state.user_profile["genres"] = selected_genres
    st.session_state.user_profile["disliked_genres"] = disliked_genres
    
    # Clean up preferences for removed genres
    updated_preferences = {genre: pref for genre, pref in current_preferences.items() 
                          if genre in selected_genres}
    
    # Ensure all selected genres have a preference (default if not specified)
    for genre in selected_genres:
        if genre not in updated_preferences:
            updated_preferences[genre] = "default"
    
    # Save updated preferences
    st.session_state.user_profile["genre_preferences"] = updated_preferences
    
    # Persist profile changes
    save_profile()

def save_authors(selected_authors):
    """
    Saves the selected authors.
    """
    st.session_state.user_profile["authors"] = selected_authors
    save_profile()

def save_favorite_books(favorite_books):
    """
    Saves the user's list of favorite books.
    """
    st.session_state.user_profile["favorite_books"] = favorite_books
    save_profile()

def get_user_profile_json():
    """
    Returns the user's profile as a JSON string for logging or API calls.
    """
    return json.dumps(st.session_state.user_profile, indent=2)

def save_profile():
    """
    Saves the current user profile from session state to a JSON file
    and sends it to the API.
    """
    # Save locally
    with open(PROFILE_PATH, "w") as f:
        json.dump(st.session_state.user_profile, f, indent=2)
    
    # Send to API
    submit_user_profile(st.session_state.user_profile)

def load_profile():
    """
    Loads the user profile from a JSON file into session state.
    If no profile exists, initializes an empty profile.
    """
    if os.path.exists(PROFILE_PATH):
        with open(PROFILE_PATH, "r") as f:
            st.session_state.user_profile = json.load(f)
    else:
        initialize_user_profile()

def add_to_recommendation_history(book_info):
    """
    Adds a book to the user's recommendation history
    
    Args:
        book_info: Dict with at least "title" field
    """
    if "recommended_history" not in st.session_state.user_profile:
        st.session_state.user_profile["recommended_history"] = []
        
    # Add to history if not already present (simple string instead of object)
    book_title = book_info["title"]
    if book_title not in st.session_state.user_profile["recommended_history"]:
        st.session_state.user_profile["recommended_history"].append(book_title)
        
    # Save updated profile
    save_profile()