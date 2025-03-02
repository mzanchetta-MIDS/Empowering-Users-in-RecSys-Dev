import streamlit as st

def show_welcome():
    st.title("Welcome to BookWise!")
    st.write("""
    Let's help you discover your next great read. In just a few minutes,
    we can learn about your reading preferences to provide personalized
    recommendations tailored just for you.

    We'll ask you a few quick questions about what you enjoy reading. Feel free
    to be as specific or general as you'd like—there are no wrong answers!
    """)
    
    # Add name field
    name = st.text_input("What's your name?", key="user_name", value=st.session_state.user_profile.get("name", ""))
    
    # Only enable the button if name is provided
    start_disabled = not name.strip()
    
    button_label = "Let's Get Started!"
    if start_disabled:
        button_label += " (Please enter your name first)"
    
    if st.button(button_label, disabled=start_disabled):
        # Save the name to the user profile
        st.session_state.user_profile["name"] = name
        st.write("DEBUG: The button was clicked! Name saved:", name)
        st.session_state.page = "genres"
        st.rerun()