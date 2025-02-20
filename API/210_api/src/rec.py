from pydantic import BaseModel, field_validator
from typing import List, Optional

from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse
from datetime import datetime
import joblib
#import numpy as np
from datetime import datetime

# load the rec model
#rec_model = joblib.load('rec_model.pkl')

# load the LLM model
#llm_model = joblib.load('llm_model.pkl')

rec = FastAPI()



class User(BaseModel):
    user_id: int
    user_name: str
    user_email: str
    user_password: str
    user_dob: datetime
    
class UserUpdate(BaseModel):
    user_id: int
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    user_password: Optional[str] = None
    user_dob: Optional[datetime] = None
    
class UserRecovery(BaseModel):
    user_email: str
    user_dob: datetime
    
class UserDelete(BaseModel):
    user_id: int
    user_password: str
    
class UserHistory(BaseModel):
    user_id: int
    
class UserRecommended(BaseModel):
    user_id: int
    title: str
    review_score: int
    
class UserRecommendedResponse(BaseModel):
    recommendations: List[str]
    
class UserLLM(BaseModel):
    user_id: int
    user_book: str
    
# class UserRecommendationFilters(BaseModel):
#     user_id: int
#     user_filters: List[str]
    
# class UserCookies(BaseModel):
#     user_id: int
#     user_cookies: List[str]
    
# class UserReviews(BaseModel):
#     user_id: int
#     user_book: str
#     user_rating: int
    
# class UserSocialRequest(BaseModel):
#     user_id: int
#     user_friend: int
    
# class UserSocialList(BaseModel):
#     user_id: int
    
# class UserSocialConnect(BaseModel):
#     user_id: int
#     user_social: str
#     user_social_id: str
    
# define the API endpoints

@rec.get("/")
async def root():
    return {"message": "Hello World"}

@rec.post("/register")
async def register(user: User):
    return {"message": "User registered successfully"}

@rec.post("/login")
async def login(user: User):
    return {"message": "User logged in successfully"}

@rec.put("/update")
async def update(user: UserUpdate):
    return {"message": "User updated successfully"}

@rec.post("/recovery")
async def recovery(user: UserRecovery):
    return {"message": "User recovered successfully"}

@rec.delete("/delete")
async def delete(user: UserDelete):
    return {"message": "User deleted successfully"}

@rec.get("/history")
async def history(user: UserHistory):
    return {"message": "User history retrieved successfully"}

@rec.post("/recommended", response_model=UserRecommendedResponse)
async def recommended(user: UserRecommended):
    recommendation = rec_model.predict(user.user_id, user.title, user.review_score)
    return_val = UserRecommendedResponse(recommendations=recommendation)
    return return_val

@rec.get("/llm")
async def llm(user: UserLLM):
    return {"message": "User LLM recommendations retrieved successfully"}
