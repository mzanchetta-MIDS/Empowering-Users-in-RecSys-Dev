from explainbot import ExplainBot

# Initialize the model
explain_bot = ExplainBot()

# Create test data
user_data = {
    "user_id": "12345",
    "liked_books": ["The Great Gatsby", "To Kill a Mockingbird"],
    "disliked_books": ["The Hobbit"],
    "liked_genres": ["Fiction", "Classics"],
    "disliked_genres": ["Fantasy"],
    "liked_authors": ["F. Scott Fitzgerald", "Harper Lee"],
    "disliked_authors": ["J.R.R. Tolkien"],
    "liked_ratings": [5, 4],
    "disliked_ratings": [1]
}

# Recommendation
recommendation = {
    "title": "The Catcher in the Rye",
    "genres": ["Classics", "Fiction"],
    "author": "J.D. Salinger"
}

# Generate explanation
explanation = explain_bot.chat_recommendation_explanation(user_data, recommendation)

print("\nRecommendation Explanation:")
print(explanation)
