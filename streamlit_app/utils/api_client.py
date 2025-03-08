import requests
import streamlit as st
import json

# Base configuration
API_BASE_URL = "http://localhost:8000"  # Change for production

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
        response = requests.post(
            f"{API_BASE_URL}/rec/users/profile",
            json=profile_data
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
            response = requests.post(
                f"{API_BASE_URL}/rec/recommendations",
                json=profile_data
            )
            if response.status_code == 200:
                return response.json()["recommendations"]
            st.error(f"Failed to get recommendations: {response.status_code}")
        else:
            st.error("No user profile found in session")
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
    return []