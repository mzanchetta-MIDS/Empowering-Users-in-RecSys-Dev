import streamlit as st
import time
from utils.profile_utils import save_profile

def show_completion():
    st.success("""
    Thanks for telling us about your reading preferences! We're using your responses 
    to craft personalized book recommendations tailored just for you.
    """)

    # Simple loading animation
    with st.spinner('Preparing your personalized recommendations...'):
        save_profile()
        time.sleep(1)

    st.balloons()

    st.write("Click below to continue to your personalized interface!")

    if st.button("Enter Bookwise.ai!"):
        # Mark the profile as completed
        st.session_state.profile_completed = True
        # Force the active tab to be "Recommendations"
        st.session_state.selected_tab = "Recommendations"

        st.rerun()
