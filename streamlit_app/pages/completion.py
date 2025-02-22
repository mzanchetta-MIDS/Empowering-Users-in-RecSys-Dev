# pages/completion.py
import streamlit as st
import time

def show_completion():
    st.success("""
    Thanks for telling us about your reading preferences! We're using your responses 
    to craft personalized book recommendations tailored just for you.
    """)

    # Simple loading animation
    with st.spinner('Preparing your personalized recommendations...'):
        time.sleep(1)

    st.balloons()

    st.write("Click below to continue to your personalized interface!")

    # Force default tab to be "Recommendations"
    st.session_state.default_tab = "Recommendations"


    if st.button("Enter Bookwise.ai!"):
        # Mark the profile as completed
        st.session_state.profile_completed = True
        st.rerun()
