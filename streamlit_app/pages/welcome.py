import streamlit as st

def show_welcome():
    st.title("Book Recommendation System")
    st.write("""
    Welcome! Let's help you discover your next great read. In just a few minutes,
    we can learn about your reading preferences to provide personalized
    recommendations tailored just for you.

    We'll ask you a few quick questions about what you enjoy reading. Feel free
    to be as specific or general as you'd like—there are no wrong answers!
    """)

    if st.button("Let's Get Started!"):
        st.write("DEBUG: The button was clicked!")  # Debug line
        st.session_state.page = "genres"
        st.rerun()  

