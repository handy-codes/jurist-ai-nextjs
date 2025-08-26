# config/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if DATABASE_URL is None:
    raise ValueError("❌ DATABASE_URL is not set. Please check your .env file.")

# Use SSL for PostgreSQL connections (Supabase requires SSL)
if DATABASE_URL.startswith("postgresql"):
    engine = create_engine(DATABASE_URL, pool_pre_ping=True,
                           connect_args={"sslmode": "require"})
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# import os
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()

# # --- Aiven PostgreSQL connection string (with pgvector support) ---
# DATABASE_URL = os.getenv("DATABASE_URL")

# # Fix 'postgres://' to 'postgresql://' for SQLAlchemy compatibility
# if DATABASE_URL.startswith("postgres://"):
#     DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# # Sanity check for debugging
# if DATABASE_URL is None:
#     raise ValueError("❌ DATABASE_URL is not set. Please check your .env file.")

# # Create the SQLAlchemy engine
# engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# # Create a sessionmaker factory
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # Base class for declaring ORM models
# Base = declarative_base()

# # Dependency for getting a DB session in other modules
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# import os
# from dotenv import load_dotenv

# load_dotenv()

# # Get database URL from environment variable
# DATABASE_URL = os.getenv("DATABASE_URL")

# # Create SQLAlchemy engine with explicit PostgreSQL dialect
# engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# # Create SessionLocal class
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # Create Base class
# Base = declarative_base()

# # Dependency to get DB session


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
