from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
from explainbot import ExplainBot

app = FastAPI()
explain_bot = ExplainBot()

class RecommendationRequest(BaseModel):
    input_data: Dict[str, Any]

@app.post("/recommendation-explanation/")
async def generate_explanation(request: RecommendationRequest):
    """
    Generate an explanation for why a book was recommended.
    """
    input_data = request.input_data
    explanation = explain_bot.chat_recommendation_explanation(input_data)

    return {"recommendation_explanation": explanation}
