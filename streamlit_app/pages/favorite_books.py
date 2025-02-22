import streamlit as st
from utils.data_utils import get_unique_books
from utils.profile_utils import save_favorite_books

def show_favorite_books():
    st.title("Favorite Books")

    # Get the list of books dynamically from data_utils
    default_books = get_unique_books()

    if "favorite_books" not in st.session_state:
        st.session_state.favorite_books = []

    # Multi-select for known + newly added books
    favorite_books = st.multiselect(
        "What are some of your other favorite books?",
        options=default_books + st.session_state.favorite_books,  # Combine preset books + user-added books
        default=st.session_state.favorite_books
    )

    st.session_state.favorite_books = favorite_books

    # Form to add a new favorite book
    with st.form("add_fav_book_form"):
        manual_favorite_book = st.text_input("Add another favorite book", value="")
        add_book_button = st.form_submit_button("Add Book")

    if add_book_button and manual_favorite_book.strip():
        if manual_favorite_book not in st.session_state.favorite_books:
            st.session_state.favorite_books.append(manual_favorite_book)
        st.rerun()

    # Navigation buttons
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back"):
            st.session_state.page = "recent_book"
            st.rerun()
    with col2:
        if st.button("Next →") and st.session_state.favorite_books:
            save_favorite_books(favorite_books)
            st.session_state.page = "reading_goals"
            st.rerun()

