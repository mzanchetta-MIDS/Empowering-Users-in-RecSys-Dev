import streamlit as st
from utils.data_utils import get_unique_genres
from utils.profile_utils import save_genres

def show_genres():
    st.title("Select Your Favorite Genres")

    default_genres = get_unique_genres()
    current_genres = st.session_state.user_profile.get("genres", [])

    with st.form("genres_form", clear_on_submit=False):
        st.write("Pick your favorite genres, then click a button to proceed.")

        # Multi-select with no typed input
        selected_genres = st.multiselect(
            "Which genres do you enjoy reading?",
            options=default_genres,
            default=current_genres
        )

        # Two big form-submit buttons
        col1, col2 = st.columns([1,1])
        with col1:
            back_clicked = st.form_submit_button("← Back")
        with col2:
            next_clicked = st.form_submit_button("Next →")

    # If the user clicked "← Back"
    if back_clicked:
        save_genres(selected_genres, "")
        st.session_state.page = "welcome"
        st.rerun()

    # If the user clicked "Next →"
    if next_clicked:
        save_genres(selected_genres, "")
        st.session_state.page = "authors"
        st.rerun()
