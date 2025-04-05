from pydantic import BaseModel
from fastapi import FastAPI
from typing import List, Dict, Any, Optional
import logging
import time 
import requests
from contextlib import asynccontextmanager
import json


# Import only the necessary functions
from src.db_utils import get_unique_genres, get_unique_authors, get_unique_books, get_book_covers_lookup


global conn

@asynccontextmanager
async def lifespan_context_manager(app: FastAPI):
    """
    Context manager to handle lifespan events for the FastAPI application.
    """
    print("Starting up...")
    host_name = "booksdataclean.cu9jy7bp7ol8.us-east-1.rds.amazonaws.com"
    dbname = 'booksfull'
    port = '5432'
    username = 'postgres'
    password = 'S3EW5y9MhZzBBYXlCjE6'
    
    global conn
    global curr 
    
    conn = connect_to_db(host_name, dbname, port, username, password)
    curr = conn.cursor()
    
    # Yield control back to the FastAPI application
    yield
    # Cleanup code
    curr.close()
    conn.close()
    logging.info("Database connection closed")
    
rec = FastAPI()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GenreResponse(BaseModel):
    genres: List[str]

class AuthorResponse(BaseModel):
    authors: List[str]

class BookResponse(BaseModel):
    books: List[str]


class BookMetadata(BaseModel):
    title: str
    author: str
    genre: str
    rating: Optional[int] = None

class UserProfile(BaseModel):
    name: Optional[str] = None
    genres: Optional[List[str]] = None
    authors: Optional[List[str]] = None
    favorite_books: Optional[List[str]] = None
    additional_preferences: Optional[str] = None
    ratings: Optional[Dict[str, int]] = None
    not_interested: Optional[List[str]] = None
    saved_for_later: Optional[List[Dict[str, Any]]] = None

class RecommendationResponse(BaseModel):
    recommendations: List[Dict[str, Any]]

# New model for recommendation model input format
class RecModelInstance(BaseModel):
    user_id: str
    liked_books: Dict[str, BookMetadata]
    disliked_books: Dict[str, BookMetadata]
    liked_genres: Dict[str, str]
    disliked_genres: List[str]
    liked_authors: List[str]
    disliked_authors: List[str]
    additional_preferences: Optional[str] = None 
    books_history: List[BookMetadata]
    authors: int
    categories: int
    description: int
    target_book: int
    target_book_rating: int

class RecModelRequest(BaseModel):
    instances: List[RecModelInstance]

class ProfileInput(BaseModel):
    profile: str

@rec.get("/genres", response_model=GenreResponse)
async def get_genres_endpoint():
    """
    Get available book genres from the database
    """
    try:
        genres = get_unique_genres()
        if not genres:
            # Fallback to hardcoded genres if database query fails
            logger.warning("Using fallback hardcoded genres due to empty result from database")
            genres = ['Fiction', 'Non-Fiction', 'Mystery', 'Fantasy',
                      'Science Fiction', 'Romance', 'History']
        return {"genres": genres}
    except Exception as e:
        logger.error(f"Error in get_genres_endpoint: {str(e)}")
        # Fallback to hardcoded genres
        genres = ['Fiction', 'Non-Fiction', 'Mystery', 'Fantasy',
                  'Science Fiction', 'Romance', 'History']
        return {"genres": genres}

@rec.get("/authors", response_model=AuthorResponse)
async def get_authors_endpoint():
    """
    Get available book authors from the database
    """
    try:
        authors = get_unique_authors()
        if not authors:
            # Fallback to hardcoded authors if database query fails
            logger.warning("Using fallback hardcoded authors due to empty result from database")
            authors = ['J.K. Rowling', 'Stephen King', 'Jane Austen',
                      'Agatha Christie', 'Neil Gaiman', 'George R.R. Martin']
        return {"authors": authors}
    except Exception as e:
        logger.error(f"Error in get_authors_endpoint: {str(e)}")
        # Fallback to hardcoded authors
        authors = ['J.K. Rowling', 'Stephen King', 'Jane Austen',
                  'Agatha Christie', 'Neil Gaiman', 'George R.R. Martin']
        return {"authors": authors}

