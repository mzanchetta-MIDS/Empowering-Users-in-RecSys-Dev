import json
import numpy as np
#import requests
from sklearn.metrics.pairwise import cosine_similarity
#import pandas as pd

# # load unique_titles
# unique_titles = np.load('../../../inference/data/unique_titles.npy', allow_pickle=True)
# # Load book_embeddings
# book_embeddings = np.load("../../../inference/data/book_embeddings.npy", allow_pickle=True)

def small_recommend(user_embeddings):
    """_summary_

    Args:
        user_embeddings (json) : user embeddings of type json
        
    Returns:
        recommendations (list) : list of recommended books
    """
    
    # load unique_titles
    unique_titles = np.load('src/static/unique_titles.npy', allow_pickle=True)
    # Load book_embeddings
    book_embeddings = np.load("src/static/book_embeddings.npy", allow_pickle=True)
    
    # Get user_embeddings from json as list
    # unique_titles = unique_titles
    # book_embeddings = book_embeddings
    top_n = 3
    recommendations = []
    
    # y = json.loads(user_embeddings_json.text)
    # #print(y)
    # z = json.loads(y["body"])
    # #print(z)
    # user_embeddings = z["result"]["predictions"][0][0]
    user_embeddings_2d = np.expand_dims(user_embeddings, axis=0)
    cosine_sim = cosine_similarity(user_embeddings_2d, book_embeddings)
    #print(cosine_sim)
    top_n_indices = np.argsort(cosine_sim[0])[-top_n:][::-1]
    for i in top_n_indices:
        recommendations.append(unique_titles[i])
        
    return recommendations
