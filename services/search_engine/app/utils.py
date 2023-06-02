import numpy as np


def cosine_similarity(v: np.ndarray, vectors: np.ndarray) -> float:
    """Compute cosine similarity between a vector and a list of vectors."""
    prod = np.dot(v, vectors.T)
    return prod / (np.linalg.norm(v) * np.linalg.norm(vectors, axis=1))


def euclidean_distance(v: np.ndarray, vectors: np.ndarray) -> float:
    """Compute euclidean distance between a vector and a list of vectors."""
    diff = v - vectors
    return np.linalg.norm(diff, axis=1)
