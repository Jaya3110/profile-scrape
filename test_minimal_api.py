#!/usr/bin/env python3
"""
Minimal test API to isolate profile extraction issue
"""

import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import time
from scraping_service import ProfileScrapingService

app = FastAPI()

# Initialize scraping service
scraping_service = ProfileScrapingService()

@app.get("/test")
async def test_endpoint():
    """Simple test endpoint"""
    return {"message": "Test API is working", "timestamp": time.time()}

@app.post("/test-scrape")
async def test_scrape():
    """Test scraping without complex request validation"""
    try:
        print("🧪 Testing minimal scrape endpoint...")
        
        # Test with hardcoded URL
        url = "https://github.com/torvalds"
        
        # Call scraping service directly
        profiles = await scraping_service.scrape_profiles(url)
        print(f"🎯 Scraping service returned: {len(profiles)} profiles")
        
        if profiles:
            for i, profile in enumerate(profiles):
                print(f"  Profile {i+1}: {profile.name} - {profile.title}")
        
        # Create simple response
        response_data = {
            "success": True,
            "profiles_count": len(profiles),
            "profiles": [{"name": p.name, "title": p.title, "company": p.company} for p in profiles],
            "timestamp": time.time()
        }
        
        print(f"📤 Sending response with {len(profiles)} profiles")
        return response_data
        
    except Exception as e:
        print(f"❌ Error in test scrape: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "timestamp": time.time()}
        )

if __name__ == "__main__":
    print("🚀 Starting minimal test API...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
