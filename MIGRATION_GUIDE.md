# Migration Guide: Puter AI to Gemini AI Backend

## Summary

Your backend has been successfully refactored to use **Google Gemini 2.0 Flash** instead of Puter AI for backend profile extraction. Puter AI is now only used in the frontend via their JavaScript SDK.

## Changes Made

### 1. Updated `scraping_service.py`
- **Removed**: Puter AI extractor import and usage
- **Added**: Google Gemini AI integration with proper configuration
- **Added**: Environment variable loading for API key management
- **Added**: Graceful fallback when API key is not configured

### 2. Created `env.example`
- Template file for environment variables
- Instructions for obtaining Gemini API key

### 3. Backend Architecture
- **Frontend**: Puter AI JavaScript SDK (browser-based)
- **Backend**: Google Gemini 2.0 Flash (server-based)

## Setup Instructions

### 1. Get Gemini API Key
1. Visit https://aistudio.google.com/app/apikey
2. Create a new API key (free tier available)
3. Copy the API key

### 2. Configure Environment
```bash
# Copy the example file
cp env.example .env

# Edit .env and add your actual API key
# Replace: GEMINI_API_KEY=your_gemini_api_key_here
# With:   GEMINI_API_KEY=your_actual_api_key_here
```

### 3. Run the Application
```bash
# Start both frontend and backend
python start.py
```

## How It Works

### Frontend (Puter AI)
- Used for browser-based AI interactions
- JavaScript SDK: `puter.ai.chat()`
- File: `index1.html`

### Backend (Gemini AI)
- Used for server-side profile extraction
- Google Generative AI API
- Files: `scraping_service.py`, `extractors/ai_extractor.py`

## Benefits

1. **Proper Architecture**: Frontend and backend use appropriate AI services
2. **No API Conflicts**: Separate services for different use cases
3. **Free Tier Available**: Gemini 2.0 Flash has generous free usage
4. **Better Performance**: Gemini is designed for backend API usage
5. **Graceful Degradation**: System works even without AI when API key not configured

## Troubleshooting

### Rate Limit Issues
If you see "Quota exceeded" errors:
1. Wait a few minutes and try again
2. Check your Gemini API quota in Google AI Studio
3. Consider upgrading to paid tier if needed

### API Key Issues
If AI extraction is disabled:
1. Check that `.env` file exists
2. Verify API key is correctly set (not the placeholder)
3. Ensure `GEMINI_API_KEY` environment variable is set

## Testing

Test the Gemini connection:
```bash
python test_gemini.py
```

Test the scraping service:
```bash
python test_scraping.py
```

## File Structure
```
├── extractors/
│   ├── ai_extractor.py          # Gemini AI backend extractor
│   ├── puter_ai_extractor.py    # (Legacy) Puter AI backend - NOT USED
│   ├── css_extractor.py         # CSS selector extractor
│   └── site_specific.py         # Site-specific extractor
├── index1.html                  # Frontend with Puter AI SDK
├── scraping_service.py          # Main scraping service (updated)
├── .env                         # Environment variables
├── env.example                  # Environment template
└── MIGRATION_GUIDE.md           # This file
```

Your backend is now properly configured to use Gemini AI for profile extraction while keeping Puter AI for frontend usage as intended.
