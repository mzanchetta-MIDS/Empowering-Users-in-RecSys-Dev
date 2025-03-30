# sections/profile.py
import streamlit as st
import json
import numpy as np
import pandas as pd
import logging 
import plotly.graph_objects as go
from utils.profile_utils import save_profile
from utils.data_utils import get_unique_genres, get_unique_authors, get_unique_books, get_genre_embeddings
from streamlit_extras.stylable_container import stylable_container

def create_profile_visualization(profile):
    """Create a 3D visualization using genre embeddings from database"""

    # Get user's selected genres
    user_genres = profile.get("genres", [])
    
    # Base genres for fallback
    base_genre_names = [
        "Fantasy", "Science Fiction", "Mystery", "Romance", "Historical Fiction",
        "Literary Fiction", "Thriller", "Horror", "Biography", "Self Help",
        "Poetry", "Memoir", "Philosophy", "Psychology", "History",
        "Politics", "Travel", "Art", "Music", "Drama",
        "Young Adult", "Children's", "Graphic Novel", "Comic", "Manga",
        "Classic", "Contemporary", "Short Story", "Essay", "Non-Fiction",
        "True Crime", "Adventure", "Dystopian", "Utopian", "Western",
        "Satire", "Comedy", "Tragedy", "Mythology", "Folklore"
    ]
    
    # Try to fetch genre embeddings from API
    try:
        # Get embeddings from the API
        response = get_genre_embeddings()
        
        if response and "embeddings" in response and response["embeddings"]:
            # Create genre coordinates dictionary from API response
            genre_coords = {}
            all_db_genres = []
            
            for item in response["embeddings"]:
                genre = item["genre_name"]
                coords = np.array([item["embedding_x"], item["embedding_y"], item["embedding_z"]])
                genre_coords[genre] = coords
                all_db_genres.append(genre)
                
            logging.info(f"Successfully loaded {len(genre_coords)} genre embeddings from API")
            using_db_data = True
        else:
            logging.warning("No genre embeddings found in API response, falling back to notional data")
            using_db_data = False
    except Exception as e:
        logging.error(f"Error fetching genre embeddings from API: {str(e)}")
        using_db_data = False
    
    # Fallback to notional data if API fetch failed
    if not using_db_data:
        logging.info("Using notional genre embeddings")
        
        # Create notional 3D coordinates for each genre
        np.random.seed(42)
        
        # Generate consistent random coordinates for each genre
        genre_coords = {}
        for genre in base_genre_names:
            hash_val = hash(genre) % 10000
            np.random.seed(hash_val)
            genre_coords[genre] = np.random.normal(0, 1, 3)
        
        # Use base genres as the full list when using notional data
        all_db_genres = base_genre_names
    
    # Compile the final list of genres to visualize
    all_genres = []
    
    # Add user genres first
    for genre in user_genres:
        if genre not in all_genres:
            all_genres.append(genre)
    
    # Add remaining genres from database or base list
    for genre in all_db_genres:
        if genre not in all_genres:
            all_genres.append(genre)
    
    # Limit to 100 genres total for better visualization performance
    all_genres = all_genres[:100]
    
    # For any user genres not in our dictionary, create random coordinates
    for genre in user_genres:
        if genre not in genre_coords:
            hash_val = hash(genre) % 10000
            np.random.seed(hash_val)
            genre_coords[genre] = np.random.normal(0, 1, 3)
    
    # Create a DataFrame with the genre data
    genres_data = []
    for genre in all_genres:
        coords = genre_coords.get(genre, np.random.normal(0, 1, 3))
        genres_data.append({
            'name': genre,
            'x': coords[0],
            'y': coords[1], 
            'z': coords[2],
            'type': 'Genre',
            'is_selected': genre in user_genres
        })
    
    # Create a DataFrame
    df = pd.DataFrame(genres_data)
    
    # Will replace with model results later 
    if user_genres:
        # Calculate user position as average of selected genres
        user_genres_coords = np.array([genre_coords[g] for g in user_genres if g in genre_coords])
        if len(user_genres_coords) > 0:
            user_coords = user_genres_coords.mean(axis=0)
        else:
            user_coords = np.random.normal(0, 1, 3)
    else:
        user_coords = np.random.normal(0, 1, 3)
    
    # Add user profile to the DataFrame
    user_data = {
        'name': 'Your Profile',
        'x': user_coords[0],
        'y': user_coords[1],
        'z': user_coords[2],
        'type': 'User Profile',
        'is_selected': False
    }
    df = pd.concat([df, pd.DataFrame([user_data])], ignore_index=True)
    
    # Create different colors based on type and selection
    colors = []
    for _, row in df.iterrows():
        if row['type'] == 'User Profile':
            colors.append('#4e7694')  # User profile in blue
        elif row['is_selected']:
            colors.append('#9C897E')  # Selected genres in brown
        else:
            colors.append('#C0C0C0')  # Other genres in light gray
    
    # Create a 3D scatter plot
    fig = go.Figure(data=[go.Scatter3d(
        x=df['x'],
        y=df['y'],
        z=df['z'],
        mode='markers',
        marker=dict(
            size=5,
            color=colors,
            opacity=0.8
        ),
        text=df['name'],
        hoverinfo='text',
        showlegend=False
    )])
    
    # Highlight the user's position
    fig.add_trace(go.Scatter3d(
        x=[user_coords[0]],
        y=[user_coords[1]],
        z=[user_coords[2]],
        mode='markers',
        marker=dict(
            size=10,
            color='#4e7694',
            symbol='circle',
            line=dict(
                color='white',
                width=2
            )
        ),
        text=['Your Profile'],
        hoverinfo='text',
        showlegend=False
    ))
    
    fig.update_layout(
        scene=dict(
            xaxis=dict(title='', showticklabels=False),
            yaxis=dict(title='', showticklabels=False),
            zaxis=dict(title='', showticklabels=False),
            bgcolor='#F5F2EB'
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        height=600,  
        paper_bgcolor='#F5F2EB',
        showlegend=False
    )
    
    return fig, df


###########

def show_profile():
    st.subheader("Your Reading Profile")
    
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
    
    # Font-awesome link and icon styles remain the same
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
    left_col, spacer_col, right_col = st.columns([1, 0.05, 1.2])

    # LEFT COLUMN: Preferences
    with left_col:
        st.markdown("### Your Preferences")
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
        st.markdown("### Profile Visualization")
        st.write("This visualization shows how your reading profile relates to different book genres in 3D space.")
        
        viz_fig, viz_data = create_profile_visualization(profile)
        st.plotly_chart(viz_fig, use_container_width=True)
        
        # Show closest genres if user has selected genres
        if profile.get("genres"):
            # User coordinates
            user_coords = viz_data[viz_data['type'] == 'User Profile'][['x', 'y', 'z']].values[0]
            
            # Euclidean distance
            def calc_distance(row):
                genre_coords = row[['x', 'y', 'z']].values
                return np.sqrt(np.sum((genre_coords - user_coords)**2))
            
            genres_df = viz_data[viz_data['type'] == 'Genre'].copy()
            genres_df['distance'] = genres_df.apply(calc_distance, axis=1)
            
            # Sort by distance and show top 5
            closest_genres = genres_df.sort_values('distance').head(5)
            
            st.markdown("#### Your profile is most aligned with:")
            
            # Instead of using columns, create a formatted HTML display
            genre_html = '<div style="display: flex; flex-wrap: wrap;">'
            
            for i, (_, genre) in enumerate(closest_genres.iterrows()):
                # Add each genre as a div that takes roughly half the width
                genre_html += f'<div style="flex: 0 0 50%; margin-bottom: 8px;">• {genre["name"]}</div>'
            
            genre_html += '</div>'
            st.markdown(genre_html, unsafe_allow_html=True)