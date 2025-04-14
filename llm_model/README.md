# ExplainBot Code

This repository contains the code and documentation used to build the Large Language Model (LLM) that powers the explainable recommendations behind the app.

## API Setup and Usage

Follow the instructions below to run the ExplainBot API locally and test the recommendation explanation endpoint.

### 1. Clone the Repository

Start by cloning the repository to your local machine:

```bash
git clone <https://github.com/mzanchetta-MIDS/Empowering-Users-in-RecSys-Dev.git>
cd <Empowering-Users-in-RecSys-Dev/llm_model>
```

### 2. Poetry Setup

Install the required dependencies using Poetry. If you don't have Poetry installed, you can follow the [official installation guide](https://pypi.org/project/poetry/).

Once Poetry is installed, run the following command to install the project dependencies:

```bash
poetry install
poetry shell
```

### 3. Launch the API

After setting up Poetry, you can launch the ExplainBot API by running the following command:

```bash
poetry run uvicorn main:app --reload
```
This will start the FastAPI server locally. By default, the server will be available at http://127.0.0.1:8000.

### 4. Test the API Endpoint

To test the API, you can use a tool like Postman or CURL (in a new terminal window) to make a `POST` request to the `/recommendation-explanation/` endpoint.

#### Request Example

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/recommendation-explanation/' \
  -H 'Content-Type: application/json' \
  -d '{
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
  }'
```

#### Example Response
```
    {
    recommended_book: Midnight Pearls

    author: Debbie Viguié
    
    description: Once upon a time in the Kingdom of Aster a strange thing happened. They say the prince married a girl who was not what she appeared and that another girl who saved the kingdom vanished without a trace. Some said it was witchcraft. Some said it was only a legend. For those who knew the truth, it was magic.... Rescued from the sea at an early age, Pearl grew up within sight of the water...and the castle. With her pale skin and silvery hair, she was an outcast in the village. Her only friend was a boy she met on the beach -- a young prince named James, who understood Pearl's desire just to be like everyone else. Their friendship is viewed from afar by many: a disdainful king, Pearl's worried foster parents, a jealous young mermaid, a lovestruck merman, and the powerful sea witch. Now a storm brews in the kingdom, with a tidal force that could keep Pearl and James apart.
    
    explanation: Midnight Pearls was recommended because it is a romantic and unique fairy tale retelling, which may appeal to your interest in fairy tales and folklore. The story revolves around a young woman named Pearl who is rescued from the sea and grows up in a village near a castle, where she forms a close bond with a young prince named James. Their love seems doomed due to their different social stations, but a mysterious stranger appears and changes everything. This book may offer a fresh take on a classic fairy tale and provide an engaging and romantic reading experience.
    }
```

