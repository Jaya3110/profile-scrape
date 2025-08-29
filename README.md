# 🔍 User Profile Scraper

An AI-powered web scraping service that extracts user profile information from websites using multiple extraction strategies including CSS selectors, site-specific adapters, and Google's Gemini 2.0 Flash AI model.

## 🚀 Features

- **Multi-Strategy Extraction**: CSS selectors, AI-powered analysis, and site-specific adapters
- **AI Integration**: Uses Google Gemini 2.0 Flash for intelligent content analysis
- **Site-Specific Support**: Optimized extractors for LinkedIn, GitHub, Twitter, and company team pages
- **Smart Caching**: In-memory caching with configurable TTL
- **Rate Limiting**: Built-in protection against API abuse
- **RESTful API**: Clean FastAPI endpoints with automatic documentation
- **Real-time Validation**: URL validation and accessibility checking

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Scraping      │
│   (HTML/JS)     │◄──►│   (FastAPI)     │◄──►│   Service       │
│                 │    │                 │    │                 │
│ - URL Input     │    │ - API Routes    │    │ - CSS Extractors│
│ - Profile Cards │    │ - Validation    │    │ - AI Extractors │
│ - Loading UI    │    │ - Rate Limiting │    │ - Site Adapters │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Technology Stack

- **Backend**: Python 3.8+, FastAPI, Uvicorn
- **Scraping**: BeautifulSoup4, httpx, fake-useragent
- **AI**: Google Gemini 2.0 Flash API
- **Data Models**: Pydantic for validation
- **Caching**: In-memory with TTL
- **Rate Limiting**: Custom implementation

## 📋 Prerequisites

- Python 3.8 or higher
- Google AI Studio account (for Gemini API key)
- Modern web browser

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd web-scrape
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp env.example .env
# Edit .env and add your Gemini API key
```

Get your Gemini API key from [Google AI Studio](https://aistudio.google.com/)

### 3. Run the Backend

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### 4. Open Frontend

Open `index.html` in your browser or serve it with a local server:

```bash
python -m http.server 3000
# Then open http://localhost:3000
```

## 📚 API Endpoints

### Health Check
```http
GET /api/health
```

### URL Validation
```http
POST /api/validate-url
Content-Type: application/json

{
  "url": "https://example.com/profile"
}
```

### Profile Scraping
```http
POST /api/scrape
Content-Type: application/json

{
  "url": "https://example.com/profile",
  "max_profiles": 10,
  "timeout": 30
}
```

### Get Cached Profiles
```http
GET /api/profiles
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `PORT` | Server port | 8000 |
| `MAX_REQUESTS_PER_MINUTE` | Rate limit | 10 |
| `CACHE_TTL_HOURS` | Cache duration | 24 |

### Rate Limiting

- **Default**: 10 requests per minute per IP
- **Configurable**: Modify in `rate_limiter.py`
- **Headers**: Rate limit info included in responses

## 🎯 Extraction Strategies

### 1. CSS Selector Extraction
- Common profile patterns (`.profile-name`, `.job-title`, etc.)
- Social media link detection
- Image and bio extraction
- Confidence scoring based on data quality

### 2. AI-Powered Extraction
- Google Gemini 2.0 Flash analysis
- Intelligent content parsing
- Context-aware information extraction
- Fallback to manual parsing if JSON fails

### 3. Site-Specific Adapters
- **LinkedIn**: Profile pages with optimized selectors
- **GitHub**: User profiles and repositories
- **Twitter**: Profile information extraction
- **Company Pages**: Team member detection

## 📊 Data Models

### Profile Object
```json
{
  "id": "uuid",
  "name": "John Doe",
  "title": "Software Engineer",
  "email": "john@example.com",
  "phone": "+1-555-0123",
  "image": "https://example.com/avatar.jpg",
  "bio": "Passionate developer...",
  "company": "Tech Corp",
  "location": "San Francisco, CA",
  "social_links": {
    "linkedin": "https://linkedin.com/in/johndoe",
    "github": "https://github.com/johndoe",
    "twitter": "https://twitter.com/johndoe"
  },
  "extracted_from": "https://example.com/profile",
  "confidence": 0.92,
  "extraction_strategy": "ai_extraction"
}
```

## 🚀 Deployment

### Local Development
```bash
python main.py
```

### Production (Railway/Render)
1. Push code to GitHub
2. Connect to Railway/Render
3. Set environment variables
4. Deploy

### Frontend Deployment (Vercel)
1. Upload `index.html` and assets
2. Configure CORS in backend
3. Update API endpoints

## 🔒 Security Features

- **Input Validation**: URL format and accessibility checking
- **Rate Limiting**: Prevents API abuse
- **CORS Configuration**: Configurable origin restrictions
- **Error Handling**: Safe error responses
- **Resource Limits**: Timeout and size constraints

## 📈 Performance

- **Caching**: 24-hour TTL for scraped results
- **Async Processing**: Non-blocking I/O operations
- **Smart Retries**: AI extraction with fallback strategies
- **Memory Management**: Automatic cache cleanup

## 🧪 Testing

### Manual Testing
```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Test scraping
curl -X POST http://localhost:8000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/username"}'
```

### Test URLs
- LinkedIn: `https://linkedin.com/in/username`
- GitHub: `https://github.com/username`
- Company Team: `https://company.com/about/team`

## 🐛 Troubleshooting

### Common Issues

1. **Gemini API Error**: Check API key and quota
2. **Scraping Timeout**: Increase timeout in request
3. **Rate Limit**: Wait for reset or increase limits
4. **CORS Issues**: Check frontend domain configuration

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python main.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google AI Studio for Gemini API
- BeautifulSoup4 for HTML parsing
- FastAPI for the web framework
- Community contributors and testers

## 📞 Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: [Your Email]

---

**Note**: This tool is for educational and legitimate business purposes only. Always respect websites' robots.txt and terms of service.
