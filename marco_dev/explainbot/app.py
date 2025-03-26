from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
from explainbot import ExplainBot

app = FastAPI()
explain_bot = ExplainBot()

class RecommendationRequest(BaseModel):
    user_data: Dict[str, Any]
    recommendation: str  # recommended book title

@app.post("/recommendation-explanation/")
async def generate_explanation(request: RecommendationRequest):
    """
    Generate an explanation for why a book was recommended.
    """
    explanation = explain_bot.chat_recommendation_explanation(
        request.user_data, request.recommendation
    )
    return {"recommendation_explanation": explanation}
