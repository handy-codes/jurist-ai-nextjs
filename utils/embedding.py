# utils/embedding.py

from sentence_transformers import SentenceTransformer

# Load the local model once
model = SentenceTransformer("all-MiniLM-L6-v2")


def get_embedding(text: str) -> list[float]:
    """Generate a vector embedding from text."""
    embedding = model.encode(text)
    # Ensure output is always a list, not numpy array
    if hasattr(embedding, "tolist"):
        return embedding.tolist()
    return list(embedding)
