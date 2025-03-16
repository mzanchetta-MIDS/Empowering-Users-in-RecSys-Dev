# pages/profile.py
import streamlit as st
import json

def show_profile():
    st.subheader("Your Reading Profile")
    
    if "user_profile" not in st.session_state:
        st.warning("Profile data not found. Please complete the onboarding process.")
        return
    
    profile = st.session_state.user_profile
    
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
    
    # Favorite books
    if profile.get("favorite_books"):
        st.write("**Favorite Books:**")
        for book in profile.get("favorite_books", []):
            st.write(f"- {book}")
    
    # Additional preferences
    if profile.get("additional_preferences"):
        st.write("**Additional Reading Preferences:**")
        st.write(profile.get("additional_preferences"))

    # Books with Ratings
    if profile.get("ratings") and len(profile.get("ratings")) > 0:
        st.write("**Books You've Rated:**")
        for book_title, rating in profile.get("ratings").items():
            st.write(f"- {book_title}: {'★' * rating}")
        
    # Not Interested Books
    if profile.get("not_interested"):
        st.write("**Books You're Not Interested In:**")
        for book in profile.get("not_interested", []):
            st.write(f"- {book}")
    
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
            "additional_preferences": "",
            "ratings": {},
            "not_interested": []
        }
        st.session_state.profile_completed = False
        st.rerun()