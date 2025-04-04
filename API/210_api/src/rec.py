from pydantic import BaseModel
from fastapi import FastAPI, Body
from typing import List, Dict, Any, Optional
import logging
import requests
import json
from contextlib import asynccontextmanager
import time

# Import only the necessary functions
from src.db_utils import connect_to_db, get_book_covers_lookup, query_to_list, query_to_df

global conn
# global curr

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
    liked_books: Dict[str, int] = {}
    disliked_books: Dict[str, int] = {}
    liked_genres: Dict[str, str] = {}
    disliked_genres: List[str] = []
    liked_authors: List[str] = []
    disliked_authors: List[str] = []
    additional_preferences: Optional[str] = None
    books_history: List[str] = [] 
    authors: int = 0
    categories: int = 0
    description: int = 0
    target_book: int = 0
    target_book_rating: int = 0

class RecModelRequest(BaseModel):
    instances: List[RecModelInstance]
    
class ProfileInput(BaseModel):
    profile: str

@rec.get("/genres", response_model=GenreResponse)
async def get_genres_endpoint():
    """
    Get available book genres from the database
    """

    global conn
    global curr
    
    query = """
        SELECT DISTINCT genre_consolidated 
        FROM books_info 
        WHERE genre_consolidated IS NOT NULL 
        ORDER BY genre_consolidated
        """
       
    try:
        genres = query_to_list(query=query, conn=conn)
        #genres = get_unique_genres(conn)
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
    
    global conn
    global curr
    
    query = """
        SELECT DISTINCT author 
        FROM books_info 
        WHERE author IS NOT NULL 
        and author NOT IN ('','1873-1954 Colette','5th Edition')
        and author NOT LIKE '%Publish%'
        ORDER BY author
        """
    try:
        authors = query_to_list(query=query, conn=conn)
        #authors = get_unique_authors()
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

@rec.get("/books", response_model=BookResponse)
async def get_books_endpoint():
    """
    Get available books from the database
    """
    
    global conn
    global curr
    
    query = """
        SELECT DISTINCT title, author 
        FROM books_info 
        ORDER BY title
        """
    
    try:
        df = query_to_df(query=query, conn=conn)
        books = [f"{row['title']} - {row['author']}" for _, row in df.iterrows()]
        #books = get_unique_books()
        if not books:
            # Fallback to hardcoded books if database query fails
            logger.warning("Using fallback hardcoded books due to empty result from database")
            books = [
                "To Kill a Mockingbird - Harper Lee",
                "1984 - George Orwell",
                "Pride and Prejudice - Jane Austen"
            ]
        return {"books": books}
    except Exception as e:
        logger.error(f"Error in get_books_endpoint: {str(e)}")
        # Fallback to hardcoded books
        books = [
            "To Kill a Mockingbird - Harper Lee",
            "1984 - George Orwell",
            "Pride and Prejudice - Jane Austen"
        ]
        return {"books": books}


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
    # print("\n----- RECEIVED PROFILE UPDATE IN NEW FORMAT -----")
    # print(data.model_dump_json(indent=2))
    # print("-----------------------------------\n")
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
          "recommended_history":[]}
    
    
    # Received profile: "{\"instances\": [{\"user_id\": \"b981eda3-0418-4344-9a8d-5abaaed505cb\", 
    # \"liked_books\": {\"1000 Best Bartender Recipes\": 5}, \"disliked_books\": {}, \"liked_genres\": 
    # {\"Biography & Autobiography / General\": \"keep\"}, \"disliked_genres\": [\"Art / General\"], 
    # \"liked_authors\": [\"A. A. Hoehling\"], \"disliked_authors\": [], \"additional_preferences\": 
    # \"No fantasy\", \"books_history\": [\"1000 Best Bartender Recipes\"], \"authors\": 0, \"categories\": 0, 
    # \"description\": 0, \"target_book\": 0, \"target_book_rating\": 0}]}"
    
    # liked_counter = 0
    # disliked_counter = 0
    #liked_books["1000 best barender"]
    #disliked_books["murder on the orient"]
    #liked_genres[0, "fantasy"]
    #disliked_genres[0, "thriller"]
    #liked_ratings[4, 5]
    #disliked_ratings[2, 1]
    
    # Convert the profile to the required format
    
    for key in profile['instances'][0].keys():
        
        if key in HT:
                        
            HT[key].extend(profile['instances'][0][key])
            
            if key.split("_")[0] == 'liked':
            
                HT['liked_ratings'].extend([5]*len(profile['instances'][0][key]))
                
            elif key.split("_")[0] == 'disliked':
                
                HT['disliked_ratings'].extend([1]*len(profile['instances'][0][key]))         
    
    HT_string = {"liked_books":"","disliked_books":"","liked_genres":"","disliked_genres":"","liked_authors":"","disliked_authors":"", "recommended_history":""}

    for key in HT_string.keys():
        
        # print(f"key: {key}, HT[key]: {HT[key]}\n")
        
        for i, entry in enumerate(HT[key]):
            HT_string[key] += f'"{entry}"'

            # print(f'\\\"{entry}\\\"')
                
            if i != len(HT[key]) - 1:
                HT_string[key] +=  ", "

            # print(HT_string[key])
            
        HT_string[key] = "[" + HT_string[key] + "]"
        
        # print(f"Final HT_string[key]: {HT_string[key]}\n")

    # for key in HT_string.keys():
        # print(f"Final HT_string[key]: {HT_string[key]}\n")
    
    constructed_profile = '{\"instances\": [{\"authors\": 0,\"user_id\":["' + str(profile["instances"][0]["user_id"]) + '"],\"liked_books\": ' + HT_string["liked_books"] + ', \"disliked_books\": ' + HT_string["disliked_books"] + ',\"liked_genres\":' + HT_string["liked_genres"] + ',\"disliked_genres\":' + HT_string["disliked_genres"] + ',\"liked_authors\": ' + HT_string["liked_authors"] + ',\"disliked_authors\": ' + HT_string["disliked_authors"] + ',\"liked_ratings\": ' + str(HT["liked_ratings"]) + ',\"disliked_ratings\": ' + str(HT["disliked_ratings"]) + ', \"keep_title\": [],\"keep_author\": [],\"keep_genre_consolidated\": [],\"remove_title\": ' + HT_string["recommended_history"] + ',\"remove_author\": ' + HT_string["disliked_authors"] + ',\"remove_genre_consolidated\":' + HT_string["disliked_genres"] + ',\"categories\": 0,\"description\": 0,\"target_book\": 0,\"target_book_rating\": 0}]}'
    
    # print(f"Constructed Profile Pre: {constructed_profile}\n")
    
    dump1 = json.dumps(constructed_profile)
    # print(f"Dump1 Type: {type(dump1)}\n\n")
    load_1 = json.loads(dump1)
 
    # Wrap constructed_profile as a dictionary with "user" key
    constructed_profile_json = {}
    
    load_1 = json.dumps(load_1)
    
    constructed_profile_json["user"] = load_1
     
    # print(f"Constructed Profile JSON:\n{constructed_profile_json}\n")
    
    # params = {
    # "user": "{\"instances\":[{\"authors\": 0,\"user_id\":[1],\"liked_books\":[\"Action\"],\"disliked_books\": [],\"liked_genres\":[],\"disliked_genres\":[],\"liked_authors\": [],\"disliked_authors\": [],\"liked_ratings\": [5],\"disliked_ratings\": [],\"categories\": 0,\"description\": 0,\"target_book\": 0,\"target_book_rating\": 0,\"keep_title\": [],\"keep_author\": [],\"keep_genre_consolidated\": [],\"remove_title\": [],\"remove_author\": [],\"remove_genre_consolidated\": []}]}"
    # }
    
    # # # print(f"params: {params}\n\n")
    
    # params_json = params
    
    # params_json["user"] = json.dumps(params_json['user'])
    
    # print(f"params_json: {params_json}\n\n")
    
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
    
    # recommendations.append(pca_book_embeddings)
    # recommendations.append(pca_user_embeddings)
    #recommendations.append(['time elapsed', end_time - start_time])
    
    print(recommendations)
    
    return {"recommendations": recommendations}
    #return {"recommendations": recommendations}


    
    # recommendations = [
    # {
    #     "id": "book-001",
    #     "title": "The Master and Margarita",
    #     "author": "Mikhail Bulgakov",
    #     "description": "A 50th-anniversary Deluxe Edition of the incomparable 20th-century masterpiece of satire and fantasy. "
    #     " One spring afternoon, the Devil, trailing fire and chaos in his wake, weaves himself out of the "
    #     "shadows and into Moscow. This fantastical, funny, and devastating satire of Soviet life combines two distinct yet "
    #     "interwoven parts, one set in contemporary Moscow, the other in ancient Jerusalem, each brimming with historical, imaginary, frightful, "
    #     "and wonderful characters. Written during the darkest days of Stalin's reign, The Master and Margarita "
    #     "became a literary phenomenon, signaling artistic and spiritual freedom for Russians everywhere.",
    #     "explanation": "This recommendation bridges your love of magical realism from García Márquez with "
    #                   "the philosophical depth you enjoy in Rushdie's work. The novel's non-linear structure "
    #                   "and blend of fantasy with harsh reality mirrors elements you appreciated in 'One "
    #                   "Hundred Years of Solitude' while introducing you to a different cultural context. " 
    #                   "Based on your preference for 'books that blur the line between reality and fantasy,' "
    #                   "this Russian classic should resonate deeply."
    # },
    #     {
    #     "id": "book-007",
    #     "title": "The Wind-Up Bird Chronicle",
    #     "author": "Haruki Murakami",
    #     "description": "Japan's most highly regarded novelist now vaults into the first ranks of international "
    #                 "fiction writers with this heroically imaginative novel, which is at once a detective "
    #                 "story, an account of a disintegrating marriage, and an excavation of the buried "
    #                 "secrets of World War II. In a Tokyo suburb a young man named Toru Okada searches for "
    #                 "his wife's missing cat. Soon he finds himself looking for his wife as well in a "
    #                 "netherworld that lies beneath the placid surface of Tokyo. As these searches intersect, "
    #                 "Okada encounters a bizarre group of allies and antagonists. Gripping, prophetic, suffused with comedy "
    #                 "and menace, The Wind-Up Bird Chronicle is a tour de force equal in scope to the "
    #                 "masterpieces of Mishima and Pynchon.",
    #     "explanation": "Since you've enjoyed Murakami's 'Hard-boiled Wonderland' but marked 'After Dark' "
    #                   "as not interesting, I'm recommending what many consider his definitive work. "
    #                   "'The Wind-Up Bird Chronicle' offers the dream-like qualities and philosophical "
    #                   "depth you appreciated in 'Hard-boiled Wonderland' but with a more "
    #                   "historical dimension through its exploration of Japan's wartime past. This "
    #                   "recommendation respects your Murakami preferences while offering of his most "
    #                   "celebrated works."
    # },
    #  {
    #     "id": "book-009",
    #     "title": "Pachinko",
    #     "author": "Min Jin Lee",
    #     "description": "This sweeping historical epic follows four generations of a Korean family who "
    #                   "move to Japan in the early 20th century. Beginning in 1910 with a pregnancy "
    #                   "outside of marriage, the novel traces the family's struggles with identity, "
    #                   "belonging, and survival through colonization, war, and persistent discrimination "
    #                   "in their adopted country.",
    #     "explanation": "You've shown interest in multi-generational family sagas through your appreciation "
    #                   "of 'One Hundred Years of Solitude.' 'Pachinko' offers a similar scope but focuses "
    #                   "on the Korean-Japanese experience. The " 
    #                   "rich character development and exploration of cultural identity should resonate "
    #                   "with your interest in books that teach you about 'different historical periods or "
    #                   "cultures.' This recommendation expands your literary horizons while staying true "
    #                   "to your core interests."
    # },
    #     {
    #     "id": "book-005",
    #     "title": "The Brief Wondrous Life of Oscar Wao",
    #     "author": "Junot Díaz",
    #     "description": "Oscar is a sweet but disastrously overweight ghetto nerd who—from the New Jersey "
    #                 "home he shares with his old world mother and rebellious sister—dreams of becoming "
    #                 "the Dominican J.R.R. Tolkien and, most of all, finding love. But Oscar may never "
    #                 "get what he wants. Blame the curse that has haunted Oscar's family for "
    #                 "generations, following them on their epic journey from Santo Domingo to the USA. "
    #                 "Encapsulating Dominican-American history, The Brief Wondrous Life of Oscar Wao "
    #                 "opens our eyes to an astonishing vision of the contemporary American experience "
    #                 "and explores the endless human capacity to persevere—and risk it all—in the "
    #                 "name of love.",
    #     "explanation": "Based on your interest in authors like García Márquez and Rushdie, this novel "
    #                 "should appeal to you with its blend of cultural history and elements of the "
    #                 "supernatural. The family curse mentioned in the description echoes the magical "
    #                 "elements you enjoy, while the Dominican-American experience offers a fresh "
    #                 "cultural perspective. The book's focus on a character who loves fantasy literature "
    #                 "adds a unique dimension that connects with your appreciation for rich, imaginative "
    #                 "storytelling across different cultures."
    # },
    # {
    #     "id": "book-002",
    #     "title": "A Tale for the Time Being",
    #     "author": "Ruth Ozeki",
    #     "description": "A compelling dual narrative that connects a novelist in British Columbia with a "
    #                   "teenage girl in Tokyo through a diary washed ashore after the 2011 tsunami. The "
    #                   "novel explores quantum physics, Zen Buddhism, suicide, bullying, and the slippery "
    #                   "nature of time while weaving a deeply human story across cultures and generations.",
    #     "explanation": "Since you rated 'The Wind-Up Bird Chronicle' highly, this novel offers similar "
    #                   "elements of Japanese culture with magical elements, but through a female author's "
    #                   "perspective. The book's meditation on time and interconnectedness mirrors themes "
    #                   "you've enjoyed in Murakami's work, while its structural experimentation aligns "
    #                   "with your stated appreciation for 'stories that challenge conventional narrative "
    #                   "structures.' Your interest in cross-cultural stories makes this an excellent next step."
    # },
    # {
    #     "id": "book-010",
    #     "title": "The Unbearable Lightness of Being",
    #     "author": "Milan Kundera",
    #     "description": "In *The Unbearable Lightness of Being*, Milan Kundera tells the story of a "
    #                 "young woman in love with a man torn between his love for her and his incorrigible "
    #                 "womanizing and one of his mistresses and her humbly faithful lover. This "
    #                 "magnificent novel juxtaposes geographically distant places, brilliant and playful "
    #                 "reflections, and a variety of styles, to take its place as perhaps the major "
    #                 "achievement of one of the world's truly great writers.",
    #     "explanation": "While you enjoy the rich, complex worlds of García Márquez and Rushdie, this "
    #                 "novel offers a perfect change of pace. Kundera's literary style remains "
    #                 "sophisticated but with a more playful approach that should serve as the 'palate "
    #                 "cleanser' you mentioned sometimes needing. The European setting expands the "
    #                 "cultural range of your reading, while its exploration of relationships and "
    #                 "philosophy provides the depth you value without the intensity of magical realism. "
    #                 "A thoughtful but refreshing addition to your reading journey."
    # },
    # {
    #     "id": "book-006",
    #     "title": "Homegoing",
    #     "author": "Yaa Gyasi",
    #     "description": "A novel of breathtaking sweep and emotional power that traces three hundred years "
    #                 "in Ghana and along the way also becomes a truly great American novel. Extraordinary "
    #                 "for its exquisite language, its implacable sorrow, its soaring beauty, and for its "
    #                 "monumental portrait of the forces that shape families and nations, Homegoing "
    #                 "heralds the arrival of a major new voice in contemporary fiction.",
    #     "explanation": "This novel aligns with your interest in literary works that span generations "
    #                 "and cultures. The description mentions its 'exquisite language' and 'soaring beauty,' "
    #                 "which connects with your appreciation for beautiful prose. As someone who enjoys "
    #                 "books that explore different historical periods and cultures, this story that traces "
    #                 "three hundred years in Ghana while also engaging with American experiences should "
    #                 "provide the kind of rich cultural exploration you value in your reading."
    # },
    #     {
    #     "id": "book-003",
    #     "title": "The God of Small Things",
    #     "author": "Arundhati Roy",
    #     "description": "Set in Kerala, India, this novel tells the story of twins Rahel and Estha whose "
    #                   "lives are destroyed by the 'Love Laws' that dictate 'who should be loved, and how, "
    #                   "and how much.' The narrative shifts between 1969 and 1993, unraveling a family "
    #                   "tragedy against the backdrop of India's caste system, politics, and social taboos.",
    #     "explanation": "You marked 'Midnight's Children' as a favorite, and this Booker Prize-winning "
    #                   "novel offers another powerful exploration of post-colonial India but through a "
    #                   "more intimate, family-focused lens. Roy's lush, poetic prose will appeal to your "
    #                   "appreciation for 'beautiful prose' mentioned in your preferences. The novel's "
    #                   "exploration of forbidden love and social constraints echoes themes in 'Beloved' "
    #                   "by Toni Morrison, which you rated 5 stars."
    # }
    # ]