# pages/authors.py
import streamlit as st
from utils.data_utils import get_unique_authors
from utils.profile_utils import save_authors

def show_authors():
    st.title("Favorite Authors")

    # Load unique authors (avoiding hard-coded values)
    default_authors = get_unique_authors()

    # Ensure existing selections persist
    current_authors = st.session_state.user_profile.get("authors", [])

    # MULTI-SELECT for known authors
    selected_authors = st.multiselect(
        "Who are some of your favorite authors?",
        options=default_authors + current_authors,  # Combine known authors + any previously added ones
        default=current_authors
    )

    # -- FORM to handle "Add another author" --
    with st.form("add_author_form"):
        new_author = st.text_input("Add another author (Press Enter to apply)", value="")
        add_author_button = st.form_submit_button("Add Author")

    # If the form is submitted with a valid author
    if add_author_button and new_author.strip():
        if new_author not in selected_authors:
            selected_authors.append(new_author)
        st.session_state.user_profile["authors"] = selected_authors
        st.rerun()  

    # Save to profile storage
    save_authors(selected_authors)

    # -- NAVIGATION BUTTONS --
    col1, col2 = st.columns([1, 5])

    with col1:
        if st.button("← Back"):
            st.session_state.page = 'genres'
            st.rerun()

    with col2:
        if st.button("Next →") and selected_authors:
            st.session_state.page = 'recent_book'
            st.rerun()
