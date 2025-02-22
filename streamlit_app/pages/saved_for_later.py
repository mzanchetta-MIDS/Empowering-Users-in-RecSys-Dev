# pages/saved_for_later.py
import streamlit as st

def show_saved_for_later():
    st.subheader("Saved for Later")

    saved_books = st.session_state.user_profile.get("saved_for_later", [])

    if not saved_books:
        st.info("You haven't saved any books yet!")
        return

    # Show each saved book as a “card”
    for idx, book in enumerate(saved_books):
        st.markdown(f"""
        <div style="background-color:#2C2C2C; 
                    padding:15px; 
                    border-radius:10px;
                    margin-bottom:20px;">
            <h4>📖 {book['title']}</h4>
            <p><strong>Author:</strong> {book['author']}</p>
            <p><strong>Description:</strong> {book['description']}</p>
            <p><strong>Why this was recommended:</strong> {book['explanation']}</p>
        </div>
        """, unsafe_allow_html=True)

