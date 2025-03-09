from pydantic import BaseModel, field_validator
from typing import List, Optional
from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse
from datetime import datetime
from fastapi.staticfiles import StaticFiles
import joblib
import requests
import numpy as np
from datetime import datetime
import json


#from recommend import recommend
from src.small_recommend import small_recommend

# load the rec model
#rec_model = joblib.load('rec_model.pkl')

# load the LLM model
#llm_model = joblib.load('llm_model.pkl')

rec = FastAPI()

rec.mount("/static", StaticFiles(directory="src/static"), name="static")

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
    
# class UserRecommended(BaseModel):
#     user: JSONResponse
    
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
#@rec.post("/recommended", response_model=UserRecommendedResponse)
async def recommended(user): # Need to figure out the input type :UserRecommended
    # Load unique_titles and book_embeddings to pass to small_recommend function
    # unique_titles = np.load('data/unique_titles.npy', allow_pickle=True)
    # book_embeddings = np.load("data/book_embeddings.npy", allow_pickle=True)
    
    # Make request to API Gateway

    user_json = json.loads(user)
    #myJSON = json.dumps(user_json)
    
    model_request = requests.post('https://f1bfm11ckf.execute-api.us-east-1.amazonaws.com/dev', json=user_json)
    test = json.loads(model_request.text)
    tset = json.loads(test["body"])
    pred = tset["result"]["predictions"][0][0]
    # print(model_request.text)
    # return_value = json.loads(model_request.text)
    ### Big model: pass model reqeust to recommend function
    # recommendation = recommend(model_request, filter)
    ### return recommendation
    # return recommendation
    ###
    
    ### Small model: pass model_request to small_recommend function
    recommendations = small_recommend(pred)
    return_val = UserRecommendedResponse(recommendations=recommendations)

    return return_val
    #return return_val

@rec.get("/llm")
async def llm(user: UserLLM):
    return {"message": "User LLM recommendations retrieved successfully"}
