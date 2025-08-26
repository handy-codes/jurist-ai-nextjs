#!/usr/bin/env python3
"""
Script to test database connection for JuristAI
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def test_database_connection():
    """Test database connection using environment variables"""
    
    # Load environment variables
    load_dotenv()
    load_dotenv('backend/.env')  # Also try backend/.env
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in environment variables")
        print("💡 Make sure you have created .env or backend/.env file with DATABASE_URL")
        return False
    
    print("🔍 Testing database connection...")
    print(f"📍 Database URL: {DATABASE_URL[:50]}..." if len(DATABASE_URL) > 50 else DATABASE_URL)
    
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Test connection
        with engine.connect() as connection:
            # Test basic query
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            
            # Test table creation (basic SQL)
            connection.execute(text("SELECT 1"))
            
            print("✅ Database connection successful!")
            print(f"📊 PostgreSQL version: {version}")
            
            # Test if we can create tables
            try:
                connection.execute(text("""
                    CREATE TABLE IF NOT EXISTS connection_test (
                        id SERIAL PRIMARY KEY,
                        test_message TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                connection.execute(text("""
                    INSERT INTO connection_test (test_message) 
                    VALUES ('JuristAI connection test successful')
                """))
                
                result = connection.execute(text("SELECT COUNT(*) FROM connection_test"))
                count = result.fetchone()[0]
                
                print(f"✅ Table creation successful! Test records: {count}")
                
                # Clean up test table
                connection.execute(text("DROP TABLE IF EXISTS connection_test"))
                connection.commit()
                
            except Exception as table_error:
                print(f"⚠️  Basic connection works, but table operations failed: {table_error}")
                print("💡 This might be a permissions issue with your database")
            
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed!")
        print(f"🔍 Error details: {e}")
        
        # Provide helpful troubleshooting tips
        print("\n🛠️  Troubleshooting tips:")
        print("1. Check if your DATABASE_URL is correct")
        print("2. Verify your database password")
        print("3. Ensure your database server is running")
        print("4. Check if your IP address is allowed (for cloud databases)")
        print("5. Verify SSL requirements (most cloud databases require SSL)")
        
        return False

def check_environment_variables():
    """Check if all required environment variables are set"""
    
    print("\n🔍 Checking environment variables...")
    
    required_vars = [
        "DATABASE_URL",
        "GROQ_API_KEY", 
        "OPENAI_API_KEY",
        "SECRET_KEY"
    ]
    
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            masked_value = value[:10] + "..." if len(value) > 10 else value
            print(f"✅ {var}: {masked_value}")
        else:
            print(f"❌ {var}: Not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("💡 Add these to your .env or backend/.env file")
        return False
    else:
        print("\n✅ All required environment variables are set!")
        return True

def main():
    print("🚀 JuristAI Database Connection Test")
    print("=" * 40)
    
    # Check environment variables first
    env_ok = check_environment_variables()
    
    if not env_ok:
        print("\n❌ Please set up your environment variables first")
        sys.exit(1)
    
    # Test database connection
    db_ok = test_database_connection()
    
    if db_ok:
        print("\n🎉 Database setup is complete and working!")
        print("✅ You're ready to deploy your app")
    else:
        print("\n❌ Database connection failed")
        print("📖 Please check the DATABASE_SETUP_GUIDE.md for help")
        sys.exit(1)

if __name__ == "__main__":
    main()


