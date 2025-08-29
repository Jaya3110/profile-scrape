#!/usr/bin/env python3
"""
Test script for Gemini API connection and available models
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

def test_gemini_connection():
    """Test Gemini API connection and list available models"""
    print("🔍 Testing Gemini API Connection...")
    
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env file")
        return False
    
    if api_key == 'your_gemini_api_key_here':
        print("❌ Please update your actual Gemini API key in .env file")
        return False
    
    try:
        # Configure the API
        genai.configure(api_key=api_key)
        print("✅ API configured successfully")
        
        # List available models
        print("\n📋 Available Models:")
        models = genai.list_models()
        for model in models:
            if 'gemini' in model.name.lower():
                print(f"  - {model.name}")
        
        # Test with the model we want to use
        print(f"\n🧪 Testing with 'gemini-2.0-flash'...")
        model = genai.GenerativeModel('gemini-2.0-flash')
        print("✅ Model created successfully")
        
        # Test a simple generation
        print("\n🚀 Testing simple text generation...")
        response = model.generate_content("Say 'Hello, Gemini is working!'")
        print(f"✅ Response: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test function"""
    print("🤖 Gemini API Connection Test")
    print("=" * 40)
    
    success = test_gemini_connection()
    
    if success:
        print("\n🎉 Gemini API is working correctly!")
        print("You can now use the AI extraction feature.")
    else:
        print("\n❌ Gemini API connection failed.")
        print("Please check your API key and try again.")

if __name__ == "__main__":
    main()
