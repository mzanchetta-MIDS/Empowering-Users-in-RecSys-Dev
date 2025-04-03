from pydantic import BaseModel
from fastapi import FastAPI
from typing import List, Dict, Any, Optional
import logging

# Import only the necessary functions
from src.db_utils import get_unique_genres, get_unique_authors, get_unique_books, get_book_covers_lookup

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

@rec.get("/books", response_model=BookResponse)
async def get_books_endpoint():
    """
    Get available books from the database
    """
    try:
        books = get_unique_books()
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
    print("\n----- RECEIVED PROFILE UPDATE IN NEW FORMAT -----")
    print(data.model_dump_json(indent=2))
    print("-----------------------------------\n")
    return {"message": "Profile updated successfully"}


@rec.post("/recommendations")
async def get_recommendations(profile: UserProfile):
    """
    Get personalized recommendations based on user profile.
    Returns recommendations in the new nested format with embeddings and timing data.
    """
    # Sample data based on the new structure
    response_data = {
        "recommendations": {
            "recommendations": [
                {
                    "title": "Caesar: The Life of a Panda Leopard",
                    "similarity": 0.6175022438470481,
                    "explanation": "{\"recommendation_explanation\":{\"recommended_book\":\"Caesar: The Life of a Panda Leopard\",\"author\":\"\\\"Patrick OBrian\\\"\",\"description\":\"Tells the enchanting yet bloodthirsty story of a creature whose father was a giant panda and whose mother was a snow leopard, in a new edition of a book first published in 1930, when the author was fifteen years old. Reprint.\",\"explanation\":\"Based on your preference for Architecture and Biography & Autobiography genres, and your dislike for Art, the recommended book, \\\"Caesar: The Life of a Panda Leopard,\\\" might intrigue you. This book, although categorized under Folk Tales, Legends & Mythology, shares thematic elements with biographies. It's a story about a unique creature, much like architectural marvels or intriguing historical figures. Despite not being a traditional architecture or biography title, its narrative structure and engaging storytelling could appeal to your tastes. Additionally, since you've indicated a dislike for fantasy, this book, being a folk tale, does not contain fantastical elements.\"}}"
                },
                {
                    "title": "Gift From the Sea - An Answer to the Conflicts in Our Lives",
                    "similarity": 0.5696139166700369,
                    "explanation": "{\"recommendation_explanation\":{\"recommended_book\":\"Gift From the Sea - An Answer to the Conflicts in Our Lives\",\"author\":\"Candace Fleming\",\"description\":\"WINNER OF THE 2021 YALSA AWARD FOR EXCELLENCE IN NONFICTION FOR YOUNG ADULTS! SIX STARRED REVIEWS! Discover the dark side of Charles Lindbergh--one of America's most celebrated heroes and complicated men--in this riveting biography from the acclaimed author of The Family Romanov. First human to cross the Atlantic via airplane; one of the first American media sensations; Nazi sympathizer and anti-Semite; loner whose baby was kidnapped and murdered; champion of Eugenics, the science of improving a human population by controlled breeding; tireless environmentalist. Charles Lindbergh was all of the above and more. Here is a rich, multi-faceted, utterly spellbinding biography about an American hero who was also a deeply flawed man. In this time where values Lindbergh held, like white Nationalism and America First, are once again on the rise, The Rise and Fall of Charles Lindbergh is essential reading for teens and history fanatics alike.\",\"explanation\":\"Based on your preference for biography & autobiography and your dislike for art, \\\"Gift From the Sea\\\" was recommended. This book, a biography, aligns with your interests. It's about Charles Lindbergh, a complex historical figure, which might appeal to you given your enjoyment of biographies about intriguing individuals. Since you've indicated a dislike for fantasy, rest assured that this book does not contain any fantasy elements.\"}}"
                },
                {
                    "title": "Arnhem",
                    "similarity": 0.5561827944775912,
                    "explanation": "{\"recommendation_explanation\":{\"recommended_book\":\"Arnhem\",\"author\":\"Antony Beevor\",\"description\":\"On 17 September 1944, General Kurt Student, the founder of Nazi Germany's parachute forces, heard the growing roar of aero engines. He went out on to his balcony above the flat landscape of southern Holland to watch the vast air armada of Dakotas and gliders,carrying the British 1st Airborne and the American 101st and 82nd Airborne Divisions. He gazed up in envy at the greatest demonstration of paratroop power ever seen. Operation Market Garden, the plan to end the war by capturing the bridges leading to the Lower Rhine and beyond, was a bold concept: the Americans thought it unusually bold for Field Marshal Montgomery. But the cost of failure was horrendous, above all for the Dutch who risked everything to help. German reprisals were cruel and lasted until the end of the war.\",\"explanation\":\"Based on your preference for biography & autobiography and architecture genres, and your dislike for art, the recommended book, \\\"Arnhem\\\" by Antony Beevor, was suggested. This history book shares themes of historical events and military strategy, aligning with your interests. Additionally, it does not contain fantasy elements, as per your preference.\"}}"
                },
                {
                    "title": "The Silmarillion",
                    "similarity": 0.5270004643591029,
                    "explanation": "{\"recommendation_explanation\":{\"recommended_book\":\"The Silmarillion\",\"author\":\"J. R. R. Tolkien\",\"description\":\"Tales and legends chronicling the world's beginnings and the happenings of the First Age, focusing on the theft of the Simarils--the three jewels crafted by Fèeanor--by Morgoth, first Dark Lord of Middle-earth.\",\"explanation\":\"Based on your preference for genres like Architecture and Biography & Autobiography, and your dislike for Art, the recommended book, \\\"The Silmarillion\\\" by J.R.R. Tolkien, was suggested due to its narrative structure and content. This epic work of mythology and legend shares thematic elements with biography, as it chronicles the history of Middle-earth and its characters. Despite your dislike for fantasy, \\\"The Silmarillion\\\" is not a typical fantasy novel. Instead, it's a collection of interconnected stories with a strong focus on history and mythology, which aligns with your interests.\"}}"
                },
                {
                    "title": "A Day of Pleasure: Stories of a Boy Growing up in Warsaw",
                    "similarity": 0.5254086905116817,
                    "explanation": "{\"recommendation_explanation\":{\"recommended_book\":\"A Day of Pleasure: Stories of a Boy Growing up in Warsaw\",\"author\":\"Isaac Bashevis Singer\",\"description\":\"An ALA Notable Book. A Day of Pleasure is the winner of the 1970 National Book Award for Children's Books.\",\"explanation\":\"Based on your preference for genres like Architecture and Biography & Autobiography, and your dislike for Art, the recommended book, \\\"A Day of Pleasure: Stories of a Boy Growing up in Warsaw\\\" by Isaac Bashevis Singer, was suggested. This book is a collection of stories, which falls under the Biography & Autobiography genre, and aligns with your interest. Additionally, Singer's writing style is known for its rich detail and human insight, which might appeal to your appreciation for architecture. Since you've indicated a dislike for fantasy, this book, being a work of realistic fiction, avoids that genre as well.\"}}"
                },
                {
                    "title": "The Awakening and Selected Stories (Modern Library Classics)",
                    "similarity": 0.5212525372520747,
                    "explanation": "{\"recommendation_explanation\":{\"recommended_book\":\"The Awakening and Selected Stories (Modern Library Classics)\",\"author\":\"Kate Chopin\",\"description\":\"WHEN IT FIRST APPEARED IN 1899, THE AWAKENING WAS GREETED WITH CRIES OF OUTRAGE. THE NOVEL'S FRANK PORTRAYAL OF A WOMAN'S EMOTIONAL, INTELLECTUAL, AND SEXUAL AWAKENING SHOCKED THE SENSIBILITIES OF THE TIME AND DESTROYED THE AUTHOR'S REPUTATION AND CAREER.\",\"explanation\":\"Based on your preference for Biography & Autobiography and Architecture genres, and your dislike for Art, the recommended book, \\\"The Awakening and Selected Stories\\\" by Kate Chopin, aligns with your interests. This collection of stories doesn't contain fantasy elements, as per your preference, and offers a rich exploration of human emotions and experiences, which resonates with your enjoyed books.\"}}"
                }
            ],
            "pca_book_embeddings": [
                {
                    "genre": "Fiction / Mystery & Detective",
                    "PCA_book_embeddings": [
                    -5.438150405883789,
                    -1.3403127193450928,
                    2.9956777095794678
                    ]
                },
                {
                    "genre": "Young Adult Fiction / General",
                    "PCA_book_embeddings": [
                    -4.5849609375,
                    1.3955729007720947,
                    0.11003676056861877
                    ]
                },
                {
                    "genre": "Drama / General",
                    "PCA_book_embeddings": [
                    -1.2343416213989258,
                    0.3158116638660431,
                    -0.28553810715675354
                    ]
                },
                {
                    "genre": "Juvenile Fiction / Fantasy & Magic",
                    "PCA_book_embeddings": [
                    -4.245406150817871,
                    -0.04301312193274498,
                    0.16828033328056335
                    ]
                },
                {
                    "genre": "Juvenile Fiction / General",
                    "PCA_book_embeddings": [
                    -1.1728687286376953,
                    -3.1813459396362305,
                    1.6162090301513672
                    ]
                },
                {
                    "genre": "Fiction / World Literature",
                    "PCA_book_embeddings": [
                    -4.724133014678955,
                    0.8812577724456787,
                    1.2946008443832397
                    ]
                },
                {
                    "genre": "Fiction / Romance",
                    "PCA_book_embeddings": [
                    -4.6014404296875,
                    2.067049980163574,
                    0.7860485911369324
                    ]
                },
                {
                    "genre": "Political Science / General",
                    "PCA_book_embeddings": [
                    3.234452724456787,
                    0.5474057197570801,
                    -2.3362879753112793
                    ]
                },
                {
                    "genre": "Fiction / Literary",
                    "PCA_book_embeddings": [
                    -4.634605884552002,
                    -1.196645736694336,
                    3.3640944957733154
                    ]
                },
                {
                    "genre": "Business & Economics / General",
                    "PCA_book_embeddings": [
                    5.193511009216309,
                    0.22182206809520721,
                    2.339620351791382
                    ]
                },
                {
                    "genre": "Juvenile Fiction / Legends, Myths, Fables",
                    "PCA_book_embeddings": [
                    0.13802815973758698,
                    0.8978589177131653,
                    -1.0384076833724976
                    ]
                },
                {
                    "genre": "Juvenile Fiction / Science Fiction",
                    "PCA_book_embeddings": [
                    -2.917534351348877,
                    -4.2339582443237305,
                    0.14952713251113892
                    ]
                },
                {
                    "genre": "Fiction / Fairy Tales, Folk Tales, Legends & Mythology",
                    "PCA_book_embeddings": [
                    -4.036827564239502,
                    -2.536520004272461,
                    1.1834754943847656
                    ]
                },
                {
                    "genre": "Fiction / Science Fiction",
                    "PCA_book_embeddings": [
                    -3.5960030555725098,
                    1.3500912189483643,
                    2.0808639526367188
                    ]
                },
                {
                    "genre": "Fiction / Classics",
                    "PCA_book_embeddings": [
                    -3.2375881671905518,
                    0.36583390831947327,
                    -0.7111803889274597
                    ]
                },
                {
                    "genre": "Religion / General",
                    "PCA_book_embeddings": [
                    3.6169557571411133,
                    2.2500927448272705,
                    0.5735050439834595
                    ]
                },
                {
                    "genre": "Fiction / General",
                    "PCA_book_embeddings": [
                    -4.009270668029785,
                    0.3470594882965088,
                    1.7322139739990234
                    ]
                },
                {
                    "genre": "Fiction / Ghost",
                    "PCA_book_embeddings": [
                    -3.214536428451538,
                    -0.6168758869171143,
                    -0.7554115653038025
                    ]
                },
                {
                    "genre": "Fiction / Action & Adventure",
                    "PCA_book_embeddings": [
                    -5.370151519775391,
                    1.182400107383728,
                    -1.2853612899780273
                    ]
                },
                {
                    "genre": "Juvenile Nonfiction / General",
                    "PCA_book_embeddings": [
                    0.7215129137039185,
                    -0.12928983569145203,
                    0.9324870705604553
                    ]
                },
                {
                    "genre": "Juvenile Fiction / Fairy Tales & Folklore",
                    "PCA_book_embeddings": [
                    -2.529700756072998,
                    -0.7770594954490662,
                    -2.5146796703338623
                    ]
                },
                {
                    "genre": "Fiction / War & Military",
                    "PCA_book_embeddings": [
                    -4.0611467361450195,
                    0.7607995271682739,
                    2.0499777793884277
                    ]
                },
                {
                    "genre": "History / Maritime History & Piracy",
                    "PCA_book_embeddings": [
                    2.6677780151367188,
                    -2.8436758518218994,
                    -1.354006052017212
                    ]
                },
                {
                    "genre": "Juvenile Fiction / Thrillers & Suspense",
                    "PCA_book_embeddings": [
                    -1.5964909791946411,
                    1.9213664531707764,
                    -0.048280179500579834
                    ]
                },
                {
                    "genre": "Comics & Graphic Novels / Superheroes",
                    "PCA_book_embeddings": [
                    -1.6730304956436157,
                    0.3766522705554962,
                    -2.269861936569214
                    ]
                },
                {
                    "genre": "Literary Criticism / General",
                    "PCA_book_embeddings": [
                    0.798335075378418,
                    -3.5292582511901855,
                    -1.2145613431930542
                    ]
                },
                {
                    "genre": "Science / General",
                    "PCA_book_embeddings": [
                    5.12402868270874,
                    -0.3641580641269684,
                    2.0461199283599854
                    ]
                },
                {
                    "genre": "Reference / General",
                    "PCA_book_embeddings": [
                    1.5324323177337646,
                    1.3600170612335205,
                    0.14596836268901825
                    ]
                },
                {
                    "genre": "History / General",
                    "PCA_book_embeddings": [
                    3.140113115310669,
                    -1.2462399005889893,
                    4.5324320793151855
                    ]
                },
                {
                    "genre": "Fiction / Occult & Supernatural",
                    "PCA_book_embeddings": [
                    -4.803785800933838,
                    0.44479042291641235,
                    1.7178601026535034
                    ]
                },
                {
                    "genre": "Philosophy / General",
                    "PCA_book_embeddings": [
                    3.866582155227661,
                    0.4423665702342987,
                    -0.9557384848594666
                    ]
                },
                {
                    "genre": "Computers / General",
                    "PCA_book_embeddings": [
                    4.115031719207764,
                    0.1375100165605545,
                    0.5807000994682312
                    ]
                },
                {
                    "genre": "Biography & Autobiography / Personal Memoirs",
                    "PCA_book_embeddings": [
                    0.4472804665565491,
                    2.173128128051758,
                    2.331615447998047
                    ]
                },
                {
                    "genre": "Art / General",
                    "PCA_book_embeddings": [
                    1.1135412454605103,
                    1.4369637966156006,
                    1.2995800971984863
                    ]
                },
                {
                    "genre": "Fiction / Visionary & Metaphysical",
                    "PCA_book_embeddings": [
                    -0.9554826021194458,
                    -3.77955961227417,
                    0.13419589400291443
                    ]
                },
                {
                    "genre": "Family & Relationships / General",
                    "PCA_book_embeddings": [
                    2.385143280029297,
                    1.1062283515930176,
                    -0.7537354826927185
                    ]
                },
                {
                    "genre": "Fiction / Thrillers",
                    "PCA_book_embeddings": [
                    -4.6142730712890625,
                    -1.6675896644592285,
                    -0.836441159248352
                    ]
                },
                {
                    "genre": "Health & Fitness / General",
                    "PCA_book_embeddings": [
                    4.277723789215088,
                    -2.0719809532165527,
                    -0.43407657742500305
                    ]
                },
                {
                    "genre": "Fiction / Anthologies",
                    "PCA_book_embeddings": [
                    -2.895049810409546,
                    -1.5323381423950195,
                    1.6593598127365112
                    ]
                },
                {
                    "genre": "Biography & Autobiography / General",
                    "PCA_book_embeddings": [
                    1.5223937034606934,
                    -0.6423241496086121,
                    -2.299941062927246
                    ]
                },
                {
                    "genre": "Fiction / Sea Stories",
                    "PCA_book_embeddings": [
                    -3.508021116256714,
                    -1.5504837036132812,
                    1.1619296073913574
                    ]
                },
                {
                    "genre": "Fiction / Erotica",
                    "PCA_book_embeddings": [
                    -5.243581295013428,
                    2.0993425846099854,
                    2.3194565773010254
                    ]
                },
                {
                    "genre": "Fiction / Sagas",
                    "PCA_book_embeddings": [
                    -4.248469352722168,
                    2.244277000427246,
                    1.6796361207962036
                    ]
                },
                {
                    "genre": "Fiction / Magical Realism",
                    "PCA_book_embeddings": [
                    -4.637389659881592,
                    1.5850467681884766,
                    1.5464048385620117
                    ]
                },
                {
                    "genre": "Fiction / Biographical",
                    "PCA_book_embeddings": [
                    -2.5752623081207275,
                    0.09400752931833267,
                    -3.304532051086426
                    ]
                },
                {
                    "genre": "History / Expeditions & Discoveries",
                    "PCA_book_embeddings": [
                    2.8505969047546387,
                    1.361673355102539,
                    2.76843523979187
                    ]
                },
                {
                    "genre": "Education / General",
                    "PCA_book_embeddings": [
                    1.6385694742202759,
                    -1.9559130668640137,
                    0.5622413754463196
                    ]
                },
                {
                    "genre": "Juvenile Fiction / Nursery Rhymes",
                    "PCA_book_embeddings": [
                    -1.788420557975769,
                    -2.825669288635254,
                    0.10402479022741318
                    ]
                },
                {
                    "genre": "Humor / Topic",
                    "PCA_book_embeddings": [
                    0.20103098452091217,
                    -4.576673984527588,
                    1.264945387840271
                    ]
                },
                {
                    "genre": "Nature / General",
                    "PCA_book_embeddings": [
                    1.7667920589447021,
                    3.2475969791412354,
                    1.455953598022461
                    ]
                },
                {
                    "genre": "True Crime / Murder",
                    "PCA_book_embeddings": [
                    -0.7616703510284424,
                    2.149416446685791,
                    -3.5549097061157227
                    ]
                },
                {
                    "genre": "Psychology / General",
                    "PCA_book_embeddings": [
                    5.082486152648926,
                    -1.6022554636001587,
                    1.9984302520751953
                    ]
                },
                {
                    "genre": "Social Science / General",
                    "PCA_book_embeddings": [
                    1.3026400804519653,
                    0.34495311975479126,
                    -1.6167985200881958
                    ]
                },
                {
                    "genre": "Photography / General",
                    "PCA_book_embeddings": [
                    4.38034200668335,
                    0.29413220286369324,
                    -1.7569100856781006
                    ]
                },
                {
                    "genre": "Religion / Theology",
                    "PCA_book_embeddings": [
                    3.3539645671844482,
                    3.0425772666931152,
                    0.721721351146698
                    ]
                },
                {
                    "genre": "Fiction / Dystopian",
                    "PCA_book_embeddings": [
                    -3.3099026679992676,
                    -1.3114646673202515,
                    2.5899317264556885
                    ]
                },
                {
                    "genre": "History / Wars & Conflicts",
                    "PCA_book_embeddings": [
                    2.53027081489563,
                    -0.9076191782951355,
                    0.22848986089229584
                    ]
                },
                {
                    "genre": "Body, Mind & Spirit / General",
                    "PCA_book_embeddings": [
                    3.4271962642669678,
                    -0.2367611825466156,
                    3.5141208171844482
                    ]
                },
                {
                    "genre": "Fiction / Short Stories",
                    "PCA_book_embeddings": [
                    -2.123596668243408,
                    2.3700344562530518,
                    1.0264885425567627
                    ]
                },
                {
                    "genre": "History / Social History",
                    "PCA_book_embeddings": [
                    0.685825526714325,
                    1.4597417116165161,
                    1.6025736331939697
                    ]
                },
                {
                    "genre": "Games & Activities / General",
                    "PCA_book_embeddings": [
                    0.517029881477356,
                    -3.0313332080841064,
                    0.6287784576416016
                    ]
                },
                {
                    "genre": "Fiction / Family Life",
                    "PCA_book_embeddings": [
                    -4.165838718414307,
                    3.811162233352661,
                    -0.19513849914073944
                    ]
                },
                {
                    "genre": "Comics & Graphic Novels / General",
                    "PCA_book_embeddings": [
                    -3.588148593902588,
                    0.8537105321884155,
                    -2.793095827102661
                    ]
                },
                {
                    "genre": "Fiction / City Life",
                    "PCA_book_embeddings": [
                    -5.523941993713379,
                    -0.3617860972881317,
                    -0.9894546866416931
                    ]
                },
                {
                    "genre": "Biography & Autobiography / Literary Figures",
                    "PCA_book_embeddings": [
                    0.8252467513084412,
                    -0.5769647359848022,
                    -1.0717499256134033
                    ]
                },
                {
                    "genre": "Juvenile Fiction / Short Stories",
                    "PCA_book_embeddings": [
                    -2.8069186210632324,
                    -1.3083537817001343,
                    -2.148289203643799
                    ]
                },
                {
                    "genre": "Fiction / Crime",
                    "PCA_book_embeddings": [
                    -1.1667840480804443,
                    -2.139892101287842,
                    1.239030361175537
                    ]
                },
                {
                    "genre": "Travel / Essays & Travelogues",
                    "PCA_book_embeddings": [
                    -1.5849521160125732,
                    3.372804641723633,
                    0.9409613609313965
                    ]
                },
                {
                    "genre": "Technology & Engineering / General",
                    "PCA_book_embeddings": [
                    1.798823595046997,
                    2.705444812774658,
                    1.5305614471435547
                    ]
                },
                {
                    "genre": "Drama / Shakespeare",
                    "PCA_book_embeddings": [
                    -1.9959927797317505,
                    0.7136659622192383,
                    -3.175471782684326
                    ]
                },
                {
                    "genre": "History / Historiography",
                    "PCA_book_embeddings": [
                    3.5713396072387695,
                    -1.5292178392410278,
                    1.178690791130066
                    ]
                },
                {
                    "genre": "Bibles / General",
                    "PCA_book_embeddings": [
                    1.2517153024673462,
                    3.283468246459961,
                    -1.756363868713379
                    ]
                },
                {
                    "genre": "History / Indigenous Peoples of the Americas",
                    "PCA_book_embeddings": [
                    0.7782724499702454,
                    0.6372498273849487,
                    -1.6148784160614014
                    ]
                },
                {
                    "genre": "Cooking / Individual Chefs & Restaurants",
                    "PCA_book_embeddings": [
                    -0.031209103763103485,
                    2.415781259536743,
                    -2.5337817668914795
                    ]
                },
                {
                    "genre": "Performing Arts / General",
                    "PCA_book_embeddings": [
                    0.05549469590187073,
                    -2.0305449962615967,
                    2.062079668045044
                    ]
                },
                {
                    "genre": "Fiction / Noir",
                    "PCA_book_embeddings": [
                    -4.869932651519775,
                    -1.6069382429122925,
                    -1.4511555433273315
                    ]
                },
                {
                    "genre": "Poetry / General",
                    "PCA_book_embeddings": [
                    -0.16148287057876587,
                    -0.9208160042762756,
                    -2.4641263484954834
                    ]
                },
                {
                    "genre": "History / Military",
                    "PCA_book_embeddings": [
                    2.838625907897949,
                    -1.7962193489074707,
                    -0.3674156069755554
                    ]
                },
                {
                    "genre": "Cooking / General",
                    "PCA_book_embeddings": [
                    1.9778389930725098,
                    -2.406576633453369,
                    -1.6444813013076782
                    ]
                },
                {
                    "genre": "Travel / General",
                    "PCA_book_embeddings": [
                    0.8110064268112183,
                    0.8061566948890686,
                    -2.678339958190918
                    ]
                },
                {
                    "genre": "Music / General",
                    "PCA_book_embeddings": [
                    2.4526684284210205,
                    -2.1056721210479736,
                    0.06403367966413498
                    ]
                },
                {
                    "genre": "Sports & Recreation / General",
                    "PCA_book_embeddings": [
                    2.0721471309661865,
                    2.1593077182769775,
                    1.901746392250061
                    ]
                },
                {
                    "genre": "True Crime / General",
                    "PCA_book_embeddings": [
                    1.6572190523147583,
                    0.3835468888282776,
                    -0.06792978942394257
                    ]
                },
                {
                    "genre": "Religion / Christian Theology",
                    "PCA_book_embeddings": [
                    3.1855251789093018,
                    3.103039264678955,
                    -1.3088735342025757
                    ]
                },
                {
                    "genre": "Language Arts & Disciplines / General",
                    "PCA_book_embeddings": [
                    2.833019971847534,
                    0.020549964159727097,
                    -1.6500416994094849
                    ]
                },
                {
                    "genre": "Crafts & Hobbies / General",
                    "PCA_book_embeddings": [
                    2.658099889755249,
                    -2.975290060043335,
                    -0.7338870167732239
                    ]
                },
                {
                    "genre": "Pets / General",
                    "PCA_book_embeddings": [
                    2.216765880584717,
                    0.8081700801849365,
                    -1.645628809928894
                    ]
                },
                {
                    "genre": "Young Adult Nonfiction / General",
                    "PCA_book_embeddings": [
                    -2.0705666542053223,
                    -2.3449416160583496,
                    -2.552452325820923
                    ]
                },
                {
                    "genre": "House & Home / General",
                    "PCA_book_embeddings": [
                    2.63765811920166,
                    1.0824812650680542,
                    -1.4514867067337036
                    ]
                },
                {
                    "genre": "Literary Collections / General",
                    "PCA_book_embeddings": [
                    2.1008121967315674,
                    0.4434311091899872,
                    -1.008237600326538
                    ]
                },
                {
                    "genre": "Humor / General",
                    "PCA_book_embeddings": [
                    -2.9144110679626465,
                    0.3437590003013611,
                    -2.8669509887695312
                    ]
                },
                {
                    "genre": "Antiques & Collectibles / General",
                    "PCA_book_embeddings": [
                    -2.215494155883789,
                    0.5303907990455627,
                    0.12673237919807434
                    ]
                },
                {
                    "genre": "Study Aids / General",
                    "PCA_book_embeddings": [
                    1.195721983909607,
                    -0.6913668513298035,
                    -2.232177495956421
                    ]
                },
                {
                    "genre": "Foreign Language Study / General",
                    "PCA_book_embeddings": [
                    4.75466775894165,
                    -0.7810948491096497,
                    0.12906910479068756
                    ]
                },
                {
                    "genre": "Medical / General",
                    "PCA_book_embeddings": [
                    4.3316969871521,
                    -0.6035783290863037,
                    1.7986423969268799
                    ]
                },
                {
                    "genre": "Law / General",
                    "PCA_book_embeddings": [
                    1.777740478515625,
                    -0.9325470924377441,
                    -1.3265621662139893
                    ]
                },
                {
                    "genre": "Mathematics / General",
                    "PCA_book_embeddings": [
                    4.189825057983398,
                    2.527113437652588,
                    2.1471638679504395
                    ]
                },
                {
                    "genre": "History / Historical Geography",
                    "PCA_book_embeddings": [
                    4.3091044425964355,
                    1.5210758447647095,
                    1.1597795486450195
                    ]
                },
                {
                    "genre": "Architecture / General",
                    "PCA_book_embeddings": [
                    4.745876312255859,
                    1.0007226467132568,
                    0.9429165124893188
                    ]
                },
                {
                    "genre": "Transportation / General",
                    "PCA_book_embeddings": [
                    4.5914387702941895,
                    -0.3206862211227417,
                    -1.6474721431732178
                    ]
                },
                {
                    "genre": "Gardening / General",
                    "PCA_book_embeddings": [
                    0.14898861944675446,
                    1.038736343383789,
                    -3.455672264099121
                    ]
                },
                {
                    "genre": "Design / General",
                    "PCA_book_embeddings": [
                    4.039839744567871,
                    -0.6738415956497192,
                    -0.06163935363292694
                    ]
                }
                ],
            "pca_user_embeddings": [
                [-0.4213385707486399, -0.11417443878396308, 0.4383526774462425]
            ],
            "time_elapsed": 11.189362525939941
        }
    }

    return response_data

@rec.get("/test-book-covers")
async def test_book_covers():
    """
    Directly test the book_covers table in the database
    """
    try:
        covers_df = get_book_covers_lookup()
        
        return {
            "success": True,
            "covers_found": not covers_df.empty,
            "total_rows": len(covers_df),
            "sample_data": covers_df.head(3).to_dict(orient='records') if not covers_df.empty else []
        }
    except Exception as e:
        return {"error": str(e)}



