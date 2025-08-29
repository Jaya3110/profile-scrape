#!/usr/bin/env python3
"""
Test main API request format
"""

import json
from models import ScrapingRequest, ScrapingResponse, ScrapingMetadata
from pydantic import ValidationError

def test_main_api_format():
    """Test the exact request/response format used by the main API"""
    
    print("🧪 Testing main API request/response format...")
    
    try:
        # Test 1: Create ScrapingRequest
        print("\n📝 Test 1: ScrapingRequest validation")
        request_data = {
            "url": "https://github.com/torvalds",
            "options": {},
            "max_profiles": 10,
            "timeout": 30
        }
        
        request = ScrapingRequest(**request_data)
        print(f"✅ ScrapingRequest created: {request.url}")
        
        # Test 2: Create mock profiles
        print("\n👤 Test 2: Profile creation")
        from models import Profile, SocialLinks
        
        profile1 = Profile(
            name="Linus Torvalds",
            title="Creator of Linux",
            company="Linux Foundation",
            extracted_from="https://github.com/torvalds",
            confidence=0.8,
            extraction_strategy="test"
        )
        
        profile2 = Profile(
            name="Test User",
            title="Developer",
            company="Tech Corp",
            extracted_from="https://github.com/torvalds",
            confidence=0.6,
            extraction_strategy="test"
        )
        
        profiles = [profile1, profile2]
        print(f"✅ Profiles created: {len(profiles)} profiles")
        
        # Test 3: Create ScrapingMetadata
        print("\n📊 Test 3: ScrapingMetadata creation")
        metadata = ScrapingMetadata(
            url=str(request.url),
            scraped_at=1234567890.0,
            processing_time=2.5,
            profiles_found=len(profiles),
            extraction_strategies_used=["test"],
            errors=[]
        )
        print(f"✅ Metadata created: {metadata.profiles_found} profiles found")
        
        # Test 4: Create ScrapingResponse
        print("\n📤 Test 4: ScrapingResponse creation")
        response = ScrapingResponse(
            success=True,
            profiles=profiles,
            metadata=metadata,
            error=None
        )
        print(f"✅ Response created: {len(response.profiles)} profiles")
        
        # Test 5: Serialize response
        print("\n🔄 Test 5: Response serialization")
        response_dict = response.model_dump()
        response_json = response.model_dump_json()
        
        print(f"✅ Response serialized: {len(response_json)} characters")
        print(f"✅ Profiles in response: {len(response_dict['profiles'])}")
        
        # Test 6: Verify profile data
        print("\n🔍 Test 6: Profile data verification")
        for i, profile in enumerate(response_dict['profiles']):
            print(f"  Profile {i+1}: {profile['name']} - {profile['title']}")
        
        print("\n🎉 All main API format tests passed!")
        return True
        
    except ValidationError as e:
        print(f"❌ Validation error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_main_api_format()

