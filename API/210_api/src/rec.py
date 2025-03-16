### Import the necessary libraries
from pydantic import BaseModel, field_validator
from typing import List, Optional
from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse
# from datetime import datetime
from fastapi.staticfiles import StaticFiles
import requests
import json
# import s3sf
#import boto3


### Import the necessary functions
from src.small_recommend import small_recommend
from src.recommend import recommend

rec = FastAPI()

rec.mount("/static", StaticFiles(directory="src/static"), name="static")
    
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
    
# define the API endpoints

@rec.post("/recommended")#, response_model=UserRecommendedResponse)
async def recommended(user): 
    """Recieve user session data that consists of:
    - User ID
    - Authors
    - Liked books
    - Disliked books
    - Liked authors
    - Disliked authors
    - Like genres
    - Dislike genres
    - Liked ratings
    - Disliked ratings
    and filter information for keeping and removing. 
    
    Return top 10 recommendations by title, author, category and similarity score as a JSON response.

    Args:
        user (json): User session data

    Returns:
        json: Top 10 recommendations by title, author, category and similarity score.
    """
    print(f'User: {user}')
    
    # if no filter is provided, set to empty

    filter = {'keep': {'title': set(), 'authors': set(), 'categories': set()},
        'remove': {'title': set(), 'authors': set(), 'categories': set([])}}

    #user_json=json.loads(user)
    user_json = json.loads(json.loads(user))
    
    print(type(user_json)) # Debugging
    print(f'User JSON: {user_json}') # Debugging
    print(f"User JSON Keys: {user_json['instances'][0].keys()}") # Debugging
    
    # Initialize filter_info dictionary
    filter_info = {}
    # Loop through the keys in the user_json dictionary
    for key in ['keep_title', 'keep_authors', 'keep_categories', 'remove_title', 'remove_authors', 'remove_categories']:
        
        action, col = key.split("_")
        
        if action not in filter_info:
            filter_info[action] = {}
        filter_info[action][col] = set(user_json['instances'][0][key])
        
        user_json["instances"][0].pop(key)
    
    print(f"Filter: {filter_info}")
    print(type(user_json))
    print(f"User Only: {user_json}")
    user_input = json.dumps(user_json)
    # filter = user_json["filter"]
    # print(f'Filter: {filter}')
    #myJSON = json.dumps(user_json)
    
    model_request = requests.post('https://f1bfm11ckf.execute-api.us-east-1.amazonaws.com/dev', json=user_input)

    test = json.loads(model_request.text)
    print(f'Test: {test}')
    tset = json.loads(test["body"])
    print(f'Test: {tset}')
    pred = tset["result"]["predictions"][0]

    recommendation = recommend(pred, filter_info)
    # ### return recommendation
    # # return recommendation
    # ###

    return recommendation

@rec.get("/llm")
async def llm(user: UserLLM):
    return {"message": "User LLM recommendations retrieved successfully"}
