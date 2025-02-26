import streamlit as st
from utils.data_utils import get_unique_books
from utils.profile_utils import save_favorite_books

def show_favorite_books():
    st.title("Favorite Books")

    default_books = get_unique_books()
    current_books = st.session_state.user_profile.get("favorite_books", [])

    # --- FORM: multi-select + optional typed book ---
    with st.form("favorite_books_form", clear_on_submit=False):
        st.write("Select or add your favorite books, then click 'Submit' or proceed with 'Next →'.")

        selected_books = st.multiselect(
            "What are some of your favorite books?",
            options=default_books + current_books,
            default=current_books
        )

        new_book = st.text_input("Add another favorite book (optional)")

        # If the user clicks this, we store the results immediately
        submitted = st.form_submit_button("Submit Books")

    # 1) If the user clicked "Submit Books" inside the form
    if submitted:
        save_current_selection(selected_books, new_book)
        st.rerun()

    # --- NAVIGATION BUTTONS (OUTSIDE THE FORM) ---
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back"):
            # 2) Also store data if user clicked Back (in case they never clicked Submit)
            save_current_selection(selected_books, new_book)
            st.session_state.page = "recent_book"
            st.rerun()

    with col2:
        if st.button("Next →"):
            # 3) Also store data if user clicked Next → (again, if they skipped 'Submit')
            save_current_selection(selected_books, new_book)
            st.session_state.page = "reading_goals"
            st.rerun()


def save_current_selection(selected_books, new_book):
    """
    Helper function to unify how we store the user's selection.
    Called on form submit, Next →, or Back.
    """
    # If user typed a new book, append if not already in the list
    if new_book.strip() and new_book.strip() not in selected_books:
        selected_books.append(new_book.strip())

    # Now save to session state (or via a helper in profile_utils)
    save_favorite_books(selected_books)
    