# sections/profile.py
import streamlit as st
import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from utils.profile_utils import save_profile
from utils.data_utils import get_unique_genres, get_unique_authors, get_unique_books

def create_profile_visualization(profile):
    """Create a 3D visualization using pre-calculated coordinates"""
    # In production, these will change 
    
    # Get user's selected genres
    user_genres = profile.get("genres", [])
    
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
    
    all_genres = []
    
    # Add user genres first
    for genre in user_genres:
        if genre not in all_genres:
            all_genres.append(genre)
    
    # Add base genres
    for genre in base_genre_names:
        if genre not in all_genres:
            all_genres.append(genre)
    
    # Limit to 100 genres total for better visualization performance
    all_genres = all_genres[:100]
    
    # Create notional 3D coordinates for each genre
    np.random.seed(42)  
    
    # Generate consistent random coordinates for each genre
    genre_coords = {}
    for genre in base_genre_names:
        hash_val = hash(genre) % 10000
        np.random.seed(hash_val)
        genre_coords[genre] = np.random.normal(0, 1, 3)
    
    # For any user genres not in our base list, create random coordinates
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
    
    # In production, this will come from model
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
            colors.append('#4e7694')  # User profile in red
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
    
    st.markdown("""
    <style>
    .streamlit-expanderHeader {
        background-color: #9C897E !important;
        color: white !important;
        font-weight: 500 !important;
        border-radius: 5px !important;
        padding: 12px 15px !important;
        font-size: 1.2em !important;
        margin-bottom: 5px !important;
    }
    
    .streamlit-expanderContent {
        background-color: #F5F2EB !important;
        border: 1px solid #E6E3DC !important;
        border-top: none !important;
        border-radius: 0 0 5px 5px !important;
        padding: 20px !important;
        font-size: 1.1em !important;
        margin-bottom: 15px !important;
    }
    
    .column-header {
        font-size: 1.5em;
        font-weight: bold;
        margin-bottom: 10px;
        color: #080603;
    }
    
    .column-subtext {
        font-size: 1.1em;
        margin-bottom: 20px;
        color: #555;
    }
    
    /* Ensure list items are larger too */
    .streamlit-expanderContent li,
    .streamlit-expanderContent p {
        font-size: 1.1em !important;
        line-height: 1.6 !important;
        margin-bottom: 8px !important;
    }
    
    /* Add spacing between columns */
    .spacer {
        margin: 0 15px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create two columns layout with specific width ratio 
    col1, spacer, col2 = st.columns([1, 0.1, 2])
    
    # Left column: Preferences
    with col1:
        st.markdown("### Your Preferences")
        st.write("Click each attribute below to view and edit your preferences.")
        
        # Favorite Genres Section with preference controls
        with st.expander("Favorite Genres"):
            if not st.session_state.edit_genres:
                if st.button("✏️ Edit Genres & Frequency", key="edit_genres_btn"):
                    st.session_state.edit_genres = True
                    st.rerun()
                
                # Display current genres with preference level
                if profile.get("genres"):
                    # Get genre preferences dictionary
                    genre_preferences = profile.get("genre_preferences", {})
                    
                    for genre in profile.get("genres", []):
                        # Get preference level with "default" as fallback
                        preference = genre_preferences.get(genre, "default")
                        
                        # Format the display text based on preference
                        if preference == "more":
                            preference_text = "(See more often)"
                        elif preference == "less":
                            preference_text = "(See less often)"
                        else:
                            preference_text = ""  
                        
                        # Display the genre with its preference
                        st.write(f"• {genre} {preference_text}")
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
                
                st.write("For each selected genre, indicate how often you'd like to see it in your recommendations:")
                
                # Initialize or get existing genre preferences
                genre_preferences = profile.get("genre_preferences", {})
                
                # Create a dictionary to store new preference selections
                new_preferences = {}
                
                # For each selected genre, show preference options
                for genre in selected_genres:
                    # Get current preference or default
                    current_pref = genre_preferences.get(genre, "default")
                    
                    # Create columns for genre name and preference selection
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.write(f"{genre}:")
                    
                    with col2:
                        # Radio buttons for preference selection
                        options = ["See less often", "Default", "See more often"]
                        values = ["less", "default", "more"]
                        
                        # Find the index of the current preference
                        default_idx = values.index(current_pref) if current_pref in values else 1
                        
                        # Show horizontal radio buttons
                        pref = st.radio(
                            f"Preference for {genre}",
                            options=options,
                            index=default_idx,
                            horizontal=True,
                            label_visibility="collapsed",
                            key=f"pref_{genre}"
                        )
                        
                        # Map selection back to value
                        pref_value = values[options.index(pref)]
                        
                        # Save to new preferences
                        new_preferences[genre] = pref_value
                
                # Action buttons
                col_a, col_b = st.columns([1, 1])
                with col_a:
                    if st.button("Cancel", key="cancel_genres"):
                        st.session_state.edit_genres = False
                        st.rerun()
                with col_b:
                    if st.button("Save", key="save_genres"):
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
        with st.expander("Genres You Dislike"):
            # Initialize edit state if not exists
            if "edit_disliked_genres" not in st.session_state:
                st.session_state.edit_disliked_genres = False
                
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
                
                col_a, col_b = st.columns([1, 1])
                with col_a:
                    if st.button("Cancel", key="cancel_disliked_genres"):
                        st.session_state.edit_disliked_genres = False
                        st.rerun()
                with col_b:
                    if st.button("Save", key="save_disliked_genres"):
                        profile["disliked_genres"] = disliked_genres
                        save_profile()
                        st.session_state.edit_disliked_genres = False
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
                
                col_a, col_b = st.columns([1, 1])
                with col_a:
                    if st.button("Cancel", key="cancel_authors"):
                        st.session_state.edit_authors = False
                        st.rerun()
                with col_b:
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
                # Editable multiselect for books
                all_books = get_unique_books()
                selected_books = st.multiselect(
                    "Select your favorite books:",
                    options=all_books,
                    default=profile.get("favorite_books", [])
                )
                
                col_a, col_b = st.columns([1, 1])
                with col_a:
                    if st.button("Cancel", key="cancel_books"):
                        st.session_state.edit_books = False
                        st.rerun()
                with col_b:
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
                # Editable text area for additional preferences
                additional_prefs = st.text_area(
                    "Additional reading preferences:",
                    value=profile.get("additional_preferences", ""),
                    height=150
                )
                
                col_a, col_b = st.columns([1, 1])
                with col_a:
                    if st.button("Cancel", key="cancel_prefs"):
                        st.session_state.edit_preferences = False
                        st.rerun()
                with col_b:
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
    
    # Spacer column - empty column to create space between the main columns
    with spacer:
        st.empty()
    
    # Right column: Visualization
    with col2:
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
