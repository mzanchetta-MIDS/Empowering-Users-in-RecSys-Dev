from utils.api_client import get_genres, get_authors, get_books, get_recommendations

def get_unique_books():
    """
    Get all unique books from the API.
    Falls back to hardcoded values if API fails.
    """
    books = get_books()
    if not books:
        # Fallback to hardcoded books if API call fails
        return [
            "To Kill a Mockingbird - Harper Lee",
            "1984 - George Orwell",
            "Pride and Prejudice - Jane Austen",
        ]
    return books

def get_unique_genres():
    """
    Get all unique genres from the API.
    Falls back to hardcoded values if API fails.
    """
    genres = get_genres()
    if not genres:
        # Fallback to hardcoded genres if API call fails
        return [
            "Fiction", "Non-Fiction", "Mystery", "Fantasy",
            "Science Fiction", "Romance", "History"
        ]
    return genres

def get_unique_authors():
    """
    Get all unique authors from the API.
    Falls back to hardcoded values if API fails.
    """
    authors = get_authors()
    if not authors:
        # Fallback to hardcoded authors if API call fails
        return [
            "J.K. Rowling", "Stephen King", "Jane Austen",
            "Agatha Christie", "Neil Gaiman", "George R.R. Martin"
        ]
    return authors

def get_sample_recommendations():
    """
    Get recommendations from the API based on user profile.
    Falls back to hardcoded values if API call fails.
    """
    recommendations = get_recommendations()
    if not recommendations:
        # Fallback to hardcoded recommendations if API call fails
        return [
            {
                "title": "The Haunted Lighthouse",
                "author": "Stephen King",
                "description": (
                    "A chilling tale of an abandoned lighthouse haunted by past tragedies, "
                    "perfect for lovers of suspense and horror."
                ),
                "explanation": (
                    "Recommended because you enjoyed horror with strong atmospheric tension."
                ),
            },
            
        ]
    return recommendations