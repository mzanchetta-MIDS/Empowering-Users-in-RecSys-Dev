
def get_unique_books():
    """
    Example function to return all unique books from training data.
    Will change later to query data source or read from DB.
    """
    return [
        "To Kill a Mockingbird - Harper Lee",
        "1984 - George Orwell",
        "Pride and Prejudice - Jane Austen",
        "The Great Gatsby - F. Scott Fitzgerald",
        "Moby Dick - Herman Melville",
        "The Catcher in the Rye - J.D. Salinger",
        "Brave New World - Aldous Huxley",
        "War and Peace - Leo Tolstoy",
        "Crime and Punishment - Fyodor Dostoevsky",
        "The Hobbit - J.R.R. Tolkien",
        "Fahrenheit 451 - Ray Bradbury",
        "Wuthering Heights - Emily Brontë",
        "Jane Eyre - Charlotte Brontë",
        "The Lord of the Rings - J.R.R. Tolkien",
        "The Brothers Karamazov - Fyodor Dostoevsky",
        "Great Expectations - Charles Dickens",
        "Les Misérables - Victor Hugo",
        "Catch-22 - Joseph Heller",
        "The Odyssey - Homer",
        "Dune - Frank Herbert",
        "Slaughterhouse-Five - Kurt Vonnegut",
        "The Road - Cormac McCarthy",
        "The Alchemist - Paulo Coelho",
        "One Hundred Years of Solitude - Gabriel García Márquez",
        "Anna Karenina - Leo Tolstoy",
        "The Picture of Dorian Gray - Oscar Wilde",
        "Beloved - Toni Morrison",
        "Dracula - Bram Stoker",
        "Frankenstein - Mary Shelley",
        "The Name of the Wind - Patrick Rothfuss"
    ]

def get_unique_genres():
    """
    Example function to return all unique genres from training data.
    """
    # Placeholder:
    return [
        "Fiction", "Non-Fiction", "Mystery", "Fantasy",
        "Science Fiction", "Romance", "History"
    ]

def get_unique_authors():
    """
    Example function to return all unique authors from training data.
    """
    # Placeholder:
    return [
        "J.K. Rowling", "Stephen King", "Jane Austen",
        "Agatha Christie", "Neil Gaiman", "George R.R. Martin"
    ]

def get_reading_goals(): 
    """
    Example function to return all unique authors from training data.
    """
    # Placeholder:
    return [
        "Older classics",
        "The latest best-sellers",
        "Award-winning books",
        "New genres I haven't explored",
        "Books similar to my favorites",
        "Less-reviewed gems",
        "Highly-rated selections",
        "Quick reads",
        "Long, immersive reads"
    ] 

def get_sample_recommendations():
    """
    Return a list of 3 recommended books, each with
    title, author, description, and an explanation (from LLM).
    In a real use-case, these would come from your
    recommendation engine + LLM.
    """
    # Placeholder:
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
        {
            "title": "Pride and Prejudice",
            "author": "Jane Austen",
            "description": (
                "A classic novel that offers sharp social commentary and a timeless love story, "
                "ideal for readers who love wit and romance."
            ),
            "explanation": (
                "Recommended because you love historical settings with rich character development."
            ),
        },
        {
            "title": "American Gods",
            "author": "Neil Gaiman",
            "description": (
                "A blend of myth, fantasy, and Americana, featuring old gods struggling "
                "to remain relevant in the modern world."
            ),
            "explanation": (
                "Recommended because you indicated interest in fantasy and mythology."
            ),
        },
    ]
