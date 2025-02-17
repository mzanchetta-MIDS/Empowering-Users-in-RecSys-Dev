import streamlit as st
import time
import os 
import base64

def get_image_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Image path 
image_path = os.path.join("assets", "book_icon.png")

# App title 
APP_TITLE = "bookwise.ai"  

# Encode image
image_base64 = get_image_base64(image_path)

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="assets/book_icon.png",  # Icon path
    layout="wide",                     # App full-width
    initial_sidebar_state="collapsed"  # Sidebar hidden/collapsed
)

st.markdown(
    f"""
    <style>
        /* Hide the sidebar completely */
        [data-testid="stSidebar"] {{
            display: none;
        }}

        /* Make a top banner (full-width) for your header */
        .app-header {{
            display: flex;
            align-items: center;
            padding: 15px;
            background-color: #2C2C2C;
            width: 100%;
            padding-left: 20px;
            padding-right: 20px;
        }}
        .header-icon {{
            width: 70px;
            height: 70px;
            margin-right: 15px;
        }}

        /* Increase font size of question labels */
        div.stTextInput label, div.stMultiSelect label, div.stTextArea label {{
            font-size: 18px !important;
            font-weight: 500;
        }}

        /* Make user inputs (text fields, dropdowns, and multi-selects) larger */
        div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="tag"] {{
            font-size: 16px !important;
        }}
    </style>
    <div class="app-header">
        <img src="data:image/png;base64,{image_base64}" class="header-icon"/>
        <h2 style="color: #FFF;">{APP_TITLE}</h2>  <!-- Uses variable instead of hardcoded text -->
    </div>
    """,
    unsafe_allow_html=True
)


def initialize_progress_bar():
    total_steps = 6
    current_step = {
        'welcome': 0,
        'genres': 1,
        'authors': 2,
        'recent_book': 3,
        'favorite_books': 4,
        'reading_goals': 5,
        'completion': 6,
        'recommendations': 6
    }
    return current_step[st.session_state.page], total_steps

def show_welcome():
    st.title("Book Recommendations. Explained. Customized. Transparent.")
    st.write("""
    Welcome! Let's help you discover your next great read. In just a few minutes, 
    we can learn about your reading preferences to provide personalized book 
    recommendations tailored just for you.

    We'll ask you a few quick questions about what you enjoy reading. Feel free 
    to be as specific or general as you'd like - there are no wrong answers! 
    You can select from our suggestions or add your own choices.
    """)

    if st.button("Let's Get Started!"):
        st.session_state.page = 'genres'
        st.rerun()  

def show_genres():
    st.title("Favorite Genres")
    st.write("Choose the book genres you enjoy reading.")

    # Initialize session state if not already set
    if "selected_genres" not in st.session_state:
        st.session_state.selected_genres = []

    # Multi-select for genre selection
    selected_genres = st.multiselect(
        "Select your favorite genres:",
        ["Fiction", "Non-Fiction", "Mystery", "Fantasy", "Science Fiction", "Romance", "History"],
        default=st.session_state.selected_genres  # Pre-fill with saved selections
    )

    # Store selection in session state
    st.session_state.selected_genres = selected_genres

    # Columns for back/next buttons
    col1, col2 = st.columns([1, 5])

    with col1:
        if st.button("← Back"):
            st.session_state.page = 'welcome'
            st.rerun()

    with col2:
        if st.button("Next →") and st.session_state.selected_genres:
            st.session_state.page = 'authors'
            st.rerun()


def show_authors():
    st.title("Favorite Authors")

    # Sample authors (In real app, fetched from a database)
    sample_authors = ["J.K. Rowling", "Stephen King", "Jane Austen"]

    # Ensure session state variables exist
    if "selected_authors" not in st.session_state:
        st.session_state.selected_authors = []

    # MULTI-SELECT for existing & newly added authors
    selected_authors = st.multiselect(
        "Who are some of your favorite authors?",
        options=sample_authors + st.session_state.selected_authors,  # Combine known + custom
        default=st.session_state.selected_authors
    )

    # Update session state if user checks/unchecks authors
    st.session_state.selected_authors = selected_authors

    # -- FORM to handle "Add another author" --
    # When you press Enter or click 'Add Author,' only this form is submitted
    with st.form("add_author_form"):
        new_author = st.text_input("Add another author (Press Enter to apply)", value="")
        # This button triggers form submission
        add_author_button = st.form_submit_button("Add Author")

    # If the form is submitted with a non-empty author
    if add_author_button and new_author.strip():
        # Append to selected_authors if not already in the list
        if new_author not in st.session_state.selected_authors:
            st.session_state.selected_authors.append(new_author)
        # Rerun so the updated list shows immediately in multiselect
        st.rerun()

    col1, col2 = st.columns([1, 5])

    with col1:
        if st.button("← Back"):
            st.session_state.page = 'genres'
            st.rerun()

    with col2:
        # Only allow forward navigation if authors are selected
        if st.button("Next →") and st.session_state.selected_authors:
            st.session_state.page = 'recent_book'
            st.rerun()

