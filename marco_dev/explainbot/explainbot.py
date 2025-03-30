import boto3
import json
import utils
from utils import fetch_books_data

class ExplainBot:
    def __init__(self, model_name="meta.llama3-1-8b-instruct-v1:0"):
        """
        Initialize the ChatBot with AWS Bedrock
        """
        self.model_name = utils.MODEL_NAME

        # Initialize AWS Bedrock client
        self.bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name="us-east-1",
            aws_access_key_id=utils.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=utils.AWS_SECRET_ACCESS_KEY,
        )
        self.books_df = fetch_books_data()

    def get_response(self, prompt):
        """
        Generate a response from AWS Bedrock
        """
        try:
            payload = {
                "modelId": self.model_name,
                "contentType": "application/json",
                "accept": "application/json",
                "body": json.dumps({
                    "prompt": prompt,
                    "max_tokens": 300,
                    "temperature": 0.3,
                    "top_p": 0.9
                }),
            }

            # invoke model
            response = self.bedrock_runtime.invoke_model(**payload)

            # read response
            response_body = json.loads(response["body"].read())

            # extract text
            completion = response_body.get("outputs", [{}])[0].get("text", "").strip()

            return completion if completion else "Error: Empty response from Bedrock."

        except Exception as e:
            print(f"Error in get_response: {e}")
            return "Error: Unable to generate a response."

    def chat_recommendation_explanation(self, input_data):
        """
        Format the prompt and send it to AWS Bedrock for explanation generation
        """
        try:
            # Extract user data
            instance = input_data['user_data']['instances'][0]

            user_id = instance['user_id']
            liked_books = instance.get('liked_books', {})
            disliked_books = instance.get('disliked_books', {})
            liked_genres = list(instance.get('liked_genres', {}).keys())
            disliked_genres = instance.get('disliked_genres', [])
            liked_authors = instance.get('liked_authors', [])
            disliked_authors = instance.get('disliked_authors', [])
            additional_preferences = instance.get('additional_preferences', '')

            # Retrieve the recommendation details
            recommendation, cosine_similarity = input_data['recommendation'][0]

            # Retrieve book details from books_df
            book_info = self.books_df[self.books_df["title"] == recommendation]
            if not book_info.empty:
                book_author = book_info["author"].values[0]
                book_publish_year = int(book_info["publish_year"].values[0])
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
                "\n\nHuman:"
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
                "- **Additional Preferences:**\n"
                "  - I don't like to read books that are way too verbose. I like smooth, engaging reads.\n"                
                "\n"
                "**Recommended Book:** The Age of Innocence\n"
                  "- **Cosine Similarity:** 0.87\n"  
                  "- **Author:** J.D. Salinger\n"  
                  "- **Publish Year:** 1951\n"
                  "- **Genre:** Classic, Fiction, Coming-of-Age\n"
                  "- **Description:** A novel that follows Holden Caulfield, a disillusioned teenager who struggles with identity, societal expectations, and the phoniness of the adult world.\n"
                "\n"
                "- **Recommendation Explanation:** The Age of Innocence was recommended because it aligns with your interest in classics and shares themes of social critique and moral conflict with The Great Gatsby and To Kill a Mockingbird. Its smooth, engaging prose avoids excessive verbosity, matching your reading preferences.\n"
                "\n---\n"
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
                "- **Additional Preferences:**\n"
                "  - I enjoy books with intricate plots, clever twists, and strong detective work.\n"                
                "\n"
                "**Recommended Book:** Gone Girl\n"
                  "- **Cosine Similarity:** 0.81\n"  
                  "- **Author:** Gillian Flynn\n"  
                  "- **Publish Year:** 2012\n"
                  "- **Genre:** Psychological Thriller, Mystery\n"
                  "- **Description:** A suspenseful novel that follows the mysterious disappearance of Amy Dunne, unraveling secrets, deception, and unreliable narration.\n"
                "\n"
                "- **Recommendation Explanation:** *Gone Girl* was recommended because it is a psychological thriller with intricate plot twists, much like *Murder on the Orient Express*, and shares the suspense-driven storytelling of your previous reads.\n"
                "\n---\n"                
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
                "- **Additional Preferences:**\n"
                "  - I prefer thought-provoking narratives that explore deep philosophical and societal themes.\n"                
                "\n"
                "**Recommended Book:** The Road\n"
                  "- **Cosine Similarity:** 0.26\n"  
                  "- **Author:** Cormac McCarthy\n"  
                  "- **Publish Year:** 2006\n"
                  "- **Genre:** Post-Apocalyptic, Dystopian Fiction\n"
                  "- **Description:** A bleak yet moving story of a father and son struggling for survival in a post-apocalyptic world, grappling with morality and despair.\n"
                "\n"
                "- **Recommendation Explanation:** *The Road* was recommended because it explores dystopian survival themes similar to *1984*, while also reflecting the bleak, introspective storytelling of *Do Androids Dream of Electric Sheep?*.\n"
                "\n---\n" 
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
                "- **Additional Preferences:**\n"
                "  - I prefer thought-provoking narratives that explore deep philosophical and societal themes.\n"                
                "\n"
                "**Recommended Book:** The Priory of the Orange Tree\n"
                  "- **Cosine Similarity:** 0.56\n"  
                  "- **Author:** Samantha Shannon\n"  
                  "- **Publish Year:** 2019\n"
                  "- **Genre:** Fantasy, Adventure, High Fantasy\n"
                  "- **Description:** A sweeping epic featuring powerful queens, dragons, and political intrigue, blending elements of adventure and deep world-building.\n"
                "\n"
                "- **Recommendation Explanation:** *The Priory of the Orange Tree* was recommended because it features epic world-building and a magic system reminiscent of *Mistborn* while delivering strong character-driven storytelling like *Harry Potter*.\n"
                "\n---\n" 
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
                "- **Additional Preferences:**\n"
                "  - I prefer books with practical advice and real-world applications rather than abstract theories.\n"                
                "\n"
                "**Recommended Book:** The Power of Habit\n"
                  "- **Cosine Similarity:** 0.98\n"  
                  "- **Author:** Charles Duhigg\n"  
                  "- **Publish Year:** 2012\n"
                  "- **Genre:** Non-Fiction, Self-Improvement, Psychology\n"
                  "- **Description:** A book exploring the science behind habit formation, providing practical strategies for making lasting behavioral changes.\n"
                "\n"
                "- **Recommendation Explanation:** *The Power of Habit* was recommended because it’s very similar to *Atomic Habits* and matches your interest in self-improvement. The strong similarity between these books shows that *The Power of Habit* also provides practical, real-world advice on building and breaking habits, exactly the kind of content you prefer.\n"
                "\n---\n" 
                "Now, based on the user data provided below, generate a similar explanation.\n"
            )

            # User Preferences
            content_user_profile = "### User Profile Information:\n"
            content_user_profile += f"- **Favorite Genres:** {', '.join(liked_genres) if liked_genres else 'None'}\n"
            content_user_profile += f"- **Disliked Genres:** {', '.join(disliked_genres) if disliked_genres else 'None'}\n"
            content_user_profile += f"- **Favorite Authors:** {', '.join(liked_authors) if liked_authors else 'None'}\n"
            content_user_profile += f"- **Disliked Authors:** {', '.join(disliked_authors) if disliked_authors else 'None'}\n"
            content_user_profile += f"- **Liked Books:**\n{liked_books_str}\n"
            content_user_profile += f"- **Disliked Books:**\n{disliked_books_str}\n"
            content_user_profile += f"- **User's Additional Preferences:** {additional_preferences}\n"

            # Recommended Book
            content_recommendation = f"\n### Recommended Book: {recommendation}\n"
            content_recommendation += f"- **Cosine Similarity:** {cosine_similarity}\n"
            content_recommendation += f"- **Genre:** {book_genres}\n"
            content_recommendation += f"- **Author:** {book_author}\n"
            content_recommendation += f"- **Publish Year:** {book_publish_year}\n"
            content_recommendation += f"- **Description:** {book_description}\n"

            # Task Instructions
            content_request = (
                "\n### Task: Provide a Direct Explanation\n"
                "Now explain concisely why this book was recommended based on the user's data provided.\n"
                "Mention both liked and disliked aspects if relevant. Also consider the user's self-provided additional preferences.\n"
                "Keep the response focused, avoiding unnecessary words.\n"
                "Do NOT include greetings, introductions, or phrases like 'Here’s why...' or 'Sure, here is...'.\n"
                "Start directly with the explanation, speaking directly to the user.\n\n"
                "The response **MUST BE UNDER 300 TOKENS**.\n\n"
                "Assistant:"
            )

            # Combine all content sections
            content = content_begin + content_user_profile + content_recommendation + content_request

            # Generate explanation
            explanation_text = self.get_response(content).strip()

            # Create JSON response
            response_json = {
                "recommended_book": recommendation,
                "author": book_author,
                "description": book_description,
                "explanation": explanation_text
            }

            return response_json

        except Exception as e:
            print(f"Error in chat_recommendation_explanation: {e}")
            return "Error: Unable to generate a response."
