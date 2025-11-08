# 🚀 Quick Start - Gemini Regional Agent

## Installation (2 minutes)

```bash
# 1. Install dependencies
cd multi-ai-agent
npm install

# 2. Set up your API key
cp .env.example .env

# 3. Edit .env and add your Gemini API key
nano .env
# Add: GEMINI_API_KEY=your_key_here

# 4. Run!
npm start
```

## Get Your Free Gemini API Key

1. Visit: https://makersuite.google.com/app/apikey
2. Click "Create API key"
3. Copy and paste into `.env`

## How to Use

**It's a chatbot - just chat naturally!**

```
You: What's the weather in London?
You: Will it rain in Addis Ababa tomorrow?
You: What crops should I plant in March?
You: Tell me about the latest farming techniques
You: Generate a PyQGIS script for satellite imagery
You: What is NDVI?
```

Gemini will automatically:
- Fetch weather data when you ask about weather
- Search the web for current information
- Get agricultural data when relevant
- Generate code when you ask
- Answer from knowledge for general questions

**That's it!** Type `exit` to quit, `help` for examples.

## What You Need

**Required:**
- Gemini API key (free from Google)
- Node.js 18+

**Optional (for web search):**
- Poe API key (otherwise uses mock data)

**Free & Works Out of the Box:**
- Weather data (via Open-Meteo)
- Agricultural data (mock data for testing)

## Example Session

```
╔═══════════════════════════════════════════════════════════╗
║              ✨  Gemini Regional Agent  🌍                ║
╚═══════════════════════════════════════════════════════════╝

You: What's the weather in Paris?

🤖 Gemini is thinking...
🌤️  Checking weather for Paris...
✨ Gemini is crafting your answer...

✨ Gemini:
The current weather in Paris is sunny with a temperature of 22°C. 
It feels like 23°C with moderate humidity at 65%. Light winds from 
the west at 3.5 m/s. Perfect weather for outdoor activities!

You: exit

👋 Goodbye!
```

## Troubleshooting

**"Missing required environment variables"**
- Make sure you created `.env` (not just `.env.example`)
- Add your Gemini API key

**"Module not found"**
```bash
npm install
```

That's all you need to know! 🎉
