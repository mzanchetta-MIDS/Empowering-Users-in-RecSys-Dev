import streamlit as st
import os
import base64

# ✅ Ensure session state is initialized early
def initialize_session_state():
    if "profile_completed" not in st.session_state:
        st.session_state.profile_completed = False  # User hasn't finished onboarding
    if "selected_tab" not in st.session_state:
        st.session_state.selected_tab = "Recommendations"  # Default landing tab

# ✅ Initialize session state at the start
initialize_session_state()

st.set_page_config(
    page_title="Bookwise.ai",
    page_icon="assets/book_icon.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ✅ Load CSS
def load_css():
    """Load and inject custom CSS for styling."""
    css_files = ["static/custom_styles.css", "assets/css/custom_styles.css"]
    for file_name in css_files:
        if os.path.exists(file_name):
            with open(file_name, "r") as f:
                css_text = f.read()
            st.markdown(f"<style>{css_text}</style>", unsafe_allow_html=True)
        else:
            st.warning(f"⚠️ Warning: CSS file {file_name} not found.")

load_css()

# ✅ Helper functions for UI
def get_image_base64(image_path: str) -> str:
    """Load an image file and return it as a Base64-encoded string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

def show_custom_header():
    """Display a custom header with your icon and app title."""
    image_path = os.path.join("assets", "book_icon.png")
    image_base64 = get_image_base64(image_path)
    st.markdown(f"""
        <div class="app-header">
            <img src="data:image/png;base64,{image_base64}" class="header-icon"/>
            <h2 style="color: #FFF;">bookwise.ai</h2>
        </div>
    """, unsafe_allow_html=True)

# ✅ Import pages
from pages.welcome import show_welcome
from pages.genres import show_genres
from pages.authors import show_authors
from pages.recent_book import show_recent_book
from pages.favorite_books import show_favorite_books
from pages.reading_goals import show_reading_goals
from pages.completion import show_completion
from pages.profile import show_profile
from pages.saved_for_later import show_saved_for_later
from pages.recommendations import show_recommendations

# ✅ Import utilities
from utils.profile_utils import load_profile, save_profile, initialize_user_profile

def main():

    # ✅ Ensure session state variables exist
    initialize_user_profile()
    #load_profile()

    # ✅ Step-by-step onboarding if profile isn't completed
    if not st.session_state.profile_completed:
        if "page" not in st.session_state:
            st.session_state.page = "welcome"

        pages = {
            "welcome": show_welcome,
            "genres": show_genres,
            "authors": show_authors,
            "recent_book": show_recent_book,
            "favorite_books": show_favorite_books,
            "reading_goals": show_reading_goals,
            "completion": show_completion
        }

        pages[st.session_state.page]()  # Load the correct page

    else:
        # ✅ Show navigation tabs once profile is completed
        show_custom_header()
        st.subheader("📚 Welcome Back!")

        tab_titles = ["Recommendations", "Profile", "Saved for Later"]
        selected_tab = st.session_state.selected_tab

        # ✅ Tabs for navigation
        tabs = st.tabs(tab_titles)

        # ✅ Ensure correct tab loads
        with tabs[tab_titles.index(selected_tab)]:
            if selected_tab == "Recommendations":
                show_recommendations()
            elif selected_tab == "Profile":
                show_profile()
            elif selected_tab == "Saved for Later":
                show_saved_for_later()

        # ✅ Update session state when tabs change
        for idx, title in enumerate(tab_titles):
            if tabs[idx]:
                st.session_state.selected_tab = title

if __name__ == "__main__":
    main()