# @rec.get("/books", response_model=BookResponse)
# async def get_books_endpoint():
#     """
#     Get available books from the database
#     """
#     try:
#         books = get_unique_books()
#         if not books:
#             # Fallback to hardcoded books if database query fails
#             logger.warning("Using fallback hardcoded books due to empty result from database")
#             books = [
#                 "To Kill a Mockingbird - Harper Lee",
#                 "1984 - George Orwell",
#                 "Pride and Prejudice - Jane Austen"
#             ]
#         return {"books": books}
#     except Exception as e:
#         logger.error(f"Error in get_books_endpoint: {str(e)}")
#         # Fallback to hardcoded books
#         books = [
#             "To Kill a Mockingbird - Harper Lee",
#             "1984 - George Orwell",
#             "Pride and Prejudice - Jane Austen"
#         ]
#         return {"books": books}

@rec.get("/books")
async def get_books_endpoint():
  """
  Get available books from the database
  """
  try:
      books_df = get_unique_books()
      if books_df.empty:
          return {"books": []}
          
      # Create display format for UI
      books_display = [f"{row['title']} - {row['author']}" for _, row in books_df.iterrows()]
      
      # Include the full metadata
      books_metadata = books_df.to_dict(orient='records')
      
      return {
          "books": books_display,
          "metadata": books_metadata
      }
  except Exception as e:
      logger.error(f"Error in get_books_endpoint: {str(e)}")
      return {"books": [], "metadata": []}


@rec.get("/book-covers")
async def get_book_covers_endpoint():
    """
    Get available book covers from the database
    """
    try:
        covers_df = get_book_covers_lookup()
        if covers_df.empty:
            logger.warning("No book covers found in database")
            return {"covers": []}
        covers = covers_df.to_dict(orient='records')
        return {"covers": covers}
    except Exception as e:
        logger.error(f"Error in get_book_covers_endpoint: {str(e)}")
        return {"covers": []}

        
@rec.post("/users/profile")
async def update_user_profile(data: RecModelRequest):
    print("\n----- RECEIVED PROFILE UPDATE IN NEW FORMAT -----")
    print(data.model_dump_json(indent=2))
    print("-----------------------------------\n")
    return {"message": "Profile updated successfully"}


@rec.post("/recommendations")
async def get_recommendations(profile):
    """Recieve user profile from StreamLit and return recommendations with explanations
    based on the profile.
    This function constructs a recommendation request and sends it to the recommendation API.
    The response is then processed and returned in a structured format.
    The function also handles the conversion of the profile data into the required format
    for the recommendation API.
    The function is designed to be called as an API endpoint.

    Args:
        profile (JSON): User profile data in JSON format.
        The profile should contain information about the user's liked and disliked books,
        genres, authors, and ratings.
        The profile is expected to be a JSON string that can be parsed into a dictionary.
        The function also handles the conversion of the profile data into the required format
        for the recommendation API.
        Example:
        {
            "instances": [
                {
                "user_id": "d908b176-6113-4f20-ace2-782f658eb659",
                "liked_books": {
                    "Moneyball": 5,
                    "The Brief Wondrous Life of Oscar Wao": 4,
                    "The Master and Margarita": 4,
                    "A Tale for the Time Being": 4
                },
                "disliked_books": {
                    "Pachinko": 2,
                    "The Wind-Up Bird Chronicle": 1,
                    "The Unbearable Lightness of Being": 1
                },
                "liked_genres": {
                    "Architecture": 1.0,
                    "Biography & Autobiography": 1.0
                },
                "disliked_genres": [
                    "Art"
                ],
                "liked_authors": [
                    "Jane Austen",
                    "Neil Gaiman"
                ],
                "disliked_authors": [],
                "additional_preferences": "Test",
                "authors": 0,
                "categories": 0,
                "description": 0,
                "target_book": 0,
                "target_book_rating": 0
                }
            ]
        }
        
        {
            "instances": [
                                {
                                "user_id": "9df3f814-5e9c-42b9-9e87-9411809154c6",
                                "liked_books": {
                                    "Einstein: A Life": 5,
                                    "George Washington": 5
                                },
                                "disliked_books": {},
                                "liked_genres": {
                                    "Biography & Autobiography / General": "keep",
                                    "Biography & Autobiography / Literary Figures": "keep",
                                    "Biography & Autobiography / Personal Memoirs": "keep"
                                },
                                "disliked_genres": [
                                    "Art / General"
                                ],
                                "liked_authors": [
                                    "Walter Isaacson"
                                ],
                                "disliked_authors": [],
                                "additional_preferences": "I like to read biographies.",
                                "books_history": [
                                    "Einstein: A Life",
                                    "The Master and Margarita",
                                    "George Washington"
                                ],
                                "authors": 0,
                                "categories": 0,
                                "description": 0,
                                "target_book": 0,
                                "target_book_rating": 0
                                }
                        ]
        }
        
        "{'instances': [{'user_id': '0f6b0f4c-c58b-4ecb-b999-79ff8d5c6de4', 'liked_books': {'50 Years of the Desert Boneyard: Davis Monthan A.F.B. Arizona': 5}, 'disliked_books': {}, 'liked_genres': {'Biography & Autobiography / General': 'keep', 'Drama / General': 'keep'}, 'disliked_genres': ['Antiques & Collectibles / General'], 'liked_authors': ['Agatha Christie', 'R.A. Salvatore'], 'disliked_authors': [], 'additional_preferences': 'I like fantasy', 'books_history': ['50 Years of the Desert Boneyard: Davis Monthan A.F.B. Arizona'], 'authors': 0, 'categories': 0, 'description': 0, 'target_book': 0, 'target_book_rating': 0}]}"
        
    Returns:
        _type_: Returns a JSON object containing the recommendations and explanations.
        The recommendations are based on the user's profile and are structured in a way
        that allows for easy consumption by the frontend application.
        Example:
        {
            "recommendations": [
                {
                    "id": "book-001",
                    "title": "The Master and Margarita",
                    "author": "Mikhail Bulgakov",
                    "description": "A 50th-anniversary Deluxe Edition of the incomparable 20th-century masterpiece of satire and fantasy. "
                    " One spring afternoon, the Devil, trailing fire and chaos in his wake, weaves himself out of the "
                    "shadows and into Moscow. This fantastical, funny, and devastating satire of Soviet life combines two distinct yet "
                    "interwoven parts, one set in contemporary Moscow, the other in ancient Jerusalem, each brimming with historical, imaginary, frightful, "
                    "and wonderful characters. Written during the darkest days of Stalin's reign, The Master and Margarita "
                    "became a literary phenomenon, signaling artistic and spiritual freedom for Russians everywhere.",
                    "explanation": "This recommendation bridges your love of magical realism from García Márquez with "
                                "the philosophical depth you enjoy in Rushdie's work. The novel's non-linear structure "
                                "and blend of fantasy with harsh reality mirrors elements you appreciated in 'One "
                                "Hundred Years of Solitude' while introducing you to a different cultural context. " 
                                "Based on your preference for 'books that blur the line between reality and fantasy,' "
                                "this Russian classic should resonate deeply."
                }
            ]
        }
    """ 
    
    print(f"Received profile: {profile}\n")
    print(f"Profile Type: {type(profile)}\n")
    
    start_time = time.time()
    
    try:
        profile = json.loads(json.loads(profile))
    except json.JSONDecodeError as e:
        pass
    
    
    HT = {"liked_books":[],
          "disliked_books":[],
          "liked_genres":[],
          "disliked_genres":[],
          "liked_authors":[],
          "disliked_authors":[],
          "liked_ratings":[], 
          "disliked_ratings":[],
          "books_history":[],
          "keep_authors":[],
          "remove_authors":[],
          "keep_genres":[],
          "remove_genres":[]}
    
    #{"instances": [{
    # "user_id": "9df3f814-5e9c-42b9-9e87-9411809154c6",
    # "liked_books": {"Einstein: A Life": {"title": "Einstein: A Life","author": "placeholder_author_1","genre": "placeholder_genre_1","rating": 5},
    # "George Washington": {"title": "George Washington","author": "placeholder_author_2","genre": "placeholder_genre_2","rating": 5}},
    # "disliked_books": {"Diary of a Whimpy Kid": {"title": "Diary of a Whimpy Kid","author": "Greg Heffley","genre": "Juvenile Comedy","rating": 2}},
    # "liked_genres": {"Biography & Autobiography / General": "keep","Biography & Autobiography / Literary Figures": "keep","Biography & Autobiography / Personal Memoirs": "keep"},
    # "disliked_genres": ["Art / General"],
    # "liked_authors": ["Walter Isaacson"],
    # "disliked_authors": [],
    # "additional_preferences": "I like to read biographies.",
    # "books_history": [{"title": "Einstein: A Life","author": "placeholder_author_1","genre": "placeholder_genre_1"},
    # {"title": "The Master and Margarita","author": "placeholder_author_3","genre": "placeholder_genre_3"},
    # {"title": "George Washington","author": "placeholder_author_2","genre": "placeholder_genre_2"},
    # {"title": "Diary of a Whimpy Kid","author": "Greg Heffley","genre": "Juvenile Comedy"}],
    # "authors": 0,"categories": 0,"description": 0,"target_book": 0,"target_book_rating": 0}]}
    
     # Task: Populate the HT correctly
    
    for key in profile['instances'][0].keys():
        
        if key in HT:
            
            if key == "books_history":
                
                for book_read in profile['instances'][0][key]:
                    
                    HT[key].append(book_read['title'])
                
                continue
            
            favor, topic = key.split("_")
            
            if topic == "books":
        
                if favor == "liked":
                    
                    for liked_book in profile['instances'][0][key]:
                        HT['liked_books'].append(profile['instances'][0][key][liked_book]['title'])
                        HT['liked_authors'].append(profile['instances'][0][key][liked_book]['author'])
                        HT['liked_genres'].append(profile['instances'][0][key][liked_book]['genre'])
                        HT['liked_ratings'].append(profile['instances'][0][key][liked_book]['rating'])
                    
                    
                elif favor == "disliked":
                    
                    for liked_book in profile['instances'][0][key]:
                        HT['disliked_books'].append(profile['instances'][0][key][liked_book]['title'])
                        HT['disliked_authors'].append(profile['instances'][0][key][liked_book]['author'])
                        HT['disliked_genres'].append(profile['instances'][0][key][liked_book]['genre'])
                        HT['disliked_ratings'].append(profile['instances'][0][key][liked_book]['rating'])
                        
                continue
            
        #     HT = {
        #   "liked_genres":[],
        #   "disliked_genres":[],
        #   "liked_authors":[],
        #   "disliked_authors":[]}
        
        # "liked_genres": {"Biography & Autobiography / General": "keep","Biography & Autobiography / Literary Figures": "keep","Biography & Autobiography / Personal Memoirs": "keep"},
        # "disliked_genres": ["Art / General"],
        # "liked_authors": ["Walter Isaacson"],
        # "disliked_authors": [],
       
            if topic == "genres":
                
                if favor == "liked":
                    
                    for genre in profile['instances'][0][key]:
                        
                        if profile['instances'][0][key][genre] == "keep":
                            continue
                        
                        HT['remove_genres'].append(genre)
                    
                elif favor == "disliked":
                        
                    HT['remove_genres'].extend(profile['instances'][0][key])
                        
                continue
            
            if topic == "authors":
                
                if favor == "liked":
                    
                    pass
                    
                    #HT['keep_authors'].extend(profile['instances'][0][key])
                    
                elif favor == "disliked":
                        
                    HT['remove_authors'].extend(profile['instances'][0][key])
                        
                continue
            
    
    print(f"Extracted User Profile args:\n\n{HT}\n")      
    
    HT_string = {"liked_books":"","disliked_books":"","liked_genres":"","disliked_genres":"","liked_authors":"","disliked_authors":"", "books_history":"",
                 "keep_authors":"","remove_authors":"","keep_genres":"","remove_genres":""}

    for key in HT_string.keys():
        
        # print(f"key: {key}, HT[key]: {HT[key]}\n")
        
        for i, entry in enumerate(HT[key]):
            HT_string[key] += f'"{entry}"'

            # print(f'\\\"{entry}\\\"')
                
            if i != len(HT[key]) - 1:
                HT_string[key] +=  ", "

            # print(HT_string[key])
            
        HT_string[key] = "[" + HT_string[key] + "]"
        
        print(f"Final HT_string[{key}]: {HT_string[key]}\n")

    # for key in HT_string.keys():
        # print(f"Final HT_string[key]: {HT_string[key]}\n")
    
    constructed_profile = '{\"instances\": [{\"authors\": 0,\"user_id\":["' + str(profile["instances"][0]["user_id"]) + '"],\"liked_books\": ' + HT_string["liked_books"] + ', \"disliked_books\": ' + HT_string["disliked_books"] + ',\"liked_genres\":' + HT_string["liked_genres"] + ',\"disliked_genres\":' + HT_string["disliked_genres"] + ',\"liked_authors\": ' + HT_string["liked_authors"] + ',\"disliked_authors\": ' + HT_string["disliked_authors"] + ',\"liked_ratings\": ' + str(HT["liked_ratings"]) + ',\"disliked_ratings\": ' + str(HT["disliked_ratings"]) + ', \"keep_title\": [],\"keep_author\": [],\"keep_genre_consolidated\": [],\"remove_title\": ' + HT_string["books_history"] + ',\"remove_author\": ' + HT_string["remove_authors"] + ',\"remove_genre_consolidated\":' + HT_string["remove_genres"] + ',\"categories\": 0,\"description\": 0,\"target_book\": 0,\"target_book_rating\": 0}]}'
    
    print(f"Constructed Profile Pre: {constructed_profile}\n")
    
    dump1 = json.dumps(constructed_profile)
    # print(f"Dump1 Type: {type(dump1)}\n\n")
    load_1 = json.loads(dump1)
 
    # Wrap constructed_profile as a dictionary with "user" key
    constructed_profile_json = {}
    
    load_1 = json.dumps(load_1)
    
    constructed_profile_json["user"] = load_1
      
     # ----------------------------------------------
    url = "http://3.222.96.42/rec/recommended"
    
    response = requests.post(url, params=constructed_profile_json)
    # Response type is <class 'requests.models.Response'>
    
    # print(f"Response: {response}\n")
    # print(f"Response Type: {type(response)}\n")
    # print(response.status_code)
    # print(response.text)
    rec_load = json.loads(response.text)
    #print(f"Response Text: {rec_text}\n\n")
    # print(f"Response Text Type: {type(rec_load)}\n")
    # print(f"Rec Text Keys: {rec_load.keys()}\n")
    
    rec_text = rec_load['recommendations']
    pca_book_embeddings = rec_load['pca_book_embeddings']
    pca_user_embeddings = rec_load['pca_user_embedding']
    
    
    #print(f"Rec Int: {rec_text}\n")
    
    recommendations = []
    
    for entry in rec_text:
        #print(f"Entry: {entry}\n")
        temp = list([entry.get('title'), entry.get('similarity')])
        #print(f"temp: {temp}\n")
        LLM_input = {'input_data': {'user_data':profile, 'recommendation': [temp]}}
        #print(f"LLM_input: {LLM_input}\n")
        expl_rec = requests.post("http://54.211.202.149/recommendation-explanation/", json=LLM_input)
        
        rec_metadata = {}
        
        rec_metadata['title'] = entry['title']
        rec_metadata['similarity'] = entry['similarity']
        
        rec_metadata['explanation'] = expl_rec.text
        
        recommendations.append(rec_metadata)

          
    # print(f"Expl Rec: {expl_rec}\n")
    # print(f"Expl Rec Type: {type(expl_rec)}\n")
    # print(f"Expl Rec Status Code: {expl_rec.status_code}\n")
    # print(f"Expl Rec Text: {expl_rec.text}\n")
    # print(f"Expl Rec JSON: {expl_rec.json()}\n")
    
    end_time = time.time()
    
    # Create a dictionary to hold the recommendations and PCA embeddings
    recommendations = {
        "recommendations": recommendations,
        "pca_book_embeddings": pca_book_embeddings,
        "pca_user_embeddings": pca_user_embeddings,
        "time_elapsed": end_time - start_time
    }

    
    return {"recommendations": recommendations}
    #return {"recommendations": recommendations}
