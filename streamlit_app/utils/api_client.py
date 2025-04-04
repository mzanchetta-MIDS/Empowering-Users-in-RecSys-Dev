import requests
import streamlit as st
import json
import uuid
import logging

# Set up logging 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base configuration
API_BASE_URL = "http://localhost:8000"  

def transform_profile_for_recommendation_api(user_profile):
    """
    Transform the user profile into the format required by the recommendation API.
    """
    # Generate a random user ID hash if not already present
    if "user_id" not in user_profile:
        user_profile["user_id"] = str(uuid.uuid4())
    
    # Initialize the API format structure with all fields
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
                "books_history": [], 
                
                # Fields to ignore but including for completeness
                "authors": 0,
                "categories": 0,
                "description": 0,
                "target_book": 0,
                "target_book_rating": 0
            }
        ]
    }
    
    # Helper function to extract just the title from a book entry
    def extract_title(book_entry):
        if isinstance(book_entry, dict):
            # For dictionary objects (like in saved_for_later)
            return book_entry.get("title", "")
        elif isinstance(book_entry, str) and " - " in book_entry:
            # For "Title - Author" format (like in favorite_books)
            return book_entry.split(" - ", 1)[0].strip()
        else:
            # Already just a title or unknown format
            return book_entry
    
    # Set to track all unique book titles the user has interacted with
    all_books = set()
    
    # Process favorite books (onboarding) - rule #1
    for book in user_profile.get("favorite_books", []):
        title = extract_title(book)
        if title:
            api_format["instances"][0]["liked_books"][title] = 5
            all_books.add(title)
    
    # Process ratings - rule #3
    for book, rating in user_profile.get("ratings", {}).items():
        title = extract_title(book)
        if title:
            if rating >= 3:  # 3, 4, or 5 stars
                api_format["instances"][0]["liked_books"][title] = rating
            else:  # 1 or 2 stars
                api_format["instances"][0]["disliked_books"][title] = rating
            all_books.add(title)
    
    # Process books marked as "not interested" - rule #2
    for book in user_profile.get("not_interested", []):
        title = extract_title(book)
        if title:
            api_format["instances"][0]["disliked_books"][title] = 1
            all_books.add(title)
    
    # Process books saved for later - rule #3 (before rating)
    for book_obj in user_profile.get("saved_for_later", []):
        title = extract_title(book_obj)
        if title and title not in api_format["instances"][0]["liked_books"]:
            api_format["instances"][0]["liked_books"][title] = 4
            all_books.add(title)
    
    # Process recommendation history
    for book_title in user_profile.get("recommended_history", []):
        title = extract_title(book_title)
        if title:
            all_books.add(title)
    
    # Set books_history from all unique books
    api_format["instances"][0]["books_history"] = list(all_books)
    
    # Process genres and preferences - using genre_preferences
    for genre in user_profile.get("genres", []):
        preference = user_profile.get("genre_preferences", {}).get(genre, "keep")
        api_format["instances"][0]["liked_genres"][genre] = preference
    
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
    
def get_book_covers():
    """Fetch book covers mapping from API"""
    try:
        print(f"DEBUG: Requesting book covers from {API_BASE_URL}/rec/book-covers")
        response = requests.get(f"{API_BASE_URL}/rec/book-covers")
        print(f"DEBUG: Response status: {response.status_code}")
        print(f"DEBUG: Response content: {response.text[:200]}...")  
        
        if response.status_code == 200:
            data = response.json()
            print(f"DEBUG: Received {len(data.get('covers', []))} covers")
            return data.get("covers", [])
        logger.error(f"Failed to fetch book covers: {response.status_code}")
    except Exception as e:
        logger.error(f"Error connecting to API: {str(e)}")
        print(f"DEBUG: Exception in get_book_covers: {str(e)}")
    return []  # Fallback to empty list if API fails


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

# Setup logger for this file
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_recommendations():
    """
    Get personalized recommendations based on user profile.
    
    Returns a list of book recommendations in the shape:
    [
      {
        "title": "...",
        "author": "...",
        "description": "...",
        "explanation": "..."
      },
      ...
    ]
    """
    try:
        # Use the profile data from session state
        if "user_profile" in st.session_state:
            profile_data = st.session_state.user_profile

            # Transform profile into the format the API expects
            api_format = transform_profile_for_recommendation_api(profile_data)
            
            # print(f"DEBUG: API format for recommendations: {api_format}")
            
            # print("api_format type:", type(api_format))
            
            api_format = json.dumps(api_format)
            # print(f"DEBUG: JSON formatted API data: {api_format}")
            # print("api_format type after json.dumps:", type(api_format))
            
            try:
                # Make the POST request, sending JSON
                response = requests.post(
                    f"{API_BASE_URL}/rec/recommendations",
                    params = {"profile": json.dumps(api_format)}
                )

                # Debug prints for troubleshooting
                # print("DEBUG status code:", response.status_code)
                # print("DEBUG response text:", response.text)

                if response.status_code == 200:
                    # Parse the JSON
                    response_data = response.json()
                    
                    # Store the embeddings in session state for later visualization
                    if "recommendations" in response_data:
                        rec_data = response_data["recommendations"]
                        if "pca_book_embeddings" in rec_data:
                            st.session_state.pca_book_embeddings = rec_data["pca_book_embeddings"]
                        if "pca_user_embeddings" in rec_data:
                            st.session_state.pca_user_embeddings = rec_data["pca_user_embeddings"]
                    
                    # The new structure has recommendations inside a nested "recommendations" object
                    raw_recommendations = response_data.get("recommendations", {}).get("recommendations", [])
                    
                    processed_recommendations = []
                    
                    for rec in raw_recommendations:
                        # Skip time elapsed entries if present
                        if isinstance(rec, list) and rec[0] == "time elapsed":
                            continue

                        # Try to parse the string in rec["explanation"]
                        explanation_json_str = rec.get("explanation", "{}")
                        try:
                            explanation_data = json.loads(explanation_json_str)
                            rec_data = explanation_data.get("recommendation_explanation", {})

                            # Build a dict in the shape our UI needs
                            processed_rec = {
                                "title": rec_data.get("recommended_book", rec.get("title", "Unknown Title")),
                                "author": rec_data.get("author", "Unknown Author"),
                                "description": rec_data.get("description", "No description available."),
                                "explanation": rec_data.get("explanation", "No explanation available.")
                            }
                            
                            processed_recommendations.append(processed_rec)
                        except json.JSONDecodeError:
                            # If parsing fails, fall back on top-level fields
                            logger.error(f"Error parsing recommendation explanation: {explanation_json_str}")
                            processed_recommendations.append({
                                "title": rec.get("title", "Unknown Title"),
                                "author": "Unknown Author",
                                "description": "Description unavailable",
                                "explanation": "Explanation unavailable"
                            })
                    
                    return processed_recommendations
                
                # If status not 200, log an error and fall back
                logger.error(f"Failed to get recommendations: {response.status_code} - {response.text}")
            except Exception as e:
                logger.error(f"Error making recommendation request: {str(e)}")
        else:
            logger.error("No user profile found in session")
    except Exception as e:
        logger.error(f"Error in get_recommendations: {str(e)}")
    
    # Fallback if we never returned anything above
    return [
        {
            "title": "The Master and Margarita",
            "author": "Mikhail Bulgakov",
            "description": "A masterpiece of satire and fantasy about the Devil visiting Soviet Moscow.",
            "explanation": "We're sorry, but we encountered an error retrieving your personalized recommendations."
        }
    ]