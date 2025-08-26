from config.database import engine
from models.database_models import Base  # ✅ Correct import path

def init_db():
    print("🔧 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

if __name__ == "__main__":
    init_db()




# from config.database import engine
# from models.database_models import Base

# def init_db():
#     Base.metadata.create_all(bind=engine)

# if __name__ == "__main__":
#     print("Creating database tables...")
#     init_db()
#     print("Database tables created successfully!") 