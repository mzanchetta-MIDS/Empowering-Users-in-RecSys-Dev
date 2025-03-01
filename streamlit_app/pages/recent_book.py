import streamlit as st

def show_recent_book():
    st.title("Recent Reading")

    if "recent_book" not in st.session_state:
        st.session_state.recent_book = ""
    if "why_captivating" not in st.session_state:
        st.session_state.why_captivating = ""

    # Text inputs for the last captivating book + reasons why
    recent_book = st.text_input(
        "What was the last book that really captivated you?",
        value=st.session_state.recent_book
    )
    st.session_state.recent_book = recent_book

    why_captivating = st.text_area(
        "What made it so captivating?",
        value=st.session_state.why_captivating
    )
    st.session_state.why_captivating = why_captivating

    # Navigation buttons
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back"):
            st.session_state.page = "authors"
            st.rerun()
    with col2:
        # Require a non-empty "last book"
        if st.button("Next →"):
            st.session_state.page = "favorite_books"
            st.rerun()