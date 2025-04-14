from explainbot import ExplainBot

# Initialize the model
explain_bot = ExplainBot()

# Create test data
input_data = {
    "user_data": {
      "instances": [
        {
          "user_id": "1001",
          "liked_books": {
            "420 handcrafts illustrated in simple steps": {
              "title": "420 handcrafts illustrated in simple steps",
              "author": "Gloria Foreman",
              "genre": "Juvenile Nonfiction / General",
              "rating": 5
            },
            "Arnhem": {
              "title": "Arnhem",
              "author": "Antony Beevor",
              "genre": "History / Military",
              "rating": 4
            },
            "Caesar: The Life of a Panda Leopard": {
              "title": "Caesar: The Life of a Panda Leopard",
              "author": "Patrick OBrian",
              "genre": "Fiction / Fairy Tales, Folk Tales, Legends & Mythology",
              "rating": 4
            }
          },
          "disliked_books": {
            "The Silmarillion": {
              "title": "The Silmarillion",
              "author": "J. R. R. Tolkien",
              "genre": "Fiction / Fairy Tales, Folk Tales, Legends & Mythology",
              "rating": 2
            },
            "Gift From the Sea - An Answer to the Conflicts in Our Lives": {
              "title": "Gift From the Sea - An Answer to the Conflicts in Our Lives",
              "author": "Candace Fleming",
              "genre": "Young Adult Nonfiction / General",
              "rating": 1
            }
          },
          "liked_genres": {
            "Antiques & Collectibles / General": "keep",
            "Bibles / General": "keep"
          },
          "disliked_genres": [
            "Biography & Autobiography / Literary Figures"
          ],
          "liked_authors": [
            "Aajonus Vonderplanitz"
          ],
          "disliked_authors": [],
          "additional_preferences": "I prefer books with grounded, imaginative storytelling. I enjoy history, craft, and myth-based fiction, but I don’t like overly abstract narratives or spiritual self-help themes.",
          "authors": 0,
          "categories": 0,
          "description": 0,
          "target_book": 0,
          "target_book_rating": 0
        }
      ]
    },
    "recommendation": [
      ["Midnight Pearls", 0.5]
    ]
  }

# Generate explanation
explanation = explain_bot.chat_recommendation_explanation(input_data)

print("\nRecommendation Explanation:")
print(explanation)
