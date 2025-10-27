#!/usr/bin/env python3
"""
Simple test script to verify the HR CV Analysis System works correctly.
Run this before starting the main application.
"""

import os
import sys
import tempfile
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import flask
        print("✓ Flask imported successfully")
    except ImportError as e:
        print(f"✗ Flask import failed: {e}")
        return False
    
    try:
        import openai
        print("✓ OpenAI imported successfully")
    except ImportError as e:
        print(f"✗ OpenAI import failed: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✓ python-dotenv imported successfully")
    except ImportError as e:
        print(f"✗ python-dotenv import failed: {e}")
        return False
    
    return True

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        from config import Config
        print("✓ Config class loaded successfully")
        
        # Check if required attributes exist
        required_attrs = ['SECRET_KEY', 'OPENAI_API_KEY', 'UPLOAD_FOLDER', 'MAX_CONTENT_LENGTH']
        for attr in required_attrs:
            if hasattr(Config, attr):
                print(f"✓ {attr} configured")
            else:
                print(f"✗ {attr} missing")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Config loading failed: {e}")
        return False

def test_services():
    """Test service modules"""
    print("\nTesting services...")
    
    try:
        from services.cv_analyzer import CVAnalyzer
        print("✓ CVAnalyzer imported successfully")
    except Exception as e:
        print(f"✗ CVAnalyzer import failed: {e}")
        return False
    
    try:
        from services.quiz_generator import QuizGenerator
        print("✓ QuizGenerator imported successfully")
    except Exception as e:
        print(f"✗ QuizGenerator import failed: {e}")
        return False
    
    try:
        from services.response_evaluator import ResponseEvaluator
        print("✓ ResponseEvaluator imported successfully")
    except Exception as e:
        print(f"✗ ResponseEvaluator import failed: {e}")
        return False
    
    return True

def test_utils():
    """Test utility modules"""
    print("\nTesting utilities...")
    
    try:
        from utils.file_processor import FileProcessor
        print("✓ FileProcessor imported successfully")
    except Exception as e:
        print(f"✗ FileProcessor import failed: {e}")
        return False
    
    return True

def test_directories():
    """Test that required directories exist"""
    print("\nTesting directories...")
    
    required_dirs = [
        'services',
        'utils', 
        'templates',
        'static/css',
        'static/js',
        'uploads'
    ]
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✓ {dir_path} exists")
        else:
            print(f"✗ {dir_path} missing")
            return False
    
    return True

def test_env_file():
    """Test environment file setup"""
    print("\nTesting environment setup...")
    
    if os.path.exists('.env'):
        print("✓ .env file exists")
        return True
    else:
        print("⚠ .env file not found - you'll need to create one")
        print("  Create .env file with:")
        print("  OPENAI_API_KEY=your_openai_api_key_here")
        print("  SECRET_KEY=your_secret_key_here")
        print("  FLASK_ENV=development")
        return False

def main():
    """Run all tests"""
    print("HR CV Analysis System - Test Suite")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_config,
        test_services,
        test_utils,
        test_directories,
        test_env_file
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! The application should work correctly.")
        print("\nTo start the application:")
        print("1. Create a .env file with your OpenAI API key")
        print("2. Run: python app.py")
        print("3. Open: http://localhost:5000")
    else:
        print("✗ Some tests failed. Please fix the issues before running the application.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
