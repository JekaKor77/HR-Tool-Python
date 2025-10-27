#!/usr/bin/env python3
"""
Setup script for HR CV Analysis System
This script helps you set up the environment file and test the application.
"""

import os
import secrets
import sys

def create_env_file():
    """Create .env file with sample configuration"""
    env_content = """# HR CV Analysis System - Environment Configuration
# Replace the placeholder values with your actual API keys

# OpenAI API Key (required)
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# Flask Secret Key (required)
# Generate a random secret key for session management
SECRET_KEY={}

# Flask Environment
# Set to 'development' for debug mode, 'production' for production
FLASK_ENV=development
""".format(secrets.token_hex(32))
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✓ Created .env file with sample configuration")
    print("⚠  Please edit .env file and add your OpenAI API key")

def main():
    """Main setup function"""
    print("HR CV Analysis System - Setup")
    print("=" * 40)
    
    # Check if .env already exists
    if os.path.exists('.env'):
        print("✓ .env file already exists")
    else:
        create_env_file()
    
    print("\nNext steps:")
    print("1. Edit .env file and add your OpenAI API key")
    print("2. Run: source venv/bin/activate")
    print("3. Run: python app.py")
    print("4. Open: http://localhost:5000")
    
    print("\nTo get your OpenAI API key:")
    print("1. Go to: https://platform.openai.com/api-keys")
    print("2. Sign in or create an account")
    print("3. Create a new API key")
    print("4. Copy the key and paste it in .env file")

if __name__ == "__main__":
    main()
