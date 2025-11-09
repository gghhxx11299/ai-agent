# MeshCore Integration Guide

This guide explains how to integrate the Multi-AI Agent with MeshCore (AI agents listing platform).

## Overview

The Multi-AI Agent is now fully compatible with MeshCore and can be listed on the platform for users to access.

## API Endpoints for MeshCore

### Standard Endpoint
- **URL**: `https://ai-agent-mak4.onrender.com/query`
- **Method**: POST
- **Content-Type**: application/json

### Request Format
```json
{
  "query": "Your question here"
}
```

Or MeshCore-compatible formats:
```json
{
  "message": "Your question here"
}
```

```json
{
  "input": "Your question here"
}
```

### Response Format
```json
{
  "success": true,
  "query": "Your question",
  "response": "AI response text",
  "answer": "AI response text",  // MeshCore compatibility
  "message": "AI response text",  // MeshCore compatibility
  "ai_model": "Gemini",
  "timestamp": "2025-01-01T12:00:00"
}
```

### MeshCore v1 API Endpoint
- **URL**: `https://ai-agent-mak4.onrender.com/v1/chat`
- **Method**: POST
- **Content-Type**: application/json

### OpenAI-Compatible Endpoint
- **URL**: `https://ai-agent-mak4.onrender.com/v1/completions`
- **Method**: POST
- **Content-Type**: application/json

**Request**:
```json
{
  "prompt": "Your question here"
}
```

**Response** (OpenAI format):
```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "Gemini",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "AI response"
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

## Environment Variables (Render)

Set these in your Render dashboard:

### Required (at least one)
- `GEMINI_API_KEY` - Gemini API key (recommended, free)
- `GROQ_API_KEY` - Groq API key (fast, free)
- `OPENROUTER_API_KEY` - OpenRouter API key (multiple models)

### Optional
- `POE_API_KEY` - Poe API key for enhanced web search
- `MESHCORE_API_KEY` - MeshCore API key (if needed)
- `MESHCORE_AGENT_ID` - MeshCore Agent ID (if needed)

## Features

✅ **Multi-AI Support**: Gemini (primary), Groq, OpenRouter (fallbacks)
✅ **Web Search**: Poe Web-Search bot, DuckDuckGo, Wikipedia (with fallbacks)
✅ **Weather Data**: Open-Meteo with comprehensive rainfall data
✅ **Agricultural Data**: Mock data (extendable)
✅ **Error Handling**: Robust error handling with graceful fallbacks
✅ **EOF Error Fixes**: All JSON parsing issues resolved
✅ **Production Ready**: Works on Render without .env file

## MeshCore Listing Configuration

When listing on MeshCore, use these settings:

### Agent Details
- **Name**: Multi-AI Agent
- **Description**: AI assistant with web search, weather data, and agricultural insights
- **API Endpoint**: `https://ai-agent-mak4.onrender.com/query`
- **API Type**: REST API
- **Authentication**: None (public API)

### Capabilities
- Web search (Poe, DuckDuckGo, Wikipedia)
- Weather data with rainfall information
- Agricultural insights
- Code generation (PyQGIS, Python)
- General knowledge Q&A

### Example Queries
- "What's the weather in London?"
- "Search for latest AI trends"
- "Tell me about farming in Ethiopia"
- "Generate a PyQGIS script for NDVI calculation"

## Testing

### Test with curl
```bash
curl -X POST https://ai-agent-mak4.onrender.com/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the weather in London?"}'
```

### Test MeshCore v1 endpoint
```bash
curl -X POST https://ai-agent-mak4.onrender.com/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'
```

### Test OpenAI-compatible endpoint
```bash
curl -X POST https://ai-agent-mak4.onrender.com/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is AI?"}'
```

## Deployment on Render

1. **Connect GitHub repository** to Render
2. **Set environment variables** in Render dashboard:
   - GEMINI_API_KEY (or GROQ_API_KEY or OPENROUTER_API_KEY)
   - POE_API_KEY (optional)
   - FLASK_ENV=production
3. **Deploy** - Render will automatically deploy
4. **Test** - Visit your Render URL to test
5. **List on MeshCore** - Add your agent to MeshCore with the Render URL

## Error Handling

The API now handles:
- ✅ EOF errors (End of File) in JSON parsing
- ✅ Incomplete JSON responses
- ✅ Missing API keys (graceful degradation)
- ✅ Network timeouts
- ✅ API failures (automatic fallback)

## Support

For issues or questions:
1. Check Render logs for errors
2. Verify environment variables are set
3. Test API endpoints directly
4. Check MeshCore integration documentation

