import requests
import streamlit as st

# Base configuration
API_BASE_URL = "http://localhost:8000"  # Change for production

def get_genres():
    """Fetch available genres from API"""
    response = requests.get(f"{API_BASE_URL}/genres")
    if response.status_code == 200:
        return response.json()
    return []  # Fallback to empty list if API fails

def get_authors():
    """Fetch available authors from API"""
    response = requests.get(f"{API_BASE_URL}/authors")
    if response.status_code == 200:
        return response.json()
    return []

def get_books():
    """Fetch available books for selection"""
    response = requests.get(f"{API_BASE_URL}/books")
    if response.status_code == 200:
        return response.json()
    return []

def submit_user_profile(profile_data):
    """Submit user profile after onboarding"""
    response = requests.post(
        f"{API_BASE_URL}/users/profile",
        json=profile_data
    )
    if response.status_code == 200:
        return response.json()
    return {"error": "Failed to submit profile"}

def get_recommendations(user_id=None):
    """Get personalized recommendations"""
    # If no user_id, use session profile data
    if not user_id and "user_profile" in st.session_state:
        profile_data = st.session_state.user_profile
        response = requests.post(
            f"{API_BASE_URL}/recommendations",
            json=profile_data
        )
    else:
        response = requests.get(f"{API_BASE_URL}/recommendations/{user_id}")
        
    if response.status_code == 200:
        return response.json()
    return []

def send_user_feedback(user_id, book_id, feedback_type, value=None):
    """Send user feedback (rating, saved, not interested)"""
    data = {
        "book_id": book_id,
        "feedback_type": feedback_type,
        "value": value
    }
    response = requests.post(
        f"{API_BASE_URL}/users/{user_id}/feedback",
        json=data
    )
    return response.status_code == 200