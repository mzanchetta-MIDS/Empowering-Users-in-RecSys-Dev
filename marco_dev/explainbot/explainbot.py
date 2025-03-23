import os
from utils import load_model

class ExplainBot:
    def __init__(self, model_name="meta-llama/Llama-2-13b-hf"):
        """
        Initialize ExplainBot and load the model
        """
        self.model_name = model_name
        self.tokenizer, self.model, self.device = load_model(self.model_name)

    def get_response(self, message):
        """
        Generate a response from the model based on the prompt
        """
        try:
            formatted_prompt = f"[INST] {message} [/INST]"
            inputs = self.tokenizer(
                formatted_prompt,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=1024
            ).to(self.device)  # Handle CPU vd GPU

            output = self.model.generate(
                inputs.input_ids,
                attention_mask=inputs.attention_mask,
                max_new_tokens=300,
                temperature=0.3,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )

            response = self.tokenizer.decode(output[0], skip_special_tokens=True)
            return response[len(formatted_prompt):].strip()

        except Exception as e:
            print(f"Error in get_response: {e}")
            return "Error: Unable to generate a response"

    def chat_recommendation_explanation(self, user_data, recommendation):
        """
        Explain why a specific book was recommended based on user data
        """
        try:
            # Extract user data
            instance = user_data['instances'][0]

            user_id = instance['user_id']  # Map back to name if needed
            liked_books = instance.get('liked_books', [])
            disliked_books = instance.get('disliked_books', [])
            liked_genres = instance.get('liked_genres', [])
            disliked_genres = instance.get('disliked_genres', [])
            liked_authors = instance.get('liked_authors', [])
            disliked_authors = instance.get('disliked_authors', [])

            # Extract recommendation info
            book_title = recommendation.get("title", "Unknown Title")
            book_genres = recommendation.get("genres", [])
            book_author = recommendation.get("author", "Unknown Author")

            # System instructions
            content_begin = (
                    "[INST] <<SYS>>\n"
                    "Generate a direct and concise explanation for why a specific book was recommended to the user.\n"
                    "The explanation should strictly focus on connections between the user's data (including reading history and declared preferences) and the recommended book.\n"
                    "Mention relevant likes and dislikes when appropriate.\n"
                    "Avoid pleasantries or filler phrases.\n"
                    "Keep the response under 300 tokens.\n"
                    "\n"
                    "These are examples if the outputs we are expecting:\n"
                    "### Example 1\n"
                    "**User Data:**\n"
                    "- Favorite Genres: Fiction, Classics\n"
                    "- Disliked Genres: Fantasy\n"
                    "- Favorite Authors: F. Scott Fitzgerald, Harper Lee\n"
                    "- Disliked Authors: J.R.R. Tolkien\n"
                    "- Liked Books: The Great Gatsby, To Kill a Mockingbird\n"
                    "- Disliked Books: The Lord of the Rings\n"
                    "\n"
                    "**Recommended Book:** The Catcher in the Rye\n"
                    "- **Reason:** This book was recommended because it aligns with your interest in classics and shares themes with The Great Gatsby and To Kill a Mockingbird.\n"
                    "\n"
                    "### Example 2\n"
                    "**User Data:**\n"
                    "- Favorite Genres: Mystery, Thriller\n"
                    "- Disliked Genres: Romance\n"
                    "- Favorite Authors: Agatha Christie, Arthur Conan Doyle\n"
                    "- Liked Books: The Hound of the Baskervilles, Murder on the Orient Express\n"
                    "- Disliked Books: The Notebook\n"
                    "\n"
                    "**Recommended Book:** Gone Girl\n"
                    "- **Reason:** This book was recommended because it is a psychological thriller with intricate plot twists, similar to your previous reads by Agatha Christie.\n"
                    "\n"
                    "### Example 3 (Collaborative Filtering)\n"
                    "**User Data:**\n"
                    "- Favorite Genres: Science Fiction, Dystopian\n"
                    "- Disliked Genres: Historical Fiction\n"
                    "- Favorite Authors: Isaac Asimov, Philip K. Dick\n"
                    "- Liked Books: 1984, Do Androids Dream of Electric Sheep?\n"
                    "- Disliked Books: The Pillars of the Earth\n"
                    "\n"
                    "**Recommended Book:** The Road\n"
                    "- **Reason:** This book was recommended because readers who enjoyed 1984 and Do Androids Dream of Electric Sheep also highly rated it, even though it is more post-apocalyptic than traditional sci-fi.\n"
                    "\n"
                    "### Example 4 (Collaborative Filtering)\n"
                    "**User Data:**\n"
                    "- Favorite Genres: Fantasy, Adventure\n"
                    "- Disliked Genres: Horror\n"
                    "- Favorite Authors: J.K. Rowling, Brandon Sanderson\n"
                    "- Disliked Authors: Stephen King\n"
                    "- Liked Books: Harry Potter series, Mistborn\n"
                    "- Disliked Books: It\n"
                    "\n"
                    "**Recommended Book:** The Priory of the Orange Tree\n"
                    "- **Reason:** This book was recommended because many readers who enjoyed Mistborn and Harry Potter also loved it for its epic world-building and magic system.\n"
                    "\n"
                    "### Example 5 (Self-Improvement, Content Similarity)\n"
                    "**User Data:**\n"
                    "- Favorite Genres: Non-Fiction, Self-Improvement\n"
                    "- Disliked Genres: Fantasy, Sci-Fi\n"
                    "- Favorite Authors: James Clear, Malcolm Gladwell\n"
                    "- Disliked Authors: J.R.R. Tolkien, George R.R. Martin\n"
                    "- Liked Books: Atomic Habits, Outliers\n"
                    "- Disliked Books: The Hobbit\n"
                    "\n"
                    "**Recommended Book:** The Power of Habit\n"
                    "- **Reason:** This book was recommended because it aligns with your interest in self-improvement and behavioral psychology, similar to Atomic Habits.\n"
                    "\n"
                    "Now, based on the user data provided below, generate a similar explanation.\n"
                    "<</SYS>>\n\n"
                )
            # User Preferences
            content_user_profile = "### User Profile Information:\n"
            content_user_profile += f"- **Favorite Genres:** {', '.join(liked_genres) if liked_genres else 'None'}\n"
            content_user_profile += f"- **Disliked Genres:** {', '.join(disliked_genres) if disliked_genres else 'None'}\n"
            content_user_profile += f"- **Favorite Authors:** {', '.join(liked_authors) if liked_authors else 'None'}\n"
            content_user_profile += f"- **Disliked Authors:** {', '.join(disliked_authors) if disliked_authors else 'None'}\n"
            content_user_profile += f"- **Liked Books:** {', '.join(liked_books) if liked_books else 'None'}\n"
            content_user_profile += f"- **Disliked Books:** {', '.join(disliked_books) if disliked_books else 'None'}\n"

            # Recommended Book
            content_recommendation = f"\n### Recommended Book: {book_title}\n"
            content_recommendation += f"- **Genre(s):** {', '.join(book_genres) if book_genres else 'Unknown'}\n"
            content_recommendation += f"- **Author:** {book_author}\n"

            # Determine recommendation reason
            recommendation_reason = ""

            # 1. Check if book's genres match user's liked genres
            if any(genre in liked_genres for genre in book_genres):
                recommendation_reason += "This book was recommended because it matches your preferred genres. "

            # 2. Check if book's genres match disliked genres
            if any(genre in disliked_genres for genre in book_genres):
                recommendation_reason += "However, it falls under a genre you dislike. "

            # 3. Check if book's author is liked or disliked
            if book_author in liked_authors:
                recommendation_reason += "Additionally, it is written by one of your favorite authors. "
            if book_author in disliked_authors:
                recommendation_reason += "But, the author is among those you disliked before. "

            # 4. General fallback reason
            if not recommendation_reason:
                recommendation_reason = "This book was recommended based on readers with similar interests."

            content_recommendation += f"- **Reason:** {recommendation_reason}\n"

            # Task Instructions
            content_request = (
                "\n### Task: Provide a Direct Explanation\n"
                "Now explain concisely why this book was recommended based on the user's data provided.\n"
                "Mention both liked and disliked aspects if relevant.\n"
                "Keep the response focused, avoiding unnecessary words.\n"
                "Do NOT include greetings, introductions, or phrases like 'Here’s why...' or 'Sure, here is...'.\n"
                "Start directly with the explanation.\n"
                "[/INST]"
            )

            # Combine all content sections
            content = content_begin + content_user_profile + content_recommendation + content_request

            # For testing ###DELETE###
            # print("SEND: ")
            # print(content)

            # Get response
            response = self.get_response(content)

            return response

        except Exception as e:
            print(f"Error in chat_recommendation_explanation: {e}")
            return "Error: Unable to generate a response."
