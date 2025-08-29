#!/usr/bin/env python3
"""
Debug script to test extraction process step by step
"""

import asyncio
import httpx
from bs4 import BeautifulSoup
import json
from extractors.css_extractor import CSSProfileExtractor
from extractors.puter_ai_extractor import PuterAIProfileExtractor
from extractors.site_specific import SiteSpecificExtractor

async def debug_extraction():
    """Debug the extraction process step by step"""
    
    # Test URL
    url = "https://github.com/torvalds"
    print(f"🔍 Testing extraction for: {url}")
    
    # Step 1: Fetch HTML
    print("\n📥 Step 1: Fetching HTML...")
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
            print(f"✅ HTML fetched: Status {response.status_code}")
            print(f"📏 Content length: {len(response.text)} characters")
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            print(f"✅ HTML parsed successfully")
            
            # Step 2: Test CSS Extractor
            print("\n🎨 Step 2: Testing CSS Extractor...")
            css_extractor = CSSProfileExtractor()
            css_profiles = css_extractor.extract(soup, url)
            print(f"📊 CSS Extractor found: {len(css_profiles)} profiles")
            
            if css_profiles:
                for i, profile in enumerate(css_profiles):
                    print(f"  Profile {i+1}: {profile.name} - {profile.title}")
            else:
                print("  ❌ No profiles found with CSS selectors")
            
            # Step 3: Test Site-Specific Extractor
            print("\n🏢 Step 3: Testing Site-Specific Extractor...")
            site_extractor = SiteSpecificExtractor()
            site_profiles = await site_extractor.extract(soup, url)
            print(f"📊 Site-Specific Extractor found: {len(site_profiles)} profiles")
            
            if site_profiles:
                for i, profile in enumerate(site_profiles):
                    print(f"  Profile {i+1}: {profile.name} - {profile.title}")
            else:
                print("  ❌ No profiles found with site-specific extraction")
            
            # Step 4: Test AI Extractor
            print("\n🤖 Step 4: Testing AI Extractor...")
            ai_extractor = PuterAIProfileExtractor()
            ai_profiles = await ai_extractor.extract(soup, url)
            print(f"📊 AI Extractor found: {len(ai_profiles)} profiles")
            
            if ai_profiles:
                for i, profile in enumerate(ai_profiles):
                    print(f"  Profile {i+1}: {profile.name} - {profile.title}")
            else:
                print("  ❌ No profiles found with AI extraction")
            
            # Step 5: Show HTML structure
            print("\n🔍 Step 5: Analyzing HTML structure...")
            
            # Look for common profile indicators
            name_elements = soup.find_all(['h1', 'h2', 'h3'], class_=lambda x: x and any(word in x.lower() for word in ['name', 'title', 'profile']))
            print(f"📝 Potential name elements: {len(name_elements)}")
            
            for elem in name_elements[:3]:  # Show first 3
                print(f"  - {elem.name}.{elem.get('class', [])}: {elem.get_text(strip=True)[:100]}")
            
            # Look for social links
            social_links = soup.find_all('a', href=lambda x: x and any(site in x for site in ['linkedin.com', 'twitter.com', 'github.com']))
            print(f"🔗 Social links found: {len(social_links)}")
            
            # Look for profile containers
            profile_containers = soup.find_all(['div', 'section'], class_=lambda x: x and any(word in x.lower() for word in ['profile', 'user', 'member', 'team']))
            print(f"📦 Profile containers: {len(profile_containers)}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_extraction())

