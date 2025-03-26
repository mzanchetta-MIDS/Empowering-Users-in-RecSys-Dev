from utils import load_model, fetch_books_data

class ExplainBot:
    def __init__(self, model_name="meta-llama/Llama-3.1-8B-Instruct"):
        """
        Initialize ExplainBot and load the model
        """
        self.model_name = model_name
        self.tokenizer, self.model, self.device = load_model(self.model_name)
        self.books_df = fetch_books_data()

    def get_response(self, message):
        """
        Generate a response from the model based on the given prompt.
        """
        try:
            formatted_prompt = f"[INST] {message} [/INST]"
            inputs = self.tokenizer(
                formatted_prompt,
                return_tensors="pt",
                # padding=True,
                # truncation=True,
                # max_length=1024
            ).to("cuda")

            output = self.model.generate(
                inputs.input_ids,
                attention_mask=inputs.attention_mask,
                max_new_tokens=300,
                temperature=0.3,
                top_p=0.9,
                # do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )

            response = self.tokenizer.decode(output[0], skip_special_tokens=True)

            # Remove input prompt from response if echoed
            if formatted_prompt in response:
                response = response.replace(formatted_prompt, "").strip()
            return response

        except Exception as e:
            print(f"Error in get_response: {e}")
            return "Error: Unable to generate a response."

    def chat_recommendation_explanation(self, user_data, recommendation):
        """
        Explain why a specific book was recommended based on user data
        """
        try:
            # Extract user data
            instance = user_data['instances'][0]

            user_id = instance['user_id']  # Map back to name if needed
            liked_books = instance.get('liked_books', {})
            disliked_books = instance.get('disliked_books', {})
            liked_genres = list(instance.get('liked_genres', {}).keys())
            disliked_genres = instance.get('disliked_genres', [])
            liked_authors = instance.get('liked_authors', [])
            disliked_authors = instance.get('disliked_authors', [])

            # Retrieve rec details
            book_info = self.books_df[self.books_df["title"] == recommendation]
            if not book_info.empty:
                book_author = book_info["author"].values[0]
                book_publish_year = int(book_info["publish_year"].values[0])  # Ensure it's an integer
                book_genres = book_info["genre_consolidated"].values[0]
                book_description = book_info["description"].values[0]
            else:
                book_author = "Unknown Author"
                book_publish_year = "Unknown Year"
                book_genres = "Unknown Genre"
                book_description = "No description available"

            # Retrieve info for liked books
            liked_books_info = self.books_df[self.books_df["title"].isin(liked_books.keys())]
            liked_books_descriptions = {
                row["title"]: row["description"] for _, row in liked_books_info.iterrows()
            }

            # Retrieve info for disliked books
            disliked_books_info = self.books_df[self.books_df["title"].isin(disliked_books.keys())]
            disliked_books_descriptions = {
                row["title"]: row["description"] for _, row in disliked_books_info.iterrows()
            }

            # Format liked books with descriptions
            liked_books_str = "\n".join(
                f"- {title} (Rated {liked_books[title]}): {liked_books_descriptions.get(title, 'No description available')}"
                for title in liked_books
            ) if liked_books else "None"

            # Format disliked books with descriptions
            disliked_books_str = "\n".join(
                f"- {title} (Rated {disliked_books[title]}): {disliked_books_descriptions.get(title, 'No description available')}"
                for title in disliked_books
            ) if disliked_books else "None"

            # System instructions
            content_begin = (
                #"[INST] <<SYS>>\n" #only for Llama 2
                "You are a book reading analyst. Your job is to generate a direct and concise explanation for why a specific book was recommended to the user.\n"
                "The explanation should strictly focus on connections between the user's data (including reading history, declared preferences, and book descriptions) and the recommended book.\n"
                "Do **not** include:\n"
                "    - A summary of your response.\n"
                "    - Meta information (e.g., 'This explanation is under 300 tokens').\n"
                "    - Any mention of task constraints.\n"

                "**Provide ONLY the explanation itself**.\n"

                "The response **MUST BE UNDER 300 TOKENS**.\n\n"

                "\n"

                "These are examples of the outputs we expect:\n"
                "\n"
                "### Example 1\n"
                "**User Data:**\n"
                "- **Favorite Genres:** Fiction, Classics\n"
                "- **Disliked Genres:** Fantasy\n"
                "- **Favorite Authors:** F. Scott Fitzgerald, Harper Lee\n"
                "- **Disliked Authors:** J.R.R. Tolkien\n"
                "- **Liked Books:**\n"
                "  - The Great Gatsby (Rated 5): A novel about wealth, love, and the disillusionment of the American Dream.\n"
                "  - To Kill a Mockingbird (Rated 4): A powerful story about race, morality, and justice in the Deep South.\n"
                "- **Disliked Books:**\n"
                "  - The Lord of the Rings (Rated 2): A high-fantasy epic with extensive world-building and mythical storytelling.\n"
                "\n"
                "**Recommended Book:** The Catcher in the Rye\n"
                "- **Reason:** This book was recommended because it aligns with your interest in classics and shares themes of societal critique and introspection with *The Great Gatsby* and *To Kill a Mockingbird*.\n"
                "\n"
                "### Example 2\n"
                "**User Data:**\n"
                "- **Favorite Genres:** Mystery, Thriller\n"
                "- **Disliked Genres:** Romance\n"
                "- **Favorite Authors:** Agatha Christie, Arthur Conan Doyle\n"
                "- **Liked Books:**\n"
                "  - The Hound of the Baskervilles (Rated 5): A Sherlock Holmes mystery involving a supernatural legend and deductive reasoning.\n"
                "  - Murder on the Orient Express (Rated 5): A classic Agatha Christie whodunit featuring Hercule Poirot.\n"
                "- **Disliked Books:**\n"
                "  - The Notebook (Rated 1): A sentimental love story centered on rekindled romance.\n"
                "\n"
                "**Recommended Book:** Gone Girl\n"
                "- **Reason:** This book was recommended because it is a psychological thriller with intricate plot twists, much like *Murder on the Orient Express*, and shares the suspense-driven storytelling of your previous reads.\n"
                "\n"
                "### Example 3 (Collaborative Filtering)\n"
                "**User Data:**\n"
                "- **Favorite Genres:** Science Fiction, Dystopian\n"
                "- **Disliked Genres:** Historical Fiction\n"
                "- **Favorite Authors:** Isaac Asimov, Philip K. Dick\n"
                "- **Liked Books:**\n"
                "  - 1984 (Rated 5): A dystopian novel exploring totalitarianism, surveillance, and free will.\n"
                "  - Do Androids Dream of Electric Sheep? (Rated 4): A sci-fi classic questioning the nature of humanity and artificial intelligence.\n"
                "- **Disliked Books:**\n"
                "  - The Pillars of the Earth (Rated 2): A historical epic centered on medieval cathedral-building and political intrigue.\n"
                "\n"
                "**Recommended Book:** The Road\n"
                "- **Reason:** This book was recommended because it explores dystopian survival themes similar to *1984*, while also reflecting the bleak, introspective storytelling of *Do Androids Dream of Electric Sheep?*.\n"
                "\n"
                "### Example 4 (Fantasy Fans, Content Similarity)\n"
                "**User Data:**\n"
                "- **Favorite Genres:** Fantasy, Adventure\n"
                "- **Disliked Genres:** Horror\n"
                "- **Favorite Authors:** J.K. Rowling, Brandon Sanderson\n"
                "- **Liked Books:**\n"
                "  - Harry Potter series (Rated 5): A coming-of-age fantasy about magic, friendship, and heroism.\n"
                "  - Mistborn (Rated 5): A high-fantasy novel with a unique magic system and political intrigue.\n"
                "- **Disliked Books:**\n"
                "  - It (Rated 1): A horror novel featuring supernatural terror and psychological fear elements.\n"
                "\n"
                "**Recommended Book:** The Priory of the Orange Tree\n"
                "- **Reason:** This book was recommended because it features epic world-building and a magic system reminiscent of *Mistborn* while delivering strong character-driven storytelling like *Harry Potter*.\n"
                "\n"
                "### Example 5 (Self-Improvement, Content Similarity)\n"
                "**User Data:**\n"
                "- **Favorite Genres:** Non-Fiction, Self-Improvement\n"
                "- **Disliked Genres:** Fantasy, Sci-Fi\n"
                "- **Favorite Authors:** James Clear, Malcolm Gladwell\n"
                "- **Liked Books:**\n"
                "  - Atomic Habits (Rated 5): A practical guide to building good habits and breaking bad ones.\n"
                "  - Outliers (Rated 4): A study on success and the factors that contribute to high achievement.\n"
                "- **Disliked Books:**\n"
                "  - The Hobbit (Rated 1): A high-fantasy adventure about a reluctant hero and a dragon quest.\n"
                "\n"
                "**Recommended Book:** The Power of Habit\n"
                "- **Reason:** This book was recommended because it aligns with your interest in self-improvement and behavioral psychology, much like *Atomic Habits*, providing actionable strategies for habit formation.\n"
                "\n"
                "Now, based on the user data provided below, generate a similar explanation.\n"
                #"<</SYS>>\n\n" # Only for Llama 2
            )

            # User Preferences
            content_user_profile = "### User Profile Information:\n"
            content_user_profile += f"- **Favorite Genres:** {', '.join(liked_genres) if liked_genres else 'None'}\n"
            content_user_profile += f"- **Disliked Genres:** {', '.join(disliked_genres) if disliked_genres else 'None'}\n"
            content_user_profile += f"- **Favorite Authors:** {', '.join(liked_authors) if liked_authors else 'None'}\n"
            content_user_profile += f"- **Disliked Authors:** {', '.join(disliked_authors) if disliked_authors else 'None'}\n"
            content_user_profile += f"- **Liked Books:**\n{liked_books_str}\n"
            content_user_profile += f"- **Disliked Books:**\n{disliked_books_str}\n"

            # Recommended Book
            content_recommendation = f"\n### Recommended Book: {recommendation}\n"
            content_recommendation += f"- **Genre:** {book_genres}\n"
            content_recommendation += f"- **Author:** {book_author}\n"
            content_recommendation += f"- **Publish Year:** {book_publish_year}\n"
            content_recommendation += f"- **Description:** {book_description}\n"

            # Task Instructions
            content_request = (
                "\n### Task: Provide a Direct Explanation\n"
                "Now explain concisely why this book was recommended based on the user's data provided.\n"
                "Mention both liked and disliked aspects if relevant.\n"
                "Keep the response focused, avoiding unnecessary words.\n"
                "Do NOT include greetings, introductions, or phrases like 'Here’s why...' or 'Sure, here is...'.\n"
                "Start directly with the explanation, speaking directly to the user.\n\n"
                "The response **MUST BE UNDER 300 TOKENS**.\n\n"
                "### Response:\n"
                # "[/INST]" # only for Llama 2
            )

            # Combine all content sections
            content = content_begin + content_user_profile + content_recommendation + content_request

            # For debugging (remove in production)
            print("SEND: ")
            print(content)

            # Get response
            response = self.get_response(content)
            clean_response = response.split("[INST]")[0].split("[/INST]")[0].strip()

            return clean_response

        except Exception as e:
            print(f"Error in chat_recommendation_explanation: {e}")
            return "Error: Unable to generate a response."
