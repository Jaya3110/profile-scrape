#!/usr/bin/env python3
"""
Test Profile model serialization
"""

import json
from models import Profile, SocialLinks
from pydantic import ValidationError

def test_profile_serialization():
    """Test if Profile model can be serialized properly"""
    
    print("🧪 Testing Profile model serialization...")
    
    try:
        # Create a test profile
        profile = Profile(
            name="Linus Torvalds",
            title="Creator of Linux",
            company="Linux Foundation",
            bio="Software engineer and creator of the Linux kernel",
            extracted_from="https://github.com/torvalds",
            confidence=0.8,
            extraction_strategy="test"
        )
        
        print(f"✅ Profile created: {profile.name} - {profile.title}")
        
        # Test JSON serialization
        profile_dict = profile.model_dump()
        print(f"✅ Profile serialized to dict: {len(profile_dict)} fields")
        
        # Test JSON string conversion
        profile_json = profile.model_dump_json()
        print(f"✅ Profile converted to JSON: {len(profile_json)} characters")
        
        # Test deserialization
        profile_parsed = Profile.model_validate_json(profile_json)
        print(f"✅ Profile deserialized: {profile_parsed.name}")
        
        # Test with multiple profiles
        profiles = [profile]
        profiles_dict = [p.model_dump() for p in profiles]
        print(f"✅ Multiple profiles serialized: {len(profiles_dict)} profiles")
        
        # Test the exact structure the API needs
        api_response = {
            "success": True,
            "profiles": profiles_dict,
            "metadata": {
                "url": "https://github.com/torvalds",
                "scraped_at": 1234567890.0,
                "processing_time": 2.5,
                "profiles_found": len(profiles),
                "extraction_strategies_used": ["test"],
                "errors": []
            },
            "error": None
        }
        
        api_json = json.dumps(api_response)
        print(f"✅ API response serialized: {len(api_json)} characters")
        
        print("\n🎉 All serialization tests passed!")
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
    test_profile_serialization()

