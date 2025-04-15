from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

app.mount("/")

# """ 
# 1 - register new user
# 2 - login
# 2 - update user
# 4 - recovery
# 5 - delete user
# 6 - history
# 7 - recommended
# 8 - LLM recommendations
# 9 - Recommendation filters
# 10 - cookies
# 11 - reviews

# Wish list:
# 12 - social aspects
#  - friend request
#  - friend list
#  - connect to socials
# 13 - translation
# 14 - Reinforcement learning
# 15 - e-commerce (buy the book and read)
#  - storage of books
#  - payment (security)
# 16 - Connector API (google books, amazon)
# """
 