#!/usr/bin/env python3
"""
Test script for debugging scraping issues
"""

import asyncio
import httpx
from bs4 import BeautifulSoup
import json

async def test_url_accessibility(url):
    """Test if a URL is accessible"""
    print(f"🔍 Testing URL: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            print(f"✅ Status Code: {response.status_code}")
            print(f"✅ Content-Type: {response.headers.get('content-type', 'Unknown')}")
            print(f"✅ Content Length: {len(response.text)} characters")
            
            # Check if it's HTML
            if 'text/html' in response.headers.get('content-type', ''):
                soup = BeautifulSoup(response.text, 'html.parser')
                title = soup.find('title')
                if title:
                    print(f"✅ Page Title: {title.get_text()[:100]}...")
                
                # Check for common anti-bot indicators
                if 'blocked' in response.text.lower() or 'captcha' in response.text.lower():
                    print("⚠️  Possible anti-bot protection detected")
                
                return True
            else:
                print("❌ Not HTML content")
                return False
                
    except Exception as e:
        print(f"❌ Error accessing URL: {e}")
        return False

async def test_api_endpoint():
    """Test the API endpoint directly"""
    print("\n🔧 Testing API Endpoint...")
    
    test_urls = [
        "https://github.com/octocat",  # GitHub profile (usually accessible)
        "https://httpbin.org/html",    # Test HTML page
        "https://example.com",         # Simple static page
    ]
    
    for url in test_urls:
        print(f"\n--- Testing: {url} ---")
        await test_url_accessibility(url)

async def test_linkedin_specific():
    """Test LinkedIn with different approaches"""
    print("\n🔗 Testing LinkedIn Access...")
    
    linkedin_urls = [
        "https://www.linkedin.com/in/satyanadella/",
        "https://www.linkedin.com/company/microsoft/",
    ]
    
    for url in linkedin_urls:
        print(f"\n--- Testing LinkedIn: {url} ---")
        await test_url_accessibility(url)

async def main():
    """Main test function"""
    print("🧪 AI Profile Scraper - Debug Test")
    print("=" * 50)
    
    # Test basic API functionality
    await test_api_endpoint()
    
    # Test LinkedIn specifically
    await test_linkedin_specific()
    
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print("- GitHub profiles usually work well")
    print("- LinkedIn has strong anti-scraping protection")
    print("- Try company team pages instead of individual profiles")
    print("- Consider using public company pages")

if __name__ == "__main__":
    asyncio.run(main())
