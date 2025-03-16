# sections/profile.py
import streamlit as st
import json
from utils.profile_utils import save_profile
from utils.data_utils import get_unique_genres, get_unique_authors, get_unique_books

def show_profile():
    st.subheader("Your Reading Profile")
    
    if "user_profile" not in st.session_state:
        st.warning("Profile data not found. Please complete the onboarding process.")
        return
    
    profile = st.session_state.user_profile
    
    # Initialize edit states if not present
    if "edit_genres" not in st.session_state:
        st.session_state.edit_genres = False
    if "edit_authors" not in st.session_state:
        st.session_state.edit_authors = False
    if "edit_books" not in st.session_state:
        st.session_state.edit_books = False
    if "edit_preferences" not in st.session_state:
        st.session_state.edit_preferences = False
    
    # Custom CSS to style the expanders
    st.markdown("""
    <style>
    .streamlit-expanderHeader {
        background-color: #9C897E !important;
        color: white !important;
        font-weight: 500 !important;
        border-radius: 5px !important;
        padding: 10px 15px !important;
    }
    
    .streamlit-expanderContent {
        background-color: #F5F2EB !important;
        border: 1px solid #E6E3DC !important;
        border-top: none !important;
        border-radius: 0 0 5px 5px !important;
        padding: 15px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Genres Section
    with st.expander("Favorite Genres"):
        if not st.session_state.edit_genres:
            if st.button("✏️ Edit", key="edit_genres_btn"):
                st.session_state.edit_genres = True
                st.rerun()
            
            # Display current genres
            if profile.get("genres"):
                for genre in profile.get("genres", []):
                    st.write(f"• {genre}")
            else:
                st.write("No genres selected.")
        else:
            # Show editable multiselect for genres
            all_genres = get_unique_genres()
            selected_genres = st.multiselect(
                "Select your favorite genres:",
                options=all_genres,
                default=profile.get("genres", [])
            )
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Cancel", key="cancel_genres"):
                    st.session_state.edit_genres = False
                    st.rerun()
            with col2:
                if st.button("Save", key="save_genres"):
                    profile["genres"] = selected_genres
                    save_profile()
                    st.session_state.edit_genres = False
                    st.rerun()
    
    # Authors Section
    with st.expander("Favorite Authors"):
        if not st.session_state.edit_authors:
            if st.button("✏️ Edit", key="edit_authors_btn"):
                st.session_state.edit_authors = True
                st.rerun()
            
            # Display current authors
            if profile.get("authors"):
                for author in profile.get("authors", []):
                    st.write(f"• {author}")
            else:
                st.write("No authors selected.")
        else:
            # Show editable multiselect for authors
            all_authors = get_unique_authors()
            selected_authors = st.multiselect(
                "Select your favorite authors:",
                options=all_authors,
                default=profile.get("authors", [])
            )
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Cancel", key="cancel_authors"):
                    st.session_state.edit_authors = False
                    st.rerun()
            with col2:
                if st.button("Save", key="save_authors"):
                    profile["authors"] = selected_authors
                    save_profile()
                    st.session_state.edit_authors = False
                    st.rerun()
    
    # Books Section
    with st.expander("Favorite Books"):
        if not st.session_state.edit_books:
            if st.button("✏️ Edit", key="edit_books_btn"):
                st.session_state.edit_books = True
                st.rerun()
            
            # Display current books
            if profile.get("favorite_books"):
                for book in profile.get("favorite_books", []):
                    st.write(f"• {book}")
            else:
                st.write("No favorite books selected.")
        else:
            # Show editable multiselect for books
            all_books = get_unique_books()
            selected_books = st.multiselect(
                "Select your favorite books:",
                options=all_books,
                default=profile.get("favorite_books", [])
            )
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Cancel", key="cancel_books"):
                    st.session_state.edit_books = False
                    st.rerun()
            with col2:
                if st.button("Save", key="save_books"):
                    profile["favorite_books"] = selected_books
                    save_profile()
                    st.session_state.edit_books = False
                    st.rerun()
    
    # Additional Preferences Section
    with st.expander("Reading Preferences"):
        if not st.session_state.edit_preferences:
            if st.button("✏️ Edit", key="edit_prefs_btn"):
                st.session_state.edit_preferences = True
                st.rerun()
            
            # Display current additional preferences
            if profile.get("additional_preferences"):
                st.write(profile.get("additional_preferences"))
            else:
                st.write("No additional preferences specified.")
        else:
            # Show editable text area for additional preferences
            additional_prefs = st.text_area(
                "Additional reading preferences:",
                value=profile.get("additional_preferences", ""),
                height=150
            )
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Cancel", key="cancel_prefs"):
                    st.session_state.edit_preferences = False
                    st.rerun()
            with col2:
                if st.button("Save", key="save_prefs"):
                    profile["additional_preferences"] = additional_prefs
                    save_profile()
                    st.session_state.edit_preferences = False
                    st.rerun()
    
    # Ratings Section
    with st.expander("Books You've Rated"):
        if profile.get("ratings") and len(profile.get("ratings")) > 0:
            for book_title, rating in profile.get("ratings").items():
                st.write(f"• {book_title}: {'★' * rating}")
        else:
            st.write("You haven't rated any books yet.")
    
    # Not Interested Section
    with st.expander("Books You're Not Interested In"):
        if profile.get("not_interested"):
            for book in profile.get("not_interested", []):
                st.write(f"• {book}")
        else:
            st.write("No books marked as 'not interested'.")
    
    # Display raw JSON for debugging/verification
    with st.expander("View Raw Profile Data (JSON)"):
        st.json(profile)
    
    # Add an option to reset profile for testing
    if st.button("Reset Profile (for testing)"):
        # Clear profile and set profile_completed to False
        st.session_state.user_profile = {
            "genres": [],
            "authors": [],
            "favorite_books": [],
            "additional_preferences": "",
            "ratings": {},
            "not_interested": []
        }
        st.session_state.profile_completed = False
        st.rerun()