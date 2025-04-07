import boto3
import json
import explainbot.utils
from explainbot.utils import fetch_books_data, MODEL_NAME

class ExplainBot:
    def __init__(self, model_name="mistral.mistral-large-2402-v1:0"):
        """
        Initialize the ChatBot with AWS Bedrock
        """
        self.model_name = explainbot.utils.MODEL_NAME

        # Initialize AWS Bedrock client
        self.bedrock_runtime = boto3.client(
            service_name="bedrock-runtime"
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
                top_reviews = book_info["reviews"].values[0]
            else:
                book_author = "Unknown Author"
                book_publish_year = "Unknown Year"
                book_genres = "Unknown Genre"
                book_description = "No description available"
                top_reviews = "No reviews available"

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

                "Please provide a recommendation explanation that focuses on the key aspects of the user’s preferences that align with the recommended book. The explanation should avoid repeating all the genres the user likes if they do not align with the book. Instead, focus on the similarities between the user’s actual interests and the recommended book, as well as any relevant themes, genres, or topics that match the user's profile. Only mention genres, themes, or categories directly related to the book. If the recommendation is based on collaborative filtering or a low similarity score, clarify that the suggestion comes from a broader range of similar users rather than direct content match.\n"

                "### Important Considerations:\n"
                "  - Be mindful of the **context and themes** of the recommended book.\n"
                "  - If the book covers **sensitive topics** (e.g., war, trauma, historical events), ensure that your explanation is **empathetic, respectful, and avoids trivialization**.\n"
                "  - If the book deals with **serious or tragic themes**, acknowledge the gravity of the subject in your response.\n"
                "  - Do **not** include generic statements like 'This is a great book!'—instead, focus on why it aligns with the user’s reading preferences.\n"
                "\n\n"

                "Do **not** include:\n"
                "    - A summary of your response.\n"
                "    - Meta information (e.g., 'This explanation is under 300 tokens').\n"
                "    - Any mention of task constraints.\n"

                "Additionally, you may incorporate insights from the **top reader review** of the recommended book to support the reasoning. The top review is selected based on a combination of review score and helpfulness, and includes:\n"
                "  - **review_text** (reader's written thoughts),\n"
                "  - **review_score** (numerical rating),\n"
                "  - **review_helpfulness** (an indicator of how useful other readers found the review).\n"

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
                  "- **Top Review:** “Holden's frustration with the adult world felt painfully real. The writing is simple but piercing—every word carries weight, and the emotional honesty hit me hard.” (Score: 5, Helpfulness: 91)\n"
                "\n"
                "- **Recommendation Explanation:** *The Age of Innocence* was recommended because it reflects your appreciation for emotionally resonant classics that critique societal norms, much like *The Great Gatsby* and *To Kill a Mockingbird*. Its concise, impactful prose fits your preference for smooth, engaging reads. The top review highlights the novel’s emotional honesty and clarity—qualities that complement your dislike of verbosity and your draw toward meaningful storytelling.\n"
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
                  "- **Top Review:** “Absolutely gripping. The twists kept coming, and just when I thought I had it figured out, everything flipped. A masterclass in unreliable narration and psychological tension.” (Score: 5, Helpfulness: 14)\n"
                "\n"
                "- **Recommendation Explanation:** *Gone Girl* was recommended because it’s a psychological thriller built on clever misdirection and layered tension—hallmarks of the mysteries you love. Like *Murder on the Orient Express*, it keeps you guessing with intricately constructed twists. The top review highlights its expert use of unreliable narration and gripping suspense, aligning perfectly with your preference for stories full of surprise and intellectual challenge.\n"
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
                  "- **Top Review:** “I found this book relentlessly grim and emotionally draining. The sparse writing style didn’t connect with me, and the plot felt too bleak to be meaningful.” (Score: 2, Helpfulness: 89)\n"
                "\n"
                "- **Recommendation Explanation:** *The Road* was recommended because it shares your interest in dystopian fiction that probes moral and existential questions, much like *1984* and *Do Androids Dream of Electric Sheep?*. While the top review critiques its bleak tone and minimalist style, those very elements may resonate with your appreciation for thought-provoking, philosophical storytelling in post-apocalyptic settings.\n"
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
                  "- **Top Review:** 'A bit slow at times, but ultimately rewarding. The world-building is intricate and the characters are complex. It’s more about the political intricacies than the action, which might not appeal to everyone.' (Score: 4, Helpfulness: 91)\n"
                "\n"
                "- **Recommendation Explanation:** *The Priory of the Orange Tree* was recommended based on the principle of collaborative filtering. While it doesn’t directly match your specific preferences for fast-paced, action-heavy fantasy, readers who enjoyed *Mistborn* and *Harry Potter* often appreciated its deep world-building and intricate political plotlines. This recommendation aims to offer a book with rich narrative complexity that might expand your reading horizons and challenge your typical reading style, similar to how other users with similar tastes have enjoyed it despite some differences in genre focus.\n"
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
                  "- **Top Review:** 'A transformative read that breaks down the science of habits in an accessible way. While it's a bit repetitive at times, the practical steps it offers are life-changing.' (Score: 5, Helpfulness: 92)\n"
                "\n"
                "- **Recommendation Explanation:** *The Power of Habit* was recommended because it closely aligns with your interest in self-improvement books like *Atomic Habits*. This book shares similar themes of habit-building and offers practical, real-world advice that matches your preferences for actionable content. It also explores the psychology behind habits, providing additional insights that can complement your existing reading. While the books share a similar focus, this recommendation also considers other readers' preferences, which further strengthens its relevance to your reading goals.\n"
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
            content_recommendation += f"- **Top Review:** {top_reviews}\n"

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
