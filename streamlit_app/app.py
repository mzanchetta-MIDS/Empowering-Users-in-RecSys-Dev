import streamlit as st
import os
import base64

# SESSION INIT
def initialize_session_state():
    if "profile_completed" not in st.session_state:
        st.session_state.profile_completed = False
    if "selected_tab" not in st.session_state:
        st.session_state.selected_tab = "Recommendations"
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = {}
    if "saved_for_later" not in st.session_state.user_profile:
        st.session_state.user_profile["saved_for_later"] = []
    if "ratings" not in st.session_state.user_profile:
        st.session_state.user_profile["ratings"] = {}
    if "not_interested" not in st.session_state.user_profile:
        st.session_state.user_profile["not_interested"] = []
    

initialize_session_state()

# PAGE CONFIG
st.set_page_config(
    page_title="Bookwise.ai",
    page_icon="assets/book_icon.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# LOAD CSS
def load_css():
    css_files = ["static/custom_styles.css", "assets/css/custom_styles.css"]
    for file_name in css_files:
        if os.path.exists(file_name):
            with open(file_name, "r") as f:
                css_text = f.read()
            st.markdown(f"<style>{css_text}</style>", unsafe_allow_html=True)
        else:
            st.warning(f"⚠️ Warning: CSS file {file_name} not found.")

load_css()

# HELPER: HEADER
def get_image_base64(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

def show_custom_header():
    image_path = os.path.join("assets", "book_icon.png")
    image_base64 = get_image_base64(image_path)
    st.markdown(f"""
        <div class="app-header">
            <img src="data:image/png;base64,{image_base64}" class="header-icon"/>
            <h2 style="color: #FFF;">bookwise.ai</h2>
        </div>
    """, unsafe_allow_html=True)

# TAB CALLBACKS
def switch_to_tab(tab_name):
    st.session_state.selected_tab = tab_name

# BOOK ACTION CALLBACKS
def save_book_for_later(book_title):
    
    # Find the book in recommendations
    book_to_save = None
    new_recommendations = []
    
    for book in st.session_state.recommendations_list:
        if book["title"] == book_title:
            book_to_save = book
        else:
            new_recommendations.append(book)
    
    if book_to_save:
        # Save to saved_for_later
        st.session_state.user_profile["saved_for_later"].append(book_to_save)
        # Update recommendations list
        st.session_state.recommendations_list = new_recommendations
        
from pages.welcome import show_welcome
from pages.genres import show_genres
from pages.authors import show_authors
from pages.favorite_books import show_favorite_books
from pages.additional_preferences import show_additional_preferences
from pages.completion import show_completion
from pages.profile import show_profile
from pages.saved_for_later import show_saved_for_later
from pages.recommendations import show_recommendations

from utils.profile_utils import load_profile, save_profile, initialize_user_profile


def main():
    
    # Process any pending actions
    if "pending_action" in st.session_state and st.session_state.pending_action:
        action = st.session_state.pending_action
        
        if action["type"] == "save":
            save_book_for_later(action["title"])
        
    initialize_user_profile()
    # Keep load_profile() commented out for local development:
    # load_profile()

    # STEP-BASED ONBOARDING
    if not st.session_state.profile_completed:
        if "page" not in st.session_state:
            st.session_state.page = "welcome"

        pages = {
            "welcome": show_welcome,
            "genres": show_genres,
            "authors": show_authors,
            "favorite_books": show_favorite_books,
            "additional_preferences": show_additional_preferences,
            "completion": show_completion
        }

        pages[st.session_state.page]()

    # TABBED INTERFACE (POST-ONBOARDING)
    else:
        show_custom_header()
        
        # Show personalized welcome message with user's name
        user_name = st.session_state.user_profile.get("name", "")
        if user_name:
            st.subheader(f"📚 Welcome Back, {user_name}!")
        else:
            st.subheader("📚 Welcome Back!")

        # Create tab buttons instead of using st.tabs()
        tab_titles = ["Recommendations", "Profile", "Library"]
        cols = st.columns(len(tab_titles))
        
        for i, title in enumerate(tab_titles):
            with cols[i]:
                if st.button(
                    title, 
                    key=f"tab_{title}",
                    use_container_width=True,
                    type="primary" if st.session_state.selected_tab == title else "secondary"
                ):
                    st.session_state.selected_tab = title
                    st.rerun()
        
        # Show the selected content based on tab
        selected_tab = st.session_state.selected_tab
        
        if selected_tab == "Recommendations":
            show_recommendations()
        elif selected_tab == "Profile":
            show_profile()
        elif selected_tab == "Library":
            show_saved_for_later()

if __name__ == "__main__":
    main()