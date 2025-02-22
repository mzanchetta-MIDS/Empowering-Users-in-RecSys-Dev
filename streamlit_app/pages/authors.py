import streamlit as st
from utils.data_utils import get_unique_authors
from utils.profile_utils import save_authors

def show_authors():
    st.title("Favorite Authors")

    default_authors = get_unique_authors()
    current_authors = st.session_state.user_profile.get("authors", [])

    # --- FORM: multi-select + optional new author ---
    with st.form("authors_form", clear_on_submit=False):
        st.write("Select or add your favorite authors, then click 'Submit' to apply.")

        selected_authors = st.multiselect(
            "Who are some of your favorite authors?",
            options=default_authors + current_authors,
            default=current_authors
        )

        new_author = st.text_input("Add a new author (optional)")

        submitted = st.form_submit_button("Submit Authors")

    if submitted:
        # If user typed a new author, add it if not already in the list
        if new_author.strip() and new_author.strip() not in selected_authors:
            selected_authors.append(new_author.strip())

        # Save authors
        save_authors(selected_authors)
        st.rerun()

    # --- NAVIGATION ---
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back"):
            st.session_state.page = "genres"
            st.rerun()

    with col2:
        # Let them move on even if they picked 0 authors or only from the list
        if st.button("Next →"):
            st.session_state.page = "recent_book"
            st.rerun()
