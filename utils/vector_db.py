# vector_db.py

from sqlalchemy import text
from config.database import SessionLocal
from utils.embedding import get_embedding


def search_similar_chunks(query, k=5):
    embedding = get_embedding(query)

    # Convert list to SQL vector string format: '[0.1, 0.2, ...]'
    embedding_str = f"'[{','.join([str(x) for x in embedding])}]'"

    sql = text(f"""
        SELECT id, text, source
        FROM legal_chunks
        ORDER BY embedding <-> {embedding_str}::vector
        LIMIT :k
    """)

    with SessionLocal() as db:
        results = db.execute(sql, {"k": k}).fetchall()

    return results


def add_chunk(chunk, source, embedding=None):
    from utils.embedding import get_embedding
    # If embedding is not provided, generate it
    if embedding is None:
        embedding = get_embedding(chunk)
    # Ensure embedding is a list, not numpy array
    if hasattr(embedding, "tolist"):
        embedding = embedding.tolist()
    # ...existing code to insert chunk and embedding into DB...


def query_similar_chunks(embedding, k=5):
    # Ensure embedding is a list, not numpy array
    if hasattr(embedding, "tolist"):
        embedding = embedding.tolist()
    sql = "SELECT id, text, source FROM legal_chunks ORDER BY embedding <-> %(embedding)s LIMIT %(k)s"
    params = {'embedding': embedding, 'k': k}
    # ...existing code to execute query...















# vector_db.py

# from sqlalchemy import text
# from config.database import SessionLocal
# from utils.embedding import get_embedding
# import psycopg2
# from psycopg2 import ProgrammingError
# import streamlit as st

# from pgvector.psycopg2 import register_vector  # Add this import


# try:
#     # Establish a raw psycopg2 connection
#     raw_conn = psycopg2.connect(
#         dbname="your_db_name",
#         user="your_db_user",
#         password="your_db_password",
#         host="your_db_host",
#         port="your_db_port"
#     )
#     register_vector(raw_conn, "vector")
#     # ...existing code...
# except ProgrammingError as e:
#     st.error(
#         "Database error: pgvector extension is not installed. "
#         "Please run `CREATE EXTENSION IF NOT EXISTS vector;` on your PostgreSQL database."
#     )
#     raise


# def search_similar_chunks(query, k=5):
#     embedding = get_embedding(query)

#     # Convert list to SQL vector string format: '[0.1, 0.2, ...]'
#     embedding_str = f"'[{','.join([str(x) for x in embedding])}]'"

#     sql = text(f"""
#         SELECT id, text, source
#         FROM legal_chunks
#         ORDER BY embedding <-> {embedding_str}::vector
#         LIMIT :k
#     """)

#     with SessionLocal() as db:
#         results = db.execute(sql, {"k": k}).fetchall()

#     return results


# def add_chunk(chunk, source, embedding=None):
#     from utils.embedding import get_embedding
#     # If embedding is not provided, generate it
#     if embedding is None:
#         embedding = get_embedding(chunk)
#     # Ensure embedding is a list, not numpy array
#     if hasattr(embedding, "tolist"):
#         embedding = embedding.tolist()
#     # ...existing code to insert chunk and embedding into DB...


# def query_similar_chunks(embedding, k=5):
#     # Ensure embedding is a list, not numpy array
#     if hasattr(embedding, "tolist"):
#         embedding = embedding.tolist()
#     sql = "SELECT id, text, source FROM legal_chunks ORDER BY embedding <-> %(embedding)s LIMIT %(k)s"
#     params = {'embedding': embedding, 'k': k}
#     # ...existing code to execute query...
