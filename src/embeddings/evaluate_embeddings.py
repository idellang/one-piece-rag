import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from tqdm.auto import tqdm


def calculate_performance(embeddings, evaluation_pairs, embedding_function, k=5):
    """
    Calculates and returns the Hit Rate and MRR for a given set of embeddings.
    This version is model-agnostic.

    Args:
        embeddings (np.ndarray): The pre-computed embeddings for all chunks.
        evaluation_pairs (list): A list of dictionaries, each with 'query' and 'correct_chunk_index'.
        embedding_function (function): A function that takes a query string and returns its embedding.
        k (int): The value for calculating Hit Rate@k.

    Returns:
        dict: A dictionary containing the 'hit_rate' and 'mrr'.
    """
    total_hits = 0
    total_reciprocal_rank = 0

    for item in tqdm(evaluation_pairs, desc="Evaluating Queries"):
        query = item['query']
        correct_chunk_index = item['correct_chunk_index']

        # Generate embedding for the query using the provided embedding function
        query_embedding = embedding_function(query)

        # Calculate cosine similarity
        similarities = cosine_similarity(query_embedding, embeddings)[0]

        # Get the indices of the top-k most similar chunks
        top_k_indices = np.argsort(similarities)[-k:][::-1].tolist()

        # Calculate metrics
        if correct_chunk_index in top_k_indices:
            total_hits += 1
            rank = top_k_indices.index(correct_chunk_index) + 1
            total_reciprocal_rank += 1 / rank

    num_queries = len(evaluation_pairs)
    hit_rate = total_hits / num_queries if num_queries > 0 else 0
    mrr = total_reciprocal_rank / num_queries if num_queries > 0 else 0

    return {"hit_rate": hit_rate, "mrr": mrr}
