# pages/genres.py
import streamlit as st
from utils.data_utils import get_unique_genres
from utils.profile_utils import save_genres

def show_genres():
    st.write("DEBUG: We are in show_genres()!")
    st.title("Select Your Favorite Genres")

    # We load unique genres from data_utils 
    default_genres = get_unique_genres()

    # Retrieve current session values, if exist
    current_genres = st.session_state.user_profile.get("genres", [])
    current_other_genre = st.session_state.user_profile.get("other_genre", "")

    # Multi-select
    selected_genres = st.multiselect(
        "Choose the book genres you enjoy reading:",
        default_genres,
        default=current_genres
    )

    # "Other" genre text input
    other_genre = st.text_input("Other genre (optional):", value=current_other_genre)

    # Navigation
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back"):
            st.session_state.page = "welcome"
            st.rerun()

    with col2:
        if st.button("Next →"):
            save_genres(selected_genres, other_genre)
            
            # Only proceed if they selected at least something
            if selected_genres or other_genre.strip():
                st.session_state.page = "authors"
                st.rerun()
