#!/usr/bin/env python3
"""
Script to generate a secure secret key for JWT tokens
"""

import secrets
import string

def generate_secret_key(length=32):
    """Generate a cryptographically secure secret key"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def main():
    print("🔐 Generating secure SECRET_KEY for JuristAI...")
    print("=" * 50)
    
    # Generate different length keys
    print(f"32 characters: {generate_secret_key(32)}")
    print(f"64 characters: {generate_secret_key(64)}")
    
    print("\n💡 Copy one of these keys to use as your SECRET_KEY in environment variables")
    print("⚠️  Keep this key secure and never commit it to version control!")

if __name__ == "__main__":
    main()


