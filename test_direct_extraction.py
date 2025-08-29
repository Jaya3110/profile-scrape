#!/usr/bin/env python3
"""
Direct test script to bypass API and test extraction logic
"""

import asyncio
import httpx
from bs4 import BeautifulSoup
from scraping_service import ProfileScrapingService

async def test_direct_extraction():
    """Test extraction logic directly"""
    
    print("🔍 Testing extraction logic directly...")
    
    # Create scraping service
    service = ProfileScrapingService()
    
    # Test URL
    url = "https://github.com/torvalds"
    print(f"📝 Testing URL: {url}")
    
    try:
        # Test URL validation
        print("\n🔍 Step 1: URL Validation")
        is_valid = await service.validate_url(url)
        print(f"✅ URL valid: {is_valid}")
        
        if not is_valid:
            print("❌ URL validation failed")
            return
        
        # Test HTML fetching
        print("\n📥 Step 2: HTML Fetching")
        html_content = await service.fetch_html(url)
        if html_content:
            print(f"✅ HTML fetched: {len(html_content)} characters")
        else:
            print("❌ HTML fetching failed")
            return
        
        # Test profile scraping
        print("\n🤖 Step 3: Profile Scraping")
        profiles = await service.scrape_profiles(url)
        print(f"🎯 Final result: {len(profiles)} profiles")
        
        if profiles:
            for i, profile in enumerate(profiles):
                print(f"\n  Profile {i+1}:")
                print(f"    Name: {profile.name}")
                print(f"    Title: {profile.title}")
                print(f"    Company: {profile.company}")
                print(f"    Bio: {profile.bio[:100] if profile.bio else 'None'}...")
                print(f"    Confidence: {profile.confidence}")
                print(f"    Strategy: {profile.extraction_strategy}")
        else:
            print("❌ No profiles found")
            
            # Let's check what the individual extractors return
            print("\n🔍 Debug: Testing individual extractors...")
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Test CSS extractor
            css_profiles = service.css_extractor.extract(soup, url)
            print(f"🎨 CSS extractor: {len(css_profiles)} profiles")
            
            # Test site-specific extractor
            site_profiles = await service.site_extractor.extract(soup, url)
            print(f"🏢 Site-specific extractor: {len(site_profiles)} profiles")
            
            # Test AI extractor
            if service.ai_enabled:
                ai_profiles = await service.ai_extractor.extract(soup, url)
                print(f"🤖 AI extractor: {len(ai_profiles)} profiles")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_direct_extraction())