def show_recent_book():
    st.title("Recent Reading")

    # Initialize session state if not already set
    if "recent_book" not in st.session_state:
        st.session_state.recent_book = ""

    if "why_captivating" not in st.session_state:
        st.session_state.why_captivating = ""

    # Text input for the recent book (pre-filled with session state)
    recent_book = st.text_input(
        "What was the last book that really captivated you?",
        value=st.session_state.recent_book
    )

    # Text area for why it was captivating (pre-filled with session state)
    why_captivating = st.text_area(
        "What made it so captivating?",
        value=st.session_state.why_captivating
    )

    # Update session state with latest inputs
    st.session_state.recent_book = recent_book
    st.session_state.why_captivating = why_captivating

    # Create columns for back/next buttons
    col1, col2 = st.columns([1, 5])

    with col1:
        if st.button("← Back"):
            st.session_state.page = 'authors'
            st.rerun()  

    with col2:
        if st.button("Next →") and st.session_state.recent_book.strip():
            st.session_state.page = 'favorite_books'
            st.rerun()


def show_favorite_books():
    st.title("Favorite Books")

    # Initialize session state if not already set
    if "favorite_books" not in st.session_state:
        st.session_state.favorite_books = []

    if "manual_favorite_book" not in st.session_state:
        st.session_state.manual_favorite_book = ""

    # Multi-select for favorite books (pre-filled with session state)
    favorite_books = st.multiselect(
        "What are some of your other favorite books?",
        options=["Sample Book 1", "Sample Book 2"],  # Replace with real data
        default=st.session_state.favorite_books
    )

    # Text input for manually adding a book
    manual_favorite_book = st.text_input(
        "Add another favorite book",
        value=st.session_state.manual_favorite_book
    )

    # Update session state with latest selections
    st.session_state.favorite_books = favorite_books
    st.session_state.manual_favorite_book = manual_favorite_book

    # Create columns for back/next buttons
    col1, col2 = st.columns([1, 5])

    with col1:
        if st.button("← Back"):
            st.session_state.page = 'recent_book'
            st.rerun()  

    with col2:
        if st.button("Next →") and (st.session_state.favorite_books or st.session_state.manual_favorite_book.strip()):
            st.session_state.page = 'reading_goals'
            st.rerun()


def show_reading_goals():
    st.title("Reading Goals")

    goals = [
        "Older classics",
        "The latest best-sellers",
        "Award-winning books",
        "New genres I haven't explored",
        "Books similar to my favorites",
        "Less-reviewed gems",
        "Highly-rated selections",
        "Quick reads",
        "Long, immersive reads"
    ]

    # Initialize session state if not already set
    if "reading_goals" not in st.session_state:
        st.session_state.reading_goals = []

    if "other_goals" not in st.session_state:
        st.session_state.other_goals = ""

    # Multi-select for reading goals (pre-filled with session state)
    reading_goals = st.multiselect(
        "Are you trying to read more of any particular type of book?",
        options=goals,
        default=st.session_state.reading_goals
    )

    # Text area for other reading goals (pre-filled with session state)
    other_goals = st.text_area(
        "Any other reading goals? (optional)",
        value=st.session_state.other_goals
    )

    # Update session state with latest selections
    st.session_state.reading_goals = reading_goals
    st.session_state.other_goals = other_goals

    # Create columns for back/next buttons
    col1, col2 = st.columns([1, 5])

    with col1:
        if st.button("← Back"):
            st.session_state.page = 'favorite_books'
            st.rerun()  

    with col2:
        if st.button("Next →") and (st.session_state.reading_goals or st.session_state.other_goals.strip()):
            st.session_state.page = 'completion'
            st.rerun()


def show_completion():
    st.success("""
    Thanks for telling us about your reading preferences! We're using your responses 
    to craft personalized book recommendations tailored just for you.
    """)
    
    # Simple loading animation
    with st.spinner('Preparing your personalized recommendations...'):
        time.sleep(3)  # Simulate processing
    
    st.balloons()

    # Create columns for back/next buttons
    col1, col2 = st.columns([1, 5])

    with col1:
        if st.button("← Back"):
            st.session_state.page = 'reading_goals'
            st.rerun()  

    with col2:
        if st.button("Next →"):
            st.session_state.page = 'recommendations'
            st.rerun()  

def show_recommendations():
    st.title("Your Personalized Recommendations")
    # Here you would integrate with your recommendation engine
    st.write("Recommendations based on your profile:")
    # Placeholder recommendations
    st.write("1. Book A - Because you enjoyed similar authors")
    st.write("2. Book B - Matches your interest in new genres")

def main():
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = 'welcome'
    
    # Page routing
    pages = {
        'welcome': show_welcome,
        'genres': show_genres,
        'authors': show_authors,
        'recent_book': show_recent_book,
        'favorite_books': show_favorite_books,
        'reading_goals': show_reading_goals,
        'completion': show_completion,
        'recommendations': show_recommendations
    }
    
    # Display current page
    pages[st.session_state.page]()
    
    # Debug info (remove in production)
    st.sidebar.write("Current page:", st.session_state.page)

if __name__ == "__main__":
    main()