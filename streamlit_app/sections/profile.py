# sections/profile.py
import streamlit as st
import json
import numpy as np
import pandas as pd
import logging 
import streamlit.components.v1 as components
import tempfile
import json

from utils.profile_utils import save_profile
from utils.data_utils import get_unique_genres, get_unique_authors, get_unique_books, load_chord_viz_data, create_genre_chord_diagram
from streamlit_extras.stylable_container import stylable_container


def show_profile():
    st.markdown("<h1 style='font-size: 38px; margin-bottom: 20px;'>Your Reading Profile</h1>", unsafe_allow_html=True)
    
    if "user_profile" not in st.session_state:
        st.warning("Profile data not found. Please complete the onboarding process.")
        return
    
    profile = st.session_state.user_profile
    
    if "edit_genres" not in st.session_state:
        st.session_state.edit_genres = False
    if "edit_disliked_genres" not in st.session_state:
        st.session_state.edit_disliked_genres = False
    if "edit_authors" not in st.session_state:
        st.session_state.edit_authors = False
    if "edit_books" not in st.session_state:
        st.session_state.edit_books = False
    if "edit_preferences" not in st.session_state:
        st.session_state.edit_preferences = False
    
    # Font-awesome link and icon styles
    st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
    <style>
    .profile-icon {
        color: #4e7694 !important;
        font-size: 22px !important;
        margin-top: 8px !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        height: 32px !important;
    }
    /* Icon styling with more specific selectors */
    .book-icon i, .thumbs-down-icon i, .user-icon i, .bookmark-icon i, 
    .cog-icon i, .star-icon i, .ban-icon i, .code-icon i {
        color: #4e7694 !important;
        font-size: 24px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create two permanent columns for the entire page layout
    left_col, spacer_col, right_col = st.columns([0.6, 0.05, 1.5])

    # LEFT COLUMN: Preferences
    with left_col:
        st.markdown("### Preferences")
        st.markdown("""
        <div style="background-color: #e8f4f8; padding: 10px; border-left: 4px solid #4e7694; margin-bottom: 15px;">
            <p style="margin: 0;"><strong>💡 Tip:</strong> You can pause selections from your favorite genres to temporarily exclude them from your recommendations.</p>
        </div>
        """, unsafe_allow_html=True)
        st.write("Click each attribute below to view and edit your preferences.")
        
        # Favorite Genres Section with preference controls
        col1, col2 = st.columns([0.07, 0.93])

        with col1:
            st.markdown('<div class="icon-container bookmark-icon"><i class="fas fa-bookmark"></i></div>', unsafe_allow_html=True)

        with col2:
            with st.expander("Favorite Genres"):
                if not st.session_state.edit_genres:
                    if st.button("✏️ Edit or Pause Genres", key="edit_genres_btn"):
                        st.session_state.edit_genres = True
                        st.rerun()
                    
                    # Display current genres with preference level
                    if profile.get("genres"):
                        # Get genre preferences dictionary
                        genre_preferences = profile.get("genre_preferences", {})
                        
                        for genre in profile.get("genres", []):
                            # Get preference level with "keep" as fallback
                            status = genre_preferences.get(genre, "keep")
                            
                            # Format the display text based on status
                            if status == "paused":
                                status_text = "(Paused)"
                            else:
                                status_text = ""  
                            
                            # Display the genre with its status
                            st.write(f"• {genre} {status_text}")
                    else:
                        st.write("No genres selected.")
                else:
                    # Editable multiselect for genres
                    all_genres = get_unique_genres()
                    selected_genres = st.multiselect(
                        "Select your favorite genres:",
                        options=all_genres,
                        default=profile.get("genres", [])
                    )
                    
                    st.write("For each genre, you can choose to include it in your recommendations or pause it temporarily:")
                    
                    # Initialize or get existing genre preferences
                    genre_preferences = profile.get("genre_preferences", {})
                    
                    # Create a dictionary to store new preference selections
                    new_preferences = {}
                    
                    # For each selected genre, show status options
                    for genre in selected_genres:
                        # Get current status or default to "keep"
                        current_status = genre_preferences.get(genre, "keep")
                        
                        # Show the genre name
                        st.write(f"**{genre}:**")
                        
                        # Radio buttons for status selection
                        options = ["Include in recs", "Pause this genre"]
                        values = ["keep", "paused"]
                        
                        # Find the index of the current status
                        default_idx = 1 if current_status == "paused" else 0
                        
                        # Show horizontal radio buttons
                        status = st.radio(
                            f"Status for {genre}",
                            options=options,
                            index=default_idx,
                            horizontal=True,
                            label_visibility="collapsed",
                            key=f"status_{genre}"
                        )
                        
                        # Map selection back to value
                        status_value = "paused" if status == "Pause this genre" else "keep"
                        
                        # Save to new preferences
                        new_preferences[genre] = status_value
                    
                    # Action buttons using HTML layout instead of columns
                    st.markdown("""
                    <div style="display: flex; gap: 10px; margin-top: 15px;">
                        <div style="flex: 1;" id="cancel-genres-container"></div>
                        <div style="flex: 1;" id="save-genres-container"></div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create placeholders for buttons
                    cancel_genres = st.empty()
                    save_genres = st.empty()
                    
                    # Add buttons to placeholders
                    if cancel_genres.button("Cancel", key="cancel_genres"):
                        st.session_state.edit_genres = False
                        st.rerun()
                    
                    if save_genres.button("Save", key="save_genres"):
                        # Save selected genres
                        profile["genres"] = selected_genres
                        
                        # Save genre preferences
                        profile["genre_preferences"] = new_preferences
                        
                        # Save to profile
                        save_profile()
                        
                        # Exit edit mode
                        st.session_state.edit_genres = False
                        st.rerun()
        
        # Disliked Genres 
        col1, col2 = st.columns([0.07, 0.93])

        with col1:
            st.markdown('<div class="icon-container thumbs-down-icon"><i class="fas fa-thumbs-down"></i></div>', unsafe_allow_html=True)

        with col2:
            with st.expander("Genres You Dislike"):
                if not st.session_state.edit_disliked_genres:
                    if st.button("✏️ Edit", key="edit_disliked_genres_btn"):
                        st.session_state.edit_disliked_genres = True
                        st.rerun()
                    
                    # Display current disliked genres
                    if profile.get("disliked_genres"):
                        for genre in profile.get("disliked_genres", []):
                            st.write(f"• {genre}")
                    else:
                        st.write("No disliked genres specified.")
                else:
                    # Editable multiselect for disliked genres
                    all_genres = get_unique_genres()
                    disliked_genres = st.multiselect(
                        "Select genres you'd prefer to avoid:",
                        options=all_genres,
                        default=profile.get("disliked_genres", [])
                    )
                    
                    # Action buttons using HTML layout instead of columns
                    st.markdown("""
                    <div style="display: flex; gap: 10px; margin-top: 15px;">
                        <div style="flex: 1;" id="cancel-disliked-container"></div>
                        <div style="flex: 1;" id="save-disliked-container"></div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create placeholders for buttons
                    cancel_disliked = st.empty()
                    save_disliked = st.empty()
                    
                    # Add buttons to placeholders
                    if cancel_disliked.button("Cancel", key="cancel_disliked_genres"):
                        st.session_state.edit_disliked_genres = False
                        st.rerun()
                    
                    if save_disliked.button("Save", key="save_disliked_genres"):
                        profile["disliked_genres"] = disliked_genres
                        save_profile()
                        st.session_state.edit_disliked_genres = False
                        st.rerun()

        # Authors Section
        col1, col2 = st.columns([0.07, 0.93])

        with col1:
            st.markdown('<div class="icon-container user-icon"><i class="fas fa-user"></i></div>', unsafe_allow_html=True)

        with col2:
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
                    
                    # Action buttons using HTML layout instead of columns
                    st.markdown("""
                    <div style="display: flex; gap: 10px; margin-top: 15px;">
                        <div style="flex: 1;" id="cancel-authors-container"></div>
                        <div style="flex: 1;" id="save-authors-container"></div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create placeholders for buttons
                    cancel_authors = st.empty()
                    save_authors = st.empty()
                    
                    # Add buttons to placeholders
                    if cancel_authors.button("Cancel", key="cancel_authors"):
                        st.session_state.edit_authors = False
                        st.rerun()
                    
                    if save_authors.button("Save", key="save_authors"):
                        profile["authors"] = selected_authors
                        save_profile()
                        st.session_state.edit_authors = False
                        st.rerun()
        
        # Books Section
        col1, col2 = st.columns([0.07, 0.93])

        with col1:
            st.markdown('<div class="icon-container book-icon"><i class="fas fa-book"></i></div>', unsafe_allow_html=True)

        with col2:
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
                    # Editable multiselect for books
                    all_books = get_unique_books()
                    selected_books = st.multiselect(
                        "Select your favorite books:",
                        options=all_books,
                        default=profile.get("favorite_books", [])
                    )
                    
                    # Action buttons using HTML layout instead of columns
                    st.markdown("""
                    <div style="display: flex; gap: 10px; margin-top: 15px;">
                        <div style="flex: 1;" id="cancel-books-container"></div>
                        <div style="flex: 1;" id="save-books-container"></div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create placeholders for buttons
                    cancel_books = st.empty()
                    save_books = st.empty()
                    
                    # Add buttons to placeholders
                    if cancel_books.button("Cancel", key="cancel_books"):
                        st.session_state.edit_books = False
                        st.rerun()
                    
                    if save_books.button("Save", key="save_books"):
                        profile["favorite_books"] = selected_books
                        save_profile()
                        st.session_state.edit_books = False
                        st.rerun()
        
        # Additional Preferences Section
        col1, col2 = st.columns([0.07, 0.93])

        with col1:
            st.markdown('<div class="icon-container cog-icon"><i class="fas fa-cog"></i></div>', unsafe_allow_html=True)

        with col2:
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
                    # Editable text area for additional preferences
                    additional_prefs = st.text_area(
                        "Additional reading preferences:",
                        value=profile.get("additional_preferences", ""),
                        height=150
                    )
                    
                    # Action buttons using HTML layout instead of columns
                    st.markdown("""
                    <div style="display: flex; gap: 10px; margin-top: 15px;">
                        <div style="flex: 1;" id="cancel-prefs-container"></div>
                        <div style="flex: 1;" id="save-prefs-container"></div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create placeholders for buttons
                    cancel_prefs = st.empty()
                    save_prefs = st.empty()
                    
                    # Add buttons to placeholders
                    if cancel_prefs.button("Cancel", key="cancel_prefs"):
                        st.session_state.edit_preferences = False
                        st.rerun()
                    
                    if save_prefs.button("Save", key="save_prefs"):
                        profile["additional_preferences"] = additional_prefs
                        save_profile()
                        st.session_state.edit_preferences = False
                        st.rerun()
        
        # Ratings Section
        col1, col2 = st.columns([0.07, 0.93])

        with col1:
            st.markdown('<div class="icon-container star-icon"><i class="fas fa-star"></i></div>', unsafe_allow_html=True)

        with col2:
            with st.expander("Books You've Rated"):
                if profile.get("ratings") and len(profile.get("ratings")) > 0:
                    for book_title, rating in profile.get("ratings").items():
                        st.write(f"• {book_title}: {'★' * rating}")
                else:
                    st.write("You haven't rated any books yet.")
        
        # Not Interested Section
        col1, col2 = st.columns([0.07, 0.93])

        with col1:
            st.markdown('<div class="icon-container ban-icon"><i class="fas fa-ban"></i></div>', unsafe_allow_html=True)

        with col2:
            with st.expander("Books You're Not Interested In"):
                if profile.get("not_interested"):
                    for book in profile.get("not_interested", []):
                        st.write(f"• {book}")
                else:
                    st.write("No books marked as 'not interested'.")
    
    with spacer_col:
        st.empty()

    # RIGHT COLUMN: Visualization - kept separate from left column



    with right_col:
        st.markdown("### Genre Map")
        st.markdown(
            """
            Your selections are mapped alongside genre linkages derived from the habits of tens of thousands of other readers—revealing how your reading identity fits into the bigger picture. 
            In this diagram, each arc represents a genre, and the connecting chords show how often those genres co-occur in others’ reading histories. 
            Thicker chords indicate stronger connections. Hover to explore, or click the 
            <strong style="color: #4e7694;">Show All Genre Connections</strong> button below to see the entire reading web.
            """,
            unsafe_allow_html=True
        )
        # Load the genre data
        try:
            genre_metadata, genre_connections = load_chord_viz_data()
            
            # Get user's selected genres for highlighting
            user_genres = profile.get("genres", [])
            
            # Generate chord diagram HTML with user preferences included
            chord_html = create_genre_chord_diagram(
                genre_metadata=genre_metadata,
                genre_connections=genre_connections,
                top_n_genres=30,
                top_n_connections=100,
                user_genres=user_genres  # Pass user genres to highlight them
            )

            # Display the chord diagram with appropriate height
            components.html(chord_html, height=1200, scrolling=True)
            
            # Add instructions for using the visualization
            with st.expander("How to use this visualization"):
                st.markdown("""
                - **Hover** over a genre segment to highlight all its connections
                - **Click** on a genre segment to focus exclusively on its connections
                - **Hover** over a connection to see details about the strength of relationship
                
                In the tooltip, Connection Strength shows how frequently readers who enjoy one genre also read books from the other genre. 
                A higher percentage means a stronger pattern of these genres appearing together in readers' libraries.

                Genres you've selected in your profile are highlighted with a black border.
                """)
            
        except Exception as e:
            st.error(f"Unable to display genre visualization: {str(e)}")
            st.info("Please ensure you have the genre data files in the correct location.")

