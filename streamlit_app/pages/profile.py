# pages/profile.py
import streamlit as st
import json

def show_profile():
    st.title("Your Reading Profile")
    
    if "user_profile" not in st.session_state:
        st.warning("Profile data not found. Please complete the onboarding process.")
        return
    
    profile = st.session_state.user_profile
    
    # Display profile in a formatted way
    st.subheader("📚 Reading Preferences")
    
    # Genres
    if profile.get("genres"):
        st.write("**Favorite Genres:**")
        for genre in profile.get("genres", []):
            st.write(f"- {genre}")
    
    # Authors
    if profile.get("authors"):
        st.write("**Favorite Authors:**")
        for author in profile.get("authors", []):
            st.write(f"- {author}")
    
    # Recent book
    if profile.get("recent_book"):
        st.write("**Recently Captivating Book:**")
        st.write(profile.get("recent_book"))
        
        if profile.get("why_captivating"):
            st.write("**What made it captivating:**")
            st.write(profile.get("why_captivating"))
    
    # Favorite books
    if profile.get("favorite_books"):
        st.write("**Favorite Books:**")
        for book in profile.get("favorite_books", []):
            st.write(f"- {book}")
    
    # Reading goals
    if profile.get("reading_goals"):
        st.write("**Reading Goals:**")
        for goal in profile.get("reading_goals", []):
            st.write(f"- {goal}")
    
    # Display raw JSON for debugging/verification
    with st.expander("View Raw Profile Data (JSON)"):
        st.json(profile)
    
    # Add an option to reset profile for testing
    if st.button("Reset Profile (for testing)"):
        # Clear profile and set profile_completed to False
        st.session_state.user_profile = {
            "genres": [],
            "other_genre": "",
            "authors": [],
            "favorite_books": [],
            "recent_book": "",
            "why_captivating": "",
            "reading_goals": [],
            "other_goals": ""
        }
        st.session_state.profile_completed = False
        st.rerun()