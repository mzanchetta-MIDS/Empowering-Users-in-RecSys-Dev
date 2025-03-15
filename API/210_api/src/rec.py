from pydantic import BaseModel, field_validator
from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse
from datetime import datetime
import joblib
#import numpy as np
from datetime import datetime

from typing import List, Dict, Any, Optional
import json

# load the rec model
#rec_model = joblib.load('rec_model.pkl')

# load the LLM model
#llm_model = joblib.load('llm_model.pkl')

rec = FastAPI()


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

@rec.get("/genres", response_model=GenreResponse)
async def get_genres():
    # Hard-coded genres for now
    genres = ['Antiques & Collectibles', 'Architecture', 'Art', 'Bibles',
    'Biography & Autobiography', 'Body, Mind & Spirit',
    'Business & Economics', 'Comics & Graphic Novels', 'Computers',
    'Cooking', 'Crafts & Hobbies', 'Design', 'Drama', 'Education',
    'Family & Relationships', 'Fiction', 'Fiction / Literary', 
    'Fiction / Magical Realism', 'Fiction / Historical', 'Foreign Language Study',
    'Games & Activities', 'Gardening', 'Health & Fitness', 'History',
    'House & Home', 'Humor', 'Juvenile Fiction', 'Juvenile Nonfiction',
    'Language Arts & Disciplines', 'Law', 'Literary Collections',
    'Literary Criticism', 'Mathematics', 'Medical', 'Music', 'Nature',
    'Performing Arts', 'Pets', 'Philosophy', 'Photography', 'Poetry',
    'Poetry / General', 'Political Science', 'Psychology', 'Reference', 
    'Religion', 'Science', 'Self-help', 'Social Science', 
    'Sports & Recreation', 'Study Aids', 'Technology & Engineering', 
    'Transportation', 'Travel', 'True Crime', 'Young Adult Fiction',
    'Young Adult Nonfiction']
    
    return {"genres": genres}


@rec.get("/authors", response_model=AuthorResponse)
async def get_authors():
    # Hard-coded authors for now
    authors = [
    "J.K. Rowling", "Stephen King", "Jane Austen",
    "Agatha Christie", "Neil Gaiman", "George R.R. Martin", "Michael Lewis",
    "Gabriel García Márquez", "Haruki Murakami", "Toni Morrison", "Salman Rushdie",
    "Ted Chiang", "Ursula K. Le Guin", "Albert Camus", "Yuval Noah Harari",
    "Michelle McNamara", "Talia Hibbert", "Glennon Doyle", "Erin Morgenstern",
    "Zadie Smith", "Roxane Gay", "Marjane Satrapi", "Chimamanda Ngozi Adichie",
    "Sally Rooney"
]

    return {"authors": authors}

@rec.get("/books", response_model=BookResponse)
async def get_books():
    # Hard-coded books for now
    books = [
   "To Kill a Mockingbird - Harper Lee",
   "1984 - George Orwell",
   "Pride and Prejudice - Jane Austen",
   "The Great Gatsby - F. Scott Fitzgerald",
   "Moby Dick - Herman Melville",
   "Moneyball - Michael Lewis",
   "One Hundred Years of Solitude - Gabriel García Márquez",
   "Beloved - Toni Morrison",
   "The Wind-Up Bird Chronicle - Haruki Murakami",
   "Midnight's Children - Salman Rushdie",
   "Exhalation - Ted Chiang",
   "The Left Hand of Darkness - Ursula K. Le Guin",
   "The Stranger - Albert Camus",
   "Sapiens - Yuval Noah Harari",
   "Brave New World - Aldous Huxley",
   "Neverwhere - Neil Gaiman",
   "I'll Be Gone in the Dark - Michelle McNamara",
   "Get a Life, Chloe Brown - Talia Hibbert",
   "Untamed - Glennon Doyle",
   "The Night Circus - Erin Morgenstern",
   "White Teeth - Zadie Smith",
   "Bad Feminist - Roxane Gay",
   "Persepolis - Marjane Satrapi",
   "Americanah - Chimamanda Ngozi Adichie",
   "Normal People - Sally Rooney",
   "A Game of Thrones - George R.R. Martin",
   "The Handmaid's Tale - Margaret Atwood",
   "And Then There Were None - Agatha Christie",
   "Harry Potter and the Sorcerer's Stone - J.K. Rowling",
   "The Shining - Stephen King"
]
    return {"books": books}

@rec.post("/users/profile")
async def update_user_profile(profile: UserProfile):
    print("\n----- RECEIVED PROFILE UPDATE -----")
    print(profile.dict())
    print("-----------------------------------\n")
    return {"message": "Profile updated successfully"}


@rec.post("/recommendations")
async def get_recommendations(profile: UserProfile):
    # Hard-coded recommendations for now
    # In a real implementation, this would use a recommendation model
    recommendations = [
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
    },
        {
        "id": "book-007",
        "title": "The Wind-Up Bird Chronicle",
        "author": "Haruki Murakami",
        "description": "Japan's most highly regarded novelist now vaults into the first ranks of international "
                    "fiction writers with this heroically imaginative novel, which is at once a detective "
                    "story, an account of a disintegrating marriage, and an excavation of the buried "
                    "secrets of World War II. In a Tokyo suburb a young man named Toru Okada searches for "
                    "his wife's missing cat. Soon he finds himself looking for his wife as well in a "
                    "netherworld that lies beneath the placid surface of Tokyo. As these searches intersect, "
                    "Okada encounters a bizarre group of allies and antagonists. Gripping, prophetic, suffused with comedy "
                    "and menace, The Wind-Up Bird Chronicle is a tour de force equal in scope to the "
                    "masterpieces of Mishima and Pynchon.",
        "explanation": "Since you've enjoyed Murakami's 'Hard-boiled Wonderland' but marked 'After Dark' "
                      "as not interesting, I'm recommending what many consider his definitive work. "
                      "'The Wind-Up Bird Chronicle' offers the dream-like qualities and philosophical "
                      "depth you appreciated in 'Hard-boiled Wonderland' but with a more "
                      "historical dimension through its exploration of Japan's wartime past. This "
                      "recommendation respects your Murakami preferences while offering of his most "
                      "celebrated works."
    },
     {
        "id": "book-009",
        "title": "Pachinko",
        "author": "Min Jin Lee",
        "description": "This sweeping historical epic follows four generations of a Korean family who "
                      "move to Japan in the early 20th century. Beginning in 1910 with a pregnancy "
                      "outside of marriage, the novel traces the family's struggles with identity, "
                      "belonging, and survival through colonization, war, and persistent discrimination "
                      "in their adopted country.",
        "explanation": "You've shown interest in multi-generational family sagas through your appreciation "
                      "of 'One Hundred Years of Solitude.' 'Pachinko' offers a similar scope but focuses "
                      "on the Korean-Japanese experience. The " 
                      "rich character development and exploration of cultural identity should resonate "
                      "with your interest in books that teach you about 'different historical periods or "
                      "cultures.' This recommendation expands your literary horizons while staying true "
                      "to your core interests."
    },
        {
        "id": "book-005",
        "title": "The Brief Wondrous Life of Oscar Wao",
        "author": "Junot Díaz",
        "description": "Oscar is a sweet but disastrously overweight ghetto nerd who—from the New Jersey "
                    "home he shares with his old world mother and rebellious sister—dreams of becoming "
                    "the Dominican J.R.R. Tolkien and, most of all, finding love. But Oscar may never "
                    "get what he wants. Blame the curse that has haunted Oscar's family for "
                    "generations, following them on their epic journey from Santo Domingo to the USA. "
                    "Encapsulating Dominican-American history, The Brief Wondrous Life of Oscar Wao "
                    "opens our eyes to an astonishing vision of the contemporary American experience "
                    "and explores the endless human capacity to persevere—and risk it all—in the "
                    "name of love.",
        "explanation": "Based on your interest in authors like García Márquez and Rushdie, this novel "
                    "should appeal to you with its blend of cultural history and elements of the "
                    "supernatural. The family curse mentioned in the description echoes the magical "
                    "elements you enjoy, while the Dominican-American experience offers a fresh "
                    "cultural perspective. The book's focus on a character who loves fantasy literature "
                    "adds a unique dimension that connects with your appreciation for rich, imaginative "
                    "storytelling across different cultures."
    },
    {
        "id": "book-002",
        "title": "A Tale for the Time Being",
        "author": "Ruth Ozeki",
        "description": "A compelling dual narrative that connects a novelist in British Columbia with a "
                      "teenage girl in Tokyo through a diary washed ashore after the 2011 tsunami. The "
                      "novel explores quantum physics, Zen Buddhism, suicide, bullying, and the slippery "
                      "nature of time while weaving a deeply human story across cultures and generations.",
        "explanation": "Since you rated 'The Wind-Up Bird Chronicle' highly, this novel offers similar "
                      "elements of Japanese culture with magical elements, but through a female author's "
                      "perspective. The book's meditation on time and interconnectedness mirrors themes "
                      "you've enjoyed in Murakami's work, while its structural experimentation aligns "
                      "with your stated appreciation for 'stories that challenge conventional narrative "
                      "structures.' Your interest in cross-cultural stories makes this an excellent next step."
    },
    {
        "id": "book-010",
        "title": "The Unbearable Lightness of Being",
        "author": "Milan Kundera",
        "description": "In *The Unbearable Lightness of Being*, Milan Kundera tells the story of a "
                    "young woman in love with a man torn between his love for her and his incorrigible "
                    "womanizing and one of his mistresses and her humbly faithful lover. This "
                    "magnificent novel juxtaposes geographically distant places, brilliant and playful "
                    "reflections, and a variety of styles, to take its place as perhaps the major "
                    "achievement of one of the world's truly great writers.",
        "explanation": "While you enjoy the rich, complex worlds of García Márquez and Rushdie, this "
                    "novel offers a perfect change of pace. Kundera's literary style remains "
                    "sophisticated but with a more playful approach that should serve as the 'palate "
                    "cleanser' you mentioned sometimes needing. The European setting expands the "
                    "cultural range of your reading, while its exploration of relationships and "
                    "philosophy provides the depth you value without the intensity of magical realism. "
                    "A thoughtful but refreshing addition to your reading journey."
    },
    {
        "id": "book-006",
        "title": "Homegoing",
        "author": "Yaa Gyasi",
        "description": "A novel of breathtaking sweep and emotional power that traces three hundred years "
                    "in Ghana and along the way also becomes a truly great American novel. Extraordinary "
                    "for its exquisite language, its implacable sorrow, its soaring beauty, and for its "
                    "monumental portrait of the forces that shape families and nations, Homegoing "
                    "heralds the arrival of a major new voice in contemporary fiction.",
        "explanation": "This novel aligns with your interest in literary works that span generations "
                    "and cultures. The description mentions its 'exquisite language' and 'soaring beauty,' "
                    "which connects with your appreciation for beautiful prose. As someone who enjoys "
                    "books that explore different historical periods and cultures, this story that traces "
                    "three hundred years in Ghana while also engaging with American experiences should "
                    "provide the kind of rich cultural exploration you value in your reading."
    },
        {
        "id": "book-003",
        "title": "The God of Small Things",
        "author": "Arundhati Roy",
        "description": "Set in Kerala, India, this novel tells the story of twins Rahel and Estha whose "
                      "lives are destroyed by the 'Love Laws' that dictate 'who should be loved, and how, "
                      "and how much.' The narrative shifts between 1969 and 1993, unraveling a family "
                      "tragedy against the backdrop of India's caste system, politics, and social taboos.",
        "explanation": "You marked 'Midnight's Children' as a favorite, and this Booker Prize-winning "
                      "novel offers another powerful exploration of post-colonial India but through a "
                      "more intimate, family-focused lens. Roy's lush, poetic prose will appeal to your "
                      "appreciation for 'beautiful prose' mentioned in your preferences. The novel's "
                      "exploration of forbidden love and social constraints echoes themes in 'Beloved' "
                      "by Toni Morrison, which you rated 5 stars."
    }
    ]
    return {"recommendations": recommendations}

