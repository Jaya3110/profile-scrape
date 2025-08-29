#!/usr/bin/env python3
"""
Simple test script to check extraction strategies
"""

import asyncio
import httpx
from bs4 import BeautifulSoup
from extractors.css_extractor import CSSProfileExtractor
from extractors.site_specific import SiteSpecificExtractor

async def test_simple_extraction():
    """Test extraction strategies with a simple approach"""
    
    url = "https://github.com/torvalds"
    print(f"🔍 Testing extraction for: {url}")
    
    # Fetch HTML
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            print(f"✅ HTML fetched: Status {response.status_code}")
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            print(f"✅ HTML parsed successfully")
            
            # Test CSS Extractor
            print("\n🎨 Testing CSS Extractor...")
            css_extractor = CSSProfileExtractor()
            css_profiles = css_extractor.extract(soup, url)
            print(f"📊 CSS Extractor found: {len(css_profiles)} profiles")
            
            if css_profiles:
                for i, profile in enumerate(css_profiles):
                    print(f"  Profile {i+1}: {profile.name} - {profile.title}")
                    print(f"    Company: {profile.company}")
                    print(f"    Bio: {profile.bio[:100] if profile.bio else 'None'}...")
            else:
                print("  ❌ No profiles found with CSS selectors")
            
            # Test Site-Specific Extractor
            print("\n🏢 Testing Site-Specific Extractor...")
            site_extractor = SiteSpecificExtractor()
            site_profiles = await site_extractor.extract(soup, url)
            print(f"📊 Site-Specific Extractor found: {len(site_profiles)} profiles")
            
            if site_profiles:
                for i, profile in enumerate(site_profiles):
                    print(f"  Profile {i+1}: {profile.name} - {profile.title}")
                    print(f"    Company: {profile.company}")
                    print(f"    Bio: {profile.bio[:100] if profile.bio else 'None'}...")
            else:
                print("  ❌ No profiles found with site-specific extraction")
            
            # Show some HTML structure
            print("\n🔍 HTML Structure Analysis:")
            
            # Look for the main profile name
            main_heading = soup.find('h1', class_='vcard-names')
            if main_heading:
                print(f"  Main heading: {main_heading.get_text(strip=True)}")
            
            # Look for bio text
            bio_elements = soup.find_all(['p', 'div'], class_=lambda x: x and 'bio' in x.lower())
            if bio_elements:
                for elem in bio_elements[:2]:
                    print(f"  Bio element: {elem.get_text(strip=True)[:100]}...")
            
            # Look for company info
            company_elements = soup.find_all(['span', 'div'], class_=lambda x: x and 'company' in x.lower())
            if company_elements:
                for elem in company_elements[:2]:
                    print(f"  Company element: {elem.get_text(strip=True)[:100]}...")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_simple_extraction())

