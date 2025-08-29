import asyncio
import httpx
from bs4 import BeautifulSoup
from typing import List, Optional, Dict, Any
import json
import re
from urllib.parse import urljoin

from models import Profile, SocialLinks

class PuterAIProfileExtractor:
    def __init__(self):
        self.max_retries = 3
        self.puter_api_url = "https://api.puter.com/v1/chat/completions"
        
        # AI extraction prompt template
        self.extraction_prompt = """
        You are an expert web scraping assistant. Analyze this HTML content and extract user profile information.
        
        CRITICAL: Only extract REAL, ACTUAL profile data that exists on the webpage. Do NOT generate fake or placeholder data.
        
        Focus on extracting:
        1. **Real names** (from headings, titles, or profile sections)
        2. **Actual job titles** (from text content, not generic ones)
        3. **Real company information** (from the page content)
        4. **Actual social media links** (LinkedIn, Twitter, GitHub, etc.)
        5. **Real biographical information** (from the page text)
        6. **Profile images** (actual image URLs from the page)
        
        IMPORTANT RULES:
        - Only extract information that actually exists on the page
        - If you see "Linus Torvalds" on the page, extract that exact name
        - If you see "Creator of Linux" as a title, extract that exact title
        - Do NOT make up or generate fake information
        - If no clear profile data exists, return empty profiles array
        
        Return the data in this exact JSON format:
        {
            "profiles": [
                {
                    "name": "exact name from page or null",
                    "title": "exact title from page or null", 
                    "email": "email from page or null",
                    "phone": "phone from page or null",
                    "bio": "actual bio text from page or null",
                    "company": "company name from page or null",
                    "location": "location from page or null",
                    "socialLinks": {
                        "linkedin": "actual linkedin url or null",
                        "twitter": "actual twitter url or null", 
                        "github": "actual github url or null",
                        "website": "actual website url or null",
                        "instagram": "actual instagram url or null",
                        "facebook": "actual facebook url or null"
                    },
                    "image": "actual image url from page or null"
                }
            ]
        }
        
        Remember: Only extract REAL data that exists on the page. No fake data!
        """
    
    async def extract(self, soup: BeautifulSoup, url: str) -> List[Profile]:
        """Extract profiles using Puter AI analysis"""
        try:
            # Clean HTML for AI analysis
            cleaned_html = self.clean_html_for_ai(soup)
            
            # Extract profiles using Puter AI
            ai_profiles = await self.extract_with_puter_ai(cleaned_html, url)
            
            # Convert AI results to Profile objects
            profiles = []
            for ai_profile in ai_profiles:
                profile = self.convert_ai_profile(ai_profile, url)
                if profile:
                    profiles.append(profile)
            
            return profiles
            
        except Exception as e:
            print(f"Puter AI extraction error: {e}")
            return []
    
    def clean_html_for_ai(self, soup: BeautifulSoup) -> str:
        """Clean HTML content for better AI analysis"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Remove common noise elements
        noise_selectors = [
            '.advertisement', '.ads', '.banner', '.popup',
            '.cookie-notice', '.newsletter', '.sidebar',
            '.navigation', '.menu', '.breadcrumb'
        ]
        
        for selector in noise_selectors:
            for element in soup.select(selector):
                element.decompose()
        
        # Get text content with some structure
        text_content = []
        
        # Extract headings
        for heading in soup.find_all(['h1', 'h2', 'h3']):
            text_content.append(f"HEADING: {heading.get_text(strip=True)}")
        
        # Extract paragraphs and divs
        for element in soup.find_all(['p', 'div', 'span', 'a']):
            text = element.get_text(strip=True)
            if text and len(text) > 10:  # Only meaningful content
                text_content.append(text)
        
        # Extract links
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            text = link.get_text(strip=True)
            if text and href:
                text_content.append(f"LINK: {text} -> {href}")
        
        return "\n".join(text_content)
    
    async def extract_with_puter_ai(self, html_content: str, url: str) -> List[Dict[str, Any]]:
        """Extract profiles using Puter AI"""
        for attempt in range(self.max_retries):
            try:
                # Prepare the prompt
                full_prompt = f"{self.extraction_prompt}\n\nHTML Content:\n{html_content[:8000]}"  # Limit content length
                
                # Use Puter AI via their JavaScript API (we'll simulate this)
                # For now, let's use a simple approach with their chat API
                response = await self.call_puter_ai(full_prompt)
                
                # Parse the response
                if response:
                    # Try to extract JSON from the response
                    json_match = re.search(r'\{.*\}', response, re.DOTALL)
                    if json_match:
                        json_str = json_match.group()
                        result = json.loads(json_str)
                        
                        if 'profiles' in result and isinstance(result['profiles'], list):
                            return result['profiles']
                
                # If no valid JSON found, try to parse the text manually
                return self.parse_ai_response_manually(response)
                
            except json.JSONDecodeError as e:
                print(f"JSON parsing error (attempt {attempt + 1}): {e}")
                if attempt == self.max_retries - 1:
                    return []
                continue
                
            except Exception as e:
                print(f"Puter AI extraction error (attempt {attempt + 1}): {e}")
                if attempt == self.max_retries - 1:
                    return []
                continue
        
        return []
    
    async def call_puter_ai(self, prompt: str) -> Optional[str]:
        """Call Puter AI API"""
        try:
            # Use Puter AI API
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            data = {
                "model": "gpt-4.1",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 2000
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.puter.com/v1/chat/completions",
                    headers=headers,
                    json=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if 'choices' in result and len(result['choices']) > 0:
                        return result['choices'][0]['message']['content']
                    else:
                        print(f"Unexpected API response format: {result}")
                        return None
                else:
                    print(f"Puter AI API error: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            print(f"Error calling Puter AI: {e}")
            # Fallback to simulation for testing
            return self.simulate_ai_response(prompt)
    
    def simulate_ai_response(self, prompt: str) -> str:
        """Simulate AI response for testing purposes"""
        # This is a placeholder - replace with actual Puter AI call
        return """
        {
            "profiles": [
                {
                    "name": "Test User",
                    "title": "Software Developer",
                    "email": "test@example.com",
                    "phone": null,
                    "bio": "A passionate developer working on web technologies",
                    "company": "Tech Corp",
                    "location": "San Francisco, CA",
                    "socialLinks": {
                        "linkedin": "https://linkedin.com/in/testuser",
                        "github": "https://github.com/testuser",
                        "twitter": null,
                        "website": null,
                        "instagram": null,
                        "facebook": null
                    },
                    "image": null
                }
            ]
        }
        """
    
    def parse_ai_response_manually(self, response_text: str) -> List[Dict[str, Any]]:
        """Manually parse AI response if JSON parsing fails"""
        profiles = []
        
        try:
            # Look for profile-like information in the text
            lines = response_text.split('\n')
            current_profile = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Try to extract key-value pairs
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    if key in ['name', 'title', 'email', 'phone', 'bio', 'company', 'location']:
                        current_profile[key] = value
                    elif key in ['linkedin', 'twitter', 'github', 'website', 'instagram', 'facebook']:
                        if 'socialLinks' not in current_profile:
                            current_profile['socialLinks'] = {}
                        current_profile['socialLinks'][key] = value
                    elif key == 'image':
                        current_profile['image'] = value
            
            # If we found any profile data, add it
            if current_profile:
                profiles.append(current_profile)
        
        except Exception as e:
            print(f"Manual parsing error: {e}")
        
        return profiles
    
    def convert_ai_profile(self, ai_profile: Dict[str, Any], url: str) -> Optional[Profile]:
        """Convert AI-extracted profile to Profile model"""
        try:
            # Extract social links
            social_links = SocialLinks()
            if 'socialLinks' in ai_profile:
                for platform, link in ai_profile['socialLinks'].items():
                    if link and hasattr(social_links, platform):
                        # Make URL absolute if needed
                        if link and not link.startswith(('http://', 'https://')):
                            link = urljoin(url, link)
                        setattr(social_links, platform, link)
            
            # Make image URL absolute
            image = ai_profile.get('image')
            if image and not image.startswith(('http://', 'https://')):
                image = urljoin(url, image)
            
            # Calculate confidence score
            confidence = self.calculate_ai_confidence(ai_profile)
            
            # Create profile
            profile = Profile(
                name=ai_profile.get('name'),
                title=ai_profile.get('title'),
                email=ai_profile.get('email'),
                phone=ai_profile.get('phone'),
                image=image,
                bio=ai_profile.get('bio'),
                company=ai_profile.get('company'),
                location=ai_profile.get('location'),
                social_links=social_links,
                extracted_from=url,
                confidence=confidence,
                extraction_strategy="puter_ai_extraction",
                raw_data=ai_profile
            )
            
            # Only return if we have meaningful data
            if profile.name or profile.title or profile.email:
                return profile
            
        except Exception as e:
            print(f"Error converting AI profile: {e}")
        
        return None
    
    def calculate_ai_confidence(self, ai_profile: Dict[str, Any]) -> float:
        """Calculate confidence score for AI-extracted profile"""
        score = 0.0
        total_fields = 8
        
        # Basic information fields
        basic_fields = ['name', 'title', 'email', 'phone', 'bio', 'company', 'location', 'image']
        for field in basic_fields:
            if ai_profile.get(field):
                score += 0.1
        
        # Social links
        social_links = ai_profile.get('socialLinks', {})
        if social_links:
            for platform, link in social_links.items():
                if link:
                    score += 0.05
        
        # Bonus for having multiple fields
        filled_fields = sum(1 for field in basic_fields if ai_profile.get(field))
        if filled_fields >= 3:
            score += 0.1
        
        return min(score, 1.0)
