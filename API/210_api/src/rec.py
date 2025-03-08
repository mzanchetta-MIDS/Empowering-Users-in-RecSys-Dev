from pydantic import BaseModel, field_validator
from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse
from datetime import datetime
import joblib
#import numpy as np
from datetime import datetime

from typing import List, Dict, Any, Optional
import json

# load the rec model
#rec_model = joblib.load('rec_model.pkl')

# load the LLM model
#llm_model = joblib.load('llm_model.pkl')

rec = FastAPI()


class GenreResponse(BaseModel):
    genres: List[str]

class AuthorResponse(BaseModel):
    authors: List[str]

class BookResponse(BaseModel):
    books: List[str]

class UserProfile(BaseModel):
    name: Optional[str] = None
    genres: Optional[List[str]] = None
    authors: Optional[List[str]] = None
    favorite_books: Optional[List[str]] = None
    additional_preferences: Optional[str] = None
    ratings: Optional[Dict[str, int]] = None
    not_interested: Optional[List[str]] = None
    saved_for_later: Optional[List[Dict[str, Any]]] = None

class RecommendationResponse(BaseModel):
    recommendations: List[Dict[str, Any]]

@rec.get("/genres", response_model=GenreResponse)
async def get_genres():
    # Hard-coded genres for now
    genres = [
        "Fiction", "Non-Fiction", "Mystery", "Fantasy",
        "Science Fiction", "Romance", "History", "Business"
    ]
    return {"genres": genres}

@rec.get("/authors", response_model=AuthorResponse)
async def get_authors():
    # Hard-coded authors for now
    authors = [
        "J.K. Rowling", "Stephen King", "Jane Austen",
        "Agatha Christie", "Neil Gaiman", "George R.R. Martin", "Michael Lewis"
    ]
    return {"authors": authors}

@rec.get("/books", response_model=BookResponse)
async def get_books():
    # Hard-coded books for now
    books = [
        "To Kill a Mockingbird - Harper Lee",
        "1984 - George Orwell",
        "Pride and Prejudice - Jane Austen",
        "The Great Gatsby - F. Scott Fitzgerald",
        "Moby Dick - Herman Melville",
        "Moneyball - Michael Lewis"
    ]
    return {"books": books}

@rec.post("/users/profile")
async def update_user_profile(profile: UserProfile):
    print("\n----- RECEIVED PROFILE UPDATE -----")
    print(profile.dict())
    print("-----------------------------------\n")
    return {"message": "Profile updated successfully"}


@rec.post("/recommendations")
async def get_recommendations(profile: UserProfile):
    # Hard-coded recommendations for now
    # In a real implementation, this would use a recommendation model
    recommendations = [
        {
            "id": "book-001",
            "title": "The Haunted Lighthouse",
            "author": "Stephen King",
            "description": "A chilling tale of an abandoned lighthouse haunted by past tragedies.",
            "explanation": "Recommended because you enjoy horror with strong atmospheric tension."
        },
        {
            "id": "book-002",
            "title": "Pride and Prejudice",
            "author": "Jane Austen",
            "description": "A classic novel that offers sharp social commentary and a timeless love story.",
            "explanation": "Recommended based on your interest in historical settings with rich character development."
        },
        {
            "id": "book-003",
            "title": "American Gods",
            "author": "Neil Gaiman",
            "description": "A blend of myth, fantasy, and Americana, featuring old gods struggling in the modern world.",
            "explanation": "This matches your interest in fantasy and mythology themes."
        },
        {
            "id": "book-004",
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "description": "A tale of wealth, love, and disillusionment during the Jazz Age, exploring the American Dream and its corruptions.",
            "explanation": "Based on your preference for classics with rich symbolism and complex characters."
        },
        {
            "id": "book-005",
            "title": "To Kill a Mockingbird",
            "author": "Harper Lee",
            "description": "A powerful exploration of racial injustice and moral growth in the American South, told through the eyes of a young girl.",
            "explanation": "Suggested because you enjoy character-driven narratives with social commentary."
        },
        {
            "id": "book-006",
            "title": "1984",
            "author": "George Orwell",
            "description": "A dystopian novel exploring the dangers of totalitarianism, surveillance, and the manipulation of truth.",
            "explanation": "Recommended based on your interest in thought-provoking literature with relevant social themes."
        },
        {
            "id": "book-007",
            "title": "The Road",
            "author": "Cormac McCarthy",
            "description": "A post-apocalyptic tale of a father and son's journey through a desolate America, exploring themes of survival and hope.",
            "explanation": "This aligns with your appreciation for emotionally impactful stories with atmospheric writing."
        },
        {
            "id": "book-008",
            "title": "Dune",
            "author": "Frank Herbert",
            "description": "An epic science fiction adventure set on a desert planet, featuring political intrigue, ecological themes, and mystical elements.",
            "explanation": "Suggested because you enjoy immersive world-building and complex political narratives."
        },
        {
            "id": "book-009",
            "title": "The Name of the Wind",
            "author": "Patrick Rothfuss",
            "description": "A richly detailed fantasy following the life of Kvothe, a legendary musician and adventurer recounting his extraordinary life story.",
            "explanation": "This matches your interest in fantasy with detailed magic systems and compelling character journeys."
        }
    ]
    return {"recommendations": recommendations}

