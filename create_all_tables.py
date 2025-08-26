from config.database import Base, engine
from models.database_models import User, Query, Feedback, Conversation, Message, LegalChunk

if __name__ == "__main__":
    print("Creating all tables (users, Query, Feedback, Conversation, Message) in the database...")
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully!")
