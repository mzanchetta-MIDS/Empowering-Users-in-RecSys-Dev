from explainbot import ExplainBot

# Initialize the model
explain_bot = ExplainBot()

# Create test data
user_data = {
    "instances": [
        {
            "user_id": "12345",
            "liked_books": {
                "The Great Gatsby": 5,
                "To Kill a Mockingbird": 4
            },
            "disliked_books": {
                "The Hobbit": 1
            },
            "liked_genres": {
                "Fiction": 1.0,
                "Classics": 1.0
            },
            "disliked_genres": [
                "Fantasy"
            ],
            "liked_authors": [
                "F. Scott Fitzgerald",
                "Harper Lee"
            ],
            "disliked_authors": [
                "J.R.R. Tolkien"
            ],
            "additional_preferences": "",
            "authors": 0,
            "categories": 0,
            "description": 0,
            "target_book": 0,
            "target_book_rating": 0
        }
    ]
}

# Recommendation
recommendation = ['Catcher in the rye : notes']

# Generate explanation
explanation = explain_bot.chat_recommendation_explanation(user_data, recommendation)

print("\nRecommendation Explanation:")
print(explanation)
