# pages/genres.py
import streamlit as st
from utils.data_utils import get_unique_genres
from utils.profile_utils import save_genres

def show_genres():
    st.title("Select Your Favorite Genres")

    # Load unique genres (avoiding hard-coded values)
    default_genres = get_unique_genres()

    # Current selections
    current_genres = st.session_state.user_profile.get("genres", [])
    current_other_genre = st.session_state.user_profile.get("other_genre", "")

    # --- FORM: Select multiple genres + optionally add a new one ---
    with st.form("genres_form", clear_on_submit=False):
        st.write("Pick or add your favorite genres, then click 'Submit' to apply.")
        
        # Multi-select for known genres
        selected_genres = st.multiselect(
            "What genres do you enjoy reading?",
            options=default_genres + current_genres,  # combine known + user-added
            default=current_genres
        )

        # Text input for manually adding a new genre
        new_genre = st.text_input("Add a new genre (optional)", value="")

        submitted = st.form_submit_button("Submit Genres")

    # Only re-run & update after "Submit Genres" is clicked
    if submitted:
        # If user typed a new genre, add it if not already in the list
        if new_genre.strip() and new_genre not in selected_genres:
            selected_genres.append(new_genre.strip())

        # Save to session state
        save_genres(selected_genres, "")  # We won't use 'other_genre' now, or you can keep it if you prefer
        st.rerun()

    # --- NAVIGATION BUTTONS ---
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back"):
            st.session_state.page = "welcome"
            st.rerun()

    with col2:
        # You can proceed even with an empty selection if you want
        if st.button("Next →"):
            st.session_state.page = "authors"
            st.rerun()
