import os
import subprocess
import sys
from pathlib import Path


def create_env_file():
    """Create .env file from template if it doesn't exist."""
    if not os.path.exists('.env'):
        print("Creating .env file...")
        with open('.env', 'w') as f:
            f.write("""# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
CLERK_SECRET_KEY=your_clerk_secret_key

# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Groq API
GROQ_API_KEY=your_groq_api_key

# OpenAI API (if needed)
OPENAI_API_KEY=your_openai_api_key
""")
        print("Please update the .env file with your actual credentials.")


def create_directories():
    """Create necessary directories if they don't exist."""
    directories = ['logs', 'feedback', 'config', 'models', 'utils', 'modules']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)


def install_requirements():
    """Install required packages."""
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip",
                          "install", "-r", "requirements.txt"])


def main():
    """Main setup function."""
    print("Starting setup...")

    # Create necessary directories
    create_directories()

    # Create .env file if it doesn't exist
    create_env_file()

    # Install requirements
    install_requirements()

    print("\nSetup completed!")
    print("\nNext steps:")
    print("1. Update the .env file with your actual credentials")
    print("2. Run the application with: streamlit run app.py")


if __name__ == "__main__":
    main()
