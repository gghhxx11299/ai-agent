# 🌩️ Thunder Client API Tests

## Base URL
**Render (Production)**: `https://ai-agent-mak4.onrender.com`
**Local Testing**: `http://localhost:5000`

---

## 📋 Test 1: API Information (GET)

**Endpoint**: `GET /`

**URL**:
```
https://ai-agent-mak4.onrender.com/
```

**Method**: `GET`

**Headers**: None required

**Expected Response**:
```json
{
  "status": "online",
  "service": "Multi-AI Agent System",
  "version": "1.0.0",
  "ai_models": {
    "primary": "Gemini (gemini-2.5-flash)",
    "fallback_1": "Groq (llama-3.3-70b-versatile)"
  },
  "endpoints": {...}
}
```

---

## 📋 Test 2: Health Check (GET)

**Endpoint**: `GET /health`

**URL**:
```
https://ai-agent-mak4.onrender.com/health
```

**Method**: `GET`

**Headers**: None required

**Expected Response**:
```json
{
  "status": "healthy",
  "ai_available": true,
  "current_ai": "Gemini",
  "models_loaded": 2
}
```

---

## 📋 Test 3: List AI Models (GET)

**Endpoint**: `GET /models`

**URL**:
```
https://ai-agent-mak4.onrender.com/models
```

**Method**: `GET`

**Headers**: None required

**Expected Response**:
```json
{
  "current_ai": "Gemini",
  "available_models": ["Gemini", "Groq"],
  "total_models": 2
}
```

---

## 📋 Test 4: System Status (GET)

**Endpoint**: `GET /status`

**URL**:
```
https://ai-agent-mak4.onrender.com/status
```

**Method**: `GET`

**Headers**: None required

**Expected Response**:
```json
{
  "system": "Multi-AI Agent System",
  "status": "operational",
  "ai": {
    "current": "Gemini",
    "available": ["Gemini", "Groq"],
    "count": 2
  },
  "features": {
    "web_search": true,
    "weather_data": true,
    "global_locations": true
  }
}
```

---

## 📋 Test 5: Simple AI Query (POST)

**Endpoint**: `POST /query`

**URL**:
```
https://ai-agent-mak4.onrender.com/query
```

**Method**: `POST`

**Headers**:
```
Content-Type: application/json
```

**Body** (JSON):
```json
{
  "query": "What is NDVI?"
}
```

**Expected Response**:
```json
{
  "success": true,
  "query": "What is NDVI?",
  "response": "NDVI stands for Normalized Difference Vegetation Index...",
  "ai_model": "Gemini"
}
```

---

## 📋 Test 6: Weather Query (POST)

**Endpoint**: `POST /query`

**URL**:
```
https://ai-agent-mak4.onrender.com/query
```

**Method**: `POST`

**Headers**:
```
Content-Type: application/json
```

**Body** (JSON):
```json
{
  "query": "What's the weather in London?"
}
```

**Expected Response**:
```json
{
  "success": true,
  "query": "What's the weather in London?",
  "response": "According to the latest weather data for London, it's currently 13.6°C and overcast...",
  "ai_model": "Gemini"
}
```

---

## 📋 Test 7: Web Search Query (POST)

**Endpoint**: `POST /query`

**URL**:
```
https://ai-agent-mak4.onrender.com/query
```

**Method**: `POST`

**Headers**:
```
Content-Type: application/json
```

**Body** (JSON):
```json
{
  "query": "What are the latest AI developments in 2025?"
}
```

**Expected Response**:
```json
{
  "success": true,
  "query": "What are the latest AI developments in 2025?",
  "response": "Based on the latest insights, 2025 is shaping up to be a dynamic year for AI...",
  "ai_model": "Gemini"
}
```

---

## 📋 Test 8: Chat Endpoint (POST)

**Endpoint**: `POST /chat` (alias for /query)

**URL**:
```
https://ai-agent-mak4.onrender.com/chat
```

**Method**: `POST`

**Headers**:
```
Content-Type: application/json
```

**Body** (JSON):
```json
{
  "query": "Tell me about crop rotation"
}
```

**Expected Response**: Same as /query endpoint

---

## 📋 Test 9: Error Handling - Missing Query (POST)

**Endpoint**: `POST /query`

**URL**:
```
https://ai-agent-mak4.onrender.com/query
```

**Method**: `POST`

**Headers**:
```
Content-Type: application/json
```

**Body** (JSON):
```json
{}
```

**Expected Response** (400 Bad Request):
```json
{
  "error": "Missing required field: query",
  "example": {
    "query": "What is the weather in London?"
  }
}
```

---

## 📋 Test 10: Error Handling - Invalid Endpoint (GET)

**Endpoint**: `GET /invalid`

**URL**:
```
https://ai-agent-mak4.onrender.com/invalid
```

**Method**: `GET`

**Expected Response** (404 Not Found):
```json
{
  "error": "Endpoint not found",
  "available_endpoints": {
    "GET /": "API information",
    "GET /health": "Health check",
    "POST /query": "Send a query",
    ...
  }
}
```

---

## 🚀 Quick Test Collection (Copy-Paste for Thunder Client)

### 1. Health Check
```
GET https://ai-agent-mak4.onrender.com/health
```

### 2. Ask About Weather
```
POST https://ai-agent-mak4.onrender.com/query
Content-Type: application/json

{
  "query": "What's the weather in Paris?"
}
```

### 3. Ask General Question
```
POST https://ai-agent-mak4.onrender.com/query
Content-Type: application/json

{
  "query": "What is machine learning?"
}
```

### 4. Get System Status
```
GET https://ai-agent-mak4.onrender.com/status
```

---

## ✅ Success Criteria

- **GET /** returns status "online"
- **GET /health** returns status "healthy"
- **POST /query** returns AI response
- Weather queries return real temperature data
- Response time < 10 seconds for simple queries
- Proper error messages for invalid requests

---

## 🔧 Troubleshooting

**If you get 404 errors:**
- Make sure the Render service is deployed and running
- Check that the URL is exactly `https://ai-agent-mak4.onrender.com`
- Verify the endpoint path (e.g., `/query` not `/query/`)

**If queries timeout:**
- First query may take longer (cold start on Render)
- Subsequent queries should be faster
- Render free tier may have slower response times

**If you get "unhealthy" status:**
- Check Render logs for API key configuration issues
- Verify environment variables are set correctly on Render

---

## 📱 Thunder Client Setup

1. Open Thunder Client in VS Code
2. Create "New Request"
3. Select method (GET or POST)
4. Enter URL: `https://ai-agent-mak4.onrender.com/[endpoint]`
5. For POST requests:
   - Go to "Body" tab
   - Select "JSON"
   - Paste the request body
6. Click "Send"

---

## 🎯 Example Thunder Client Screenshots

**Simple Query:**
```
Method: POST
URL: https://ai-agent-mak4.onrender.com/query
Body: {"query": "What is NDVI?"}
```

**Expected Result:**
- Status: 200 OK
- Response contains AI-generated answer
- Response time: ~3-8 seconds
