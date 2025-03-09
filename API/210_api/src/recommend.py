# Embeddings to Recommendations

# Imports


filter = {'keep': {'title': set(), 'authors': set(), 'categories': set()},
          'remove': {'title': set(), 'authors': set(), 'categories': set([i for i in range(100)])}}

def recommend(self, session_info, filter=filter, top_k=10, path='embeddings/book_embeddings.npy'):
    """
    Recommend top_k books based on cosine similarity using book embeddings.
    :param filter: Dictionary with 'keep' and 'remove' filters.
    :param input_book_title: Title of the book to find recommendations for.
    :param top_k: Number of recommendations to return.
    :param path: Path to embeddings if they need to be loaded.
    :return: DataFrame with top_k recommendations.
    """
    from sklearn.metrics.pairwise import cosine_similarity

    # Ensure that embeddings are loaded
    if self.full_book_embeddings is None:
        self.load_book_embeddings(path, self.full_book_embeddings_copy)

    # Apply filtering logic
    self.full_book_embeddings_copy = self.full_book_embeddings.copy()
    
    # Apply 'keep' filters
    for key, value_set in filter.get('keep', {}).items():
        if value_set:
            self.full_book_embeddings_copy = self.full_book_embeddings_copy[
                self.full_book_embeddings_copy[key].isin(value_set)]
    
    # Apply 'remove' filters
    for key, value_set in filter.get('remove', {}).items():
        if value_set:
            self.full_book_embeddings_copy = self.full_book_embeddings_copy[
                ~self.full_book_embeddings_copy[key].isin(value_set)]

    # Get user embeddings
    user_embeddings = self.user_model(session_info)
    
    # Get book embeddings (make sure to extract relevant embeddings)
    book_embeddings = np.vstack(self.full_book_embeddings_copy['embeddings'].values)

    # Compute Cosine Similarity between user and book embeddings
    similarity_scores = cosine_similarity(user_embeddings, book_embeddings)

    # Add similarity scores to the dataframe
    self.full_book_embeddings_copy['similarity'] = similarity_scores.mean(axis=0)

    # Get Top-K Recommendations
    recommendations = self.full_book_embeddings_copy.sort_values(by='similarity', ascending=False).head(top_k)

    return recommendations[['title', 'authors', 'categories', 'similarity']]