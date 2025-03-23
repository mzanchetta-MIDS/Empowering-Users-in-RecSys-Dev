from fastapi import FastAPI
from pydantic import BaseModel
from explainbot import ExplainBot
from typing import Dict, Any

# Initialize FastAPI app
app = FastAPI()

# Initialize bot
model_name = "meta-llama/Llama-2-13b-hf"
explain_bot = ExplainBot(model_name=model_name)

# Pydantic model
class RecommendationExplanationRequest(BaseModel):
    user_data: Dict[str, Any]  # User data
    recommendation: Dict[str, Any]  # Recommended book

# Endpoint: Explain a recommendation
@app.post("/recommendation-explanation/")
async def generate_recommendation_explanation(request: RecommendationExplanationRequest):
    """
    Generate an explanation for why a specific book was recommended to the user
    """
    explanation = explain_bot.chat_recommendation_explanation(
        request.user_data, request.recommendation
    )
    return {"recommendation_explanation": explanation}
