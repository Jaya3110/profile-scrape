import asyncio
import httpx
import time
import random
from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup
import re
import json
import os
from urllib.parse import urljoin, urlparse
from fake_useragent import UserAgent
import google.generativeai as genai
from datetime import datetime, timedelta
from dotenv import load_dotenv

from models import Profile, SocialLinks, CacheEntry
from extractors.css_extractor import CSSProfileExtractor
from extractors.ai_extractor import AIProfileExtractor
from extractors.site_specific import SiteSpecificExtractor

class ProfileScrapingService:
    def __init__(self):
        self.cache: Dict[str, CacheEntry] = {}
        self.cache_ttl_hours = 24
        self.user_agent = UserAgent()
        
        # Initialize extractors
        self.css_extractor = CSSProfileExtractor()
        self.ai_extractor = AIProfileExtractor()
        self.site_extractor = SiteSpecificExtractor()
        
        # Configure AI (Gemini 2.0 Flash)
        self.setup_ai()
    
    def setup_ai(self):
        """Setup AI extraction with Gemini 2.0 Flash"""
        # Load environment variables
        load_dotenv()
        
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key and api_key != 'your_gemini_api_key_here':
            try:
                genai.configure(api_key=api_key)
                # Initialize the AI extractor with Gemini 2.0 Flash model
                gemini_model = genai.GenerativeModel('gemini-2.0-flash')
                self.ai_extractor = AIProfileExtractor(gemini_model)
                print("✅ AI extraction enabled with Gemini 2.0 Flash")
                self.ai_enabled = True
            except Exception as e:
                print(f"❌ Failed to configure Gemini AI: {e}")
                print("⚠️  AI extraction will be disabled")
                self.ai_enabled = False
        else:
            print("⚠️  GEMINI_API_KEY not found or not configured")
            print("⚠️  AI extraction will be disabled")
            self.ai_enabled = False
    
    async def validate_url(self, url) -> bool:
        """Validate if URL is accessible and returns HTML content"""
        try:
            # Convert Pydantic HttpUrl to string if needed
            url_str = str(url)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url_str, headers=headers)
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    # Accept any content type that contains 'html' or is text
                    return 'html' in content_type or 'text' in content_type
                elif response.status_code in [403, 429, 401]:
                    # Some sites return these status codes but still have content
                    return True
                elif response.status_code == 404:
                    # Page not found
                    return False
                else:
                    # For other status codes, try to get content anyway
                    return True
        except Exception as e:
            print(f"URL validation error: {e}")
            return False
    
    async def scrape_profiles(self, url, max_profiles: int = 10) -> List[Profile]:
        """Main method to scrape profiles using multiple strategies"""
        # Convert Pydantic HttpUrl to string if needed
        url_str = str(url)
        
        # Check cache first
        cached_result = self.get_cached_result(url_str)
        if cached_result:
            return cached_result[:max_profiles]
        
        try:
            # Fetch HTML content
            html_content = await self.fetch_html(url_str)
            if not html_content:
                return []
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Try different extraction strategies
            profiles = []
            strategies_used = []
            
            # Strategy 1: Site-specific extraction (highest priority)
            site_profiles = await self.site_extractor.extract(soup, url)
            if site_profiles:
                profiles.extend(site_profiles)
                strategies_used.append("site_specific")
            
            # Strategy 2: CSS selector extraction
            css_profiles = self.css_extractor.extract(soup, url)
            if css_profiles:
                profiles.extend(css_profiles)
                strategies_used.append("css_selectors")
            
            # Strategy 3: AI-powered extraction (if available)
            if self.ai_enabled and len(profiles) < max_profiles:
                ai_profiles = await self.ai_extractor.extract(soup, url)
                if ai_profiles:
                    profiles.extend(ai_profiles)
                    strategies_used.append("ai_extraction")
            
            # Remove duplicates and limit results
            unique_profiles = self.remove_duplicates(profiles)
            final_profiles = unique_profiles[:max_profiles]
            
            # Cache the results
            self.cache_result(url_str, final_profiles)
            
            return final_profiles
            
        except Exception as e:
            print(f"Scraping error: {e}")
            return []
    
    async def fetch_html(self, url: str) -> Optional[str]:
        """Fetch HTML content from URL with proper headers and LinkedIn-specific handling"""
        try:
            # Check if this is a LinkedIn URL and needs special handling
            if 'linkedin.com' in url:
                return await self.fetch_linkedin_html(url)
            
            headers = {
                'User-Agent': self.user_agent.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)
                
                # Don't raise for status - handle different response codes
                if response.status_code == 200:
                    return response.text
                elif response.status_code in [403, 429, 401]:
                    # Some sites return these but still have content
                    return response.text
                else:
                    # For other status codes, try to get content anyway
                    return response.text
                
        except Exception as e:
            print(f"Error fetching HTML: {e}")
            return None
    
    async def fetch_linkedin_html(self, url: str) -> Optional[str]:
        """Special handling for LinkedIn URLs with enhanced anti-detection measures"""
        try:
            # Enhanced headers for LinkedIn
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
                'DNT': '1',
            }
            
            # Try multiple approaches for LinkedIn
            approaches = [
                ('direct', url, headers),
                ('google_cache', f"https://webcache.googleusercontent.com/search?q=cache:{url}", headers),
                ('archive_org', await self.get_archive_url(url), headers) if await self.get_archive_url(url) else None
            ]
            
            # Filter out None approaches
            approaches = [a for a in approaches if a is not None]
            
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                for approach_name, approach_url, approach_headers in approaches:
                    try:
                        print(f"🔍 Trying LinkedIn {approach_name} approach...")
                        
                        # Add delay to avoid rate limiting
                        await asyncio.sleep(random.uniform(2, 5))
                        
                        response = await client.get(approach_url, headers=approach_headers)
                        
                        if response.status_code == 200:
                            content = response.text
                            if self.has_linkedin_profile_content(content):
                                print(f"✅ LinkedIn {approach_name} approach successful!")
                                return content
                        elif response.status_code == 429:
                            print(f"⚠️  Rate limited on {approach_name}, trying next approach...")
                            continue
                        
                    except Exception as e:
                        print(f"❌ LinkedIn {approach_name} approach failed: {e}")
                        continue
            
            print("❌ All LinkedIn approaches failed")
            return None
            
        except Exception as e:
            print(f"Error fetching LinkedIn HTML: {e}")
            return None
    
    async def get_archive_url(self, url: str) -> Optional[str]:
        """Get archived version URL from Archive.org"""
        try:
            api_url = f"https://archive.org/wayback/available?url={url}"
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(api_url)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('archived_snapshots', {}).get('closest', {}).get('available'):
                        return data['archived_snapshots']['closest']['url']
        except:
            pass
        return None
    
    def has_linkedin_profile_content(self, html: str) -> bool:
        """Check if HTML contains actual LinkedIn profile content"""
        if not html or len(html) < 1000:
            return False
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for profile indicators
        profile_indicators = [
            'pv-text-details',
            'text-heading-xlarge',
            'profile-picture',
            'pv-top-card',
            'experience-section',
            'education-section'
        ]
        
        for indicator in profile_indicators:
            if soup.find(class_=lambda x: x and indicator in x):
                return True
        
        # Check for profile-like content in text
        text = soup.get_text().lower()
        profile_text_indicators = [
            'experience at',
            'education at',
            'connections',
            'followers',
            'years of experience'
        ]
        
        indicator_count = 0
        for indicator in profile_text_indicators:
            if indicator in text:
                indicator_count += 1
        
        return indicator_count >= 2
    
    def remove_duplicates(self, profiles: List[Profile]) -> List[Profile]:
        """Remove duplicate profiles based on name and email with improved logic"""
        seen = set()
        unique_profiles = []
        
        # Sort profiles by confidence (highest first) to keep best quality
        sorted_profiles = sorted(profiles, key=lambda x: x.confidence, reverse=True)
        
        for profile in sorted_profiles:
            # Create a unique identifier based on name and company
            identifier = f"{profile.name or 'unknown'}_{profile.company or 'no-company'}"
            
            # Also check for very similar names (typos, variations)
            if self.is_similar_profile(profile, unique_profiles):
                continue
                
            if identifier not in seen:
                seen.add(identifier)
                unique_profiles.append(profile)
        
        return unique_profiles
    
    def is_similar_profile(self, profile: Profile, existing_profiles: List[Profile]) -> bool:
        """Check if profile is too similar to existing ones"""
        if not profile.name:
            return False
            
        for existing in existing_profiles:
            if not existing.name:
                continue
                
            # Check if names are very similar (typos, variations)
            if self.names_are_similar(profile.name, existing.name):
                # If they're from the same company, likely duplicates
                if profile.company and existing.company and profile.company == existing.company:
                    return True
                    
                # If they have very similar titles, likely duplicates
                if profile.title and existing.title and self.titles_are_similar(profile.title, existing.title):
                    return True
        
        return False
    
    def names_are_similar(self, name1: str, name2: str) -> bool:
        """Check if two names are very similar (typos, variations)"""
        if not name1 or not name2:
            return False
            
        # Convert to lowercase and remove extra spaces
        name1_clean = ' '.join(name1.lower().split())
        name2_clean = ' '.join(name2.lower().split())
        
        # Exact match
        if name1_clean == name2_clean:
            return True
            
        # Check for common variations
        if name1_clean.replace(' ', '') == name2_clean.replace(' ', ''):
            return True
            
        # Check for initials vs full names
        if self.is_initials_vs_full_name(name1_clean, name2_clean):
            return True
            
        return False
    
    def is_initials_vs_full_name(self, name1: str, name2: str) -> bool:
        """Check if one name is initials and the other is full name"""
        # Split names into parts
        parts1 = name1.split()
        parts2 = name2.split()
        
        # Check if one is initials (single letters)
        if len(parts1) == 1 and len(parts2) > 1:
            if len(parts1[0]) == 1 and parts1[0].upper() == parts1[0]:
                # Check if initials match first letters of full name
                if parts1[0].upper() == parts2[0][0].upper():
                    return True
                    
        elif len(parts2) == 1 and len(parts1) > 1:
            if len(parts2[0]) == 1 and parts2[0].upper() == parts2[0]:
                # Check if initials match first letters of full name
                if parts2[0].upper() == parts1[0][0].upper():
                    return True
        
        return False
    
    def titles_are_similar(self, title1: str, title2: str) -> bool:
        """Check if two titles are very similar"""
        if not title1 or not title2:
            return False
            
        # Convert to lowercase and remove extra spaces
        title1_clean = ' '.join(title1.lower().split())
        title2_clean = ' '.join(title2.lower().split())
        
        # Exact match
        if title1_clean == title2_clean:
            return True
            
        # Check for common variations
        if title1_clean.replace(' ', '') == title2_clean.replace(' ', ''):
            return True
            
        return False
    
    def get_cached_result(self, url: str) -> Optional[List[Profile]]:
        """Get cached result if available and not expired"""
        if url in self.cache:
            entry = self.cache[url]
            if datetime.now() < entry.expires_at:
                return entry.profiles
            else:
                # Remove expired entry
                del self.cache[url]
        return None
    
    def cache_result(self, url: str, profiles: List[Profile]):
        """Cache scraping results"""
        expires_at = datetime.now() + timedelta(hours=self.cache_ttl_hours)
        
        cache_entry = CacheEntry(
            url=url,
            profiles=profiles,
            cached_at=datetime.now(),
            expires_at=expires_at
        )
        
        self.cache[url] = cache_entry
        
        # Clean up old cache entries
        self.cleanup_cache()
    
    def cleanup_cache(self):
        """Remove expired cache entries"""
        current_time = datetime.now()
        expired_urls = [
            url for url, entry in self.cache.items()
            if current_time > entry.expires_at
        ]
        
        for url in expired_urls:
            del self.cache[url]
    
    def get_cached_profiles(self) -> List[Profile]:
        """Get all cached profiles"""
        all_profiles = []
        for entry in self.cache.values():
            all_profiles.extend(entry.profiles)
        return all_profiles
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "total_cached_urls": len(self.cache),
            "total_cached_profiles": sum(len(entry.profiles) for entry in self.cache.values()),
            "cache_size_mb": sum(len(str(entry)) for entry in self.cache.values()) / (1024 * 1024)
        }
