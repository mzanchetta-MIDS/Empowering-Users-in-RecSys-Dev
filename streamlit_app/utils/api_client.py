import requests
import streamlit as st
import json
import uuid

# Base configuration
API_BASE_URL = "http://localhost:8000"  # Change for production

def transform_profile_for_recommendation_api(user_profile):
    """
    Transform the user profile into the format required by the recommendation API.
    """
    # Generate a random user ID hash if not already present
    if "user_id" not in user_profile:
        user_profile["user_id"] = str(uuid.uuid4())
    
    # Initialize the API format structure
    api_format = {
        "instances": [
            {
                "user_id": user_profile["user_id"],
                "liked_books": {},
                "disliked_books": {},
                "liked_genres": {},
                "disliked_genres": [],
                "liked_authors": user_profile.get("authors", []),
                "disliked_authors": [],
                "additional_preferences": user_profile.get("additional_preferences", ""),
                
                # Fields we're ignoring but including for completeness
                "authors": 0,
                "categories": 0,
                "description": 0,
                "target_book": 0,
                "target_book_rating": 0
            }
        ]
    }
    
    # Process favorite books (onboarding) - rule #1
    for book in user_profile.get("favorite_books", []):
        api_format["instances"][0]["liked_books"][book] = 5
    
    # Process ratings - rule #3
    for book, rating in user_profile.get("ratings", {}).items():
        if rating >= 3:  # 3, 4, or 5 stars
            api_format["instances"][0]["liked_books"][book] = rating
        else:  # 1 or 2 stars
            api_format["instances"][0]["disliked_books"][book] = rating
    
    # Process books marked as "not interested" - rule #2
    for book in user_profile.get("not_interested", []):
        api_format["instances"][0]["disliked_books"][book] = 1
    
    # Process books saved for later - rule #3 (before rating)
    for book_obj in user_profile.get("saved_for_later", []):
        if isinstance(book_obj, dict):
            book_title = book_obj.get("title", "")
            if book_title and book_title not in api_format["instances"][0]["liked_books"]:
                api_format["instances"][0]["liked_books"][book_title] = 4
    
    # Process genres and preferences - using genre_preferences
    for genre in user_profile.get("genres", []):
        preference = user_profile.get("genre_preferences", {}).get(genre, "default")
        
        # Convert text preference to numerical weight
        if preference == "more":
            weight = 1.5
        elif preference == "less":
            weight = 0.5
        else:  # default
            weight = 1.0
            
        api_format["instances"][0]["liked_genres"][genre] = weight
    
    # Process disliked genres
    for genre in user_profile.get("disliked_genres", []):
        api_format["instances"][0]["disliked_genres"].append(genre)
    
    return api_format

def get_genres():
    """Fetch available genres from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/rec/genres")
        if response.status_code == 200:
            return response.json()["genres"]
        st.error(f"Failed to fetch genres: {response.status_code}")
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
    return []  # Fallback to empty list if API fails

def get_authors():
    """Fetch available authors from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/rec/authors")
        if response.status_code == 200:
            return response.json()["authors"]
        st.error(f"Failed to fetch authors: {response.status_code}")
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
    return []

def get_books():
    """Fetch available books for selection"""
    try:
        response = requests.get(f"{API_BASE_URL}/rec/books")
        if response.status_code == 200:
            return response.json()["books"]
        st.error(f"Failed to fetch books: {response.status_code}")
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
    return []

def submit_user_profile(profile_data):
    """Submit user profile after onboarding or updates"""
    try:
        # Transform profile before submitting
        api_format = transform_profile_for_recommendation_api(profile_data)
        
        response = requests.post(
            f"{API_BASE_URL}/rec/users/profile",
            json=api_format
        )
        if response.status_code == 200:
            return response.json()
        st.error(f"Failed to submit profile: {response.status_code}")
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
    return {"error": "Failed to submit profile"}

def get_recommendations():
    """Get personalized recommendations based on user profile"""
    try:
        # Use the profile data from session state
        if "user_profile" in st.session_state:
            profile_data = st.session_state.user_profile
            
            # Transform profile into API format
            api_format = transform_profile_for_recommendation_api(profile_data)
            
            response = requests.post(
                f"{API_BASE_URL}/rec/recommendations",
                json=api_format
            )
            if response.status_code == 200:
                return response.json()["recommendations"]
            st.error(f"Failed to get recommendations: {response.status_code}")
        else:
            st.error("No user profile found in session")
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
    return []