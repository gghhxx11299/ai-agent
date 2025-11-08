# ✨ Multi AI Regional Agent

An intelligent AI assistant powered by **multiple AI models** with real-time web search, weather data, and agricultural insights. Features automatic fallback between Gemini, Groq, and OpenRouter for maximum reliability!

## 🌟 Features

### 🤖 Multiple AI Models with Automatic Fallback
- **Gemini AI**: Google's powerful language model (Primary - FREE)
- **Groq**: Ultra-fast inference with Llama models (Fallback #1 - FREE)
- **OpenRouter**: Access to multiple models including Claude, GPT-4, and more (Fallback #2)
- **Smart Fallback**: Automatically switches models if one fails - maximum reliability!

### 📊 Real-Time Data Integration
- **Real-Time Web Search**: Current information via Poe API
- **Free Weather Data**: Real-time weather via Open-Meteo (no API key required!) ✨
- **Agricultural Insights**: Crop data, soil information, and farming recommendations
- **PyQGIS Code Generation**: Generate automated satellite imagery processing scripts 🛰️

### 💡 Intelligent Features
- **Smart Query Understanding**: AI analyzes your question and decides what data to fetch
- **Multi-Source Synthesis**: Combines data from multiple sources into coherent answers
- **Conversational Interface**: Just ask naturally - no need to remember commands
- **Automatic Keyword Extraction**: Intelligent keyword matching for precise web searches

## 🏗️ How It Works

**AI with Fallback System** 🔄

```
You: "What are the latest drought-resistant crops for Ethiopia?"
          ↓
    Primary AI (Gemini) Analyzes Query
    - Detects need for current information
    - Extracts keywords: "drought-resistant", "crops", "Ethiopia"
    - Identifies location: Ethiopia
          ↓
    ┌─────────────────────────────────┐
    │  Data Fetching (in parallel)    │
    ├─────────────────────────────────┤
    │ • Poe Web Search (keywords)     │
    │ • Weather Data (Open-Meteo)     │
    │ • Agricultural Data             │
    └─────────────────────────────────┘
          ↓
    AI Synthesizes Response
    - Combines all data sources
    - Provides conversational answer
          ↓
    If Primary AI Fails → Auto-switches to Groq
    If Groq Fails → Auto-switches to OpenRouter
          ↓
    Natural Language Response to You
```

## 📋 Prerequisites

- **Python 3.8+** (with pip)
- **At least ONE AI API Key** (you can use multiple for fallback):
  - Gemini API key (Recommended - **FREE**) - [Get it here](https://makersuite.google.com/app/apikey)
  - Groq API key (Fast & **FREE**) - [Get it here](https://console.groq.com/keys)
  - OpenRouter API key (Multiple models) - [Get it here](https://openrouter.ai/keys)
- **Optional:**
  - Poe API key (for web search)
  - Other regional data API keys as needed

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd multi-ai-agent
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add **at least one** AI API key:

```env
# Choose at least one (or use all three for maximum reliability!)

# Option 1: Gemini (Recommended)
GEMINI_API_KEY=your_gemini_api_key_here

# Option 2: Groq (Fast & Free)
GROQ_API_KEY=your_groq_api_key_here

# Option 3: OpenRouter (Multiple Models)
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

**💡 Pro Tip:** Configure multiple API keys for automatic fallback! If Gemini fails, it automatically switches to Groq, then OpenRouter.

### 3. Run the Agent

**Option A: Terminal Interface (Local)**
```bash
python main.py
```

Or with debug mode:
```bash
python main.py --debug
```

**Option B: Web API (Local or Production)**
```bash
python api.py
```
API will be available at `http://localhost:5000`

## 🌐 Deployment to Production

### Deploy to Render.com (Recommended)

This project includes a **Flask API** (`api.py`) ready for production deployment!

**Quick Deploy:**
1. Push your code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Create new Web Service
4. Connect your repository
5. Use these settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn api:app --bind 0.0.0.0:$PORT --timeout 120 --workers 2`
6. Add environment variables (at least one AI API key)
7. Deploy!

**📖 Full deployment guide:** See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

### API Endpoints

Once deployed, your API will have these endpoints:

- `GET /` - API information and documentation
- `GET /health` - Health check
- `GET /status` - System status
- `GET /models` - List available AI models
- `POST /query` - Send a query to the AI
- `POST /chat` - Chat with the AI (alias)

**Example API Usage:**
```bash
curl -X POST https://your-app.onrender.com/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the weather in London?"}'
```

## 💬 Usage

### Just Chat Naturally!

**This is a chatbot.** Talk to the AI like you would talk to a knowledgeable friend. No commands to remember - just ask your questions naturally!

#### Example Conversations:

**🌤️ Weather:**
```
You: What's the weather like in London right now?

✨ AI:
The current weather in London is partly cloudy with a temperature of 18°C...
```

**🌾 Agriculture:**
```
You: I want to plant crops in March in Ethiopia, what should I grow?

✨ AI:
March is a great time for planting in Ethiopia! Based on the climate and soil conditions...
• Teff - ideal for the belg season
• Maize - plant early March for best yields
• Chickpeas - drought-resistant option
...
```

**🔍 Current Information:**
```
You: What are the latest farming techniques being used in 2025?

✨ AI:
According to recent reports, several innovative techniques are gaining traction:
• Precision agriculture using drone technology
• AI-powered pest detection systems
...
```

**🛰️ Code Generation:**
```
You: Generate a PyQGIS script to process satellite imagery

✨ AI:
I've generated a PyQGIS script for automated satellite imagery processing!
Script saved to: generated_scripts/satellite_processing_1234567890.py
...
```

### System Commands

Only 3 commands to remember:
- `help` - Show conversation examples
- `clear` - Clear the screen
- `exit` - Exit the chat

## 📁 Project Structure

```
multi-ai-agent/
├── src/
│   ├── integrations/
│   │   ├── gemini.py          # Gemini AI integration
│   │   ├── groq.py            # Groq AI integration
│   │   ├── openrouter.py      # OpenRouter AI integration
│   │   ├── web_search.py      # DuckDuckGo web search
│   │   └── regional_data.py   # Weather, agriculture, satellite data
│   ├── utils/
│   │   └── code_generator.py  # PyQGIS script generation
│   └── orchestrator.py        # Main orchestration with AI fallback
├── config/
│   └── config.py              # Configuration management
├── main.py                    # Terminal interface (local use)
├── api.py                     # Flask REST API (production)
├── requirements.txt           # Python dependencies
├── Procfile                   # Render/Heroku deployment config
├── render.yaml                # Render infrastructure as code
├── start.sh                   # Production startup script
├── .env.example               # Environment variables template
├── DEPLOYMENT.md              # Deployment guide
└── README.md                  # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| **AI Models (need at least 1)** |
| `GEMINI_API_KEY` | Google Gemini API key | Recommended ✨ | - |
| `GROQ_API_KEY` | Groq API access key | Optional | - |
| `GROQ_MODEL` | Groq model to use | Optional | `llama-3.3-70b-versatile` |
| `OPENROUTER_API_KEY` | OpenRouter API key | Optional | - |
| `OPENROUTER_MODEL` | OpenRouter model | Optional | `anthropic/claude-3.5-sonnet` |
| **Data Sources** |
| `POE_API_KEY` | Poe API for web search | Optional | - |
| `POE_BOT_NAME` | Poe bot to use | Optional | `GPT-4` |
| `AGRICULTURE_API_KEY` | Agriculture data API key | Optional | - |
| `GEE_API_KEY` | Google Earth Engine API | Optional | - |

**Note:** Weather data uses Open-Meteo (no API key required) ✨

### Getting API Keys

#### 1. **Gemini API** (Recommended - FREE!)
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Free tier available with generous limits

#### 2. **Groq API** (Fast & FREE!)
   - Visit [Groq Console](https://console.groq.com/keys)
   - Sign up and get your API key
   - Ultra-fast inference with Llama models

#### 3. **OpenRouter API** (Multiple Models)
   - Visit [OpenRouter](https://openrouter.ai/keys)
   - Access to Claude, GPT-4, and many other models
   - Pay-per-use pricing

#### 4. **Poe API** (Optional - for web search)
   - Visit [Poe Developer Portal](https://poe.com/developers)
   - Create a bot and get API access

#### 5. **Weather Data** (No API key needed!)
   - Uses [Open-Meteo](https://open-meteo.com/) - completely free and open-source
   - No signup, no API key, no rate limits

## 🛰️ PyQGIS Script Generation

The agent can generate complete PyQGIS scripts for automated satellite imagery processing - perfect for agricultural monitoring and land use analysis.

### What It Does

The generated script automates:
1. **Loading** all satellite images (Landsat 8/9, Sentinel-2) from a folder
2. **NDVI Calculation** - Normalized Difference Vegetation Index for each image
3. **Clipping** images to regional boundaries using shapefile
4. **Exporting** results as GeoTIFF files

### How to Use

Just ask naturally:
```
> Generate a PyQGIS script for satellite processing
> I need a script to calculate NDVI from Landsat
> Create a satellite processing script for my region
```

The agent will generate a complete, ready-to-use Python script for QGIS!

## 🔌 AI Model Fallback System

The system includes an intelligent fallback mechanism:

1. **Primary Model**: Tries Gemini first (if configured)
2. **Fallback #1**: If Gemini fails, automatically switches to Groq
3. **Fallback #2**: If Groq fails, switches to OpenRouter
4. **Smart Persistence**: Once a working model is found, it becomes the new primary

### Example Fallback Flow:

```
User Query → Gemini [FAIL] → Groq [SUCCESS] → Response Delivered
                                    ↓
                            Groq now primary for subsequent queries
```

## 📊 Example Queries

**Data Queries:**
- "What is the weather forecast for Addis Ababa this week?"
- "What crops should I plant in Nairobi during March?"
- "Search for latest pest control methods for maize"
- "Tell me about climate change impact on East African agriculture"

**Code Generation:**
- "Generate a PyQGIS script for satellite processing"
- "Create a script to calculate NDVI from Sentinel-2"
- "I need a script to clip satellite images to my region"

**General Knowledge:**
- "What is NDVI and why is it important?"
- "Explain crop rotation benefits"
- "How does satellite imagery help farmers?"

## 🆘 Troubleshooting

### "No AI API keys configured"
- Make sure you've created a `.env` file
- Add at least one API key (Gemini, Groq, or OpenRouter)

### "API request failed"
- Verify your API keys are correct
- Check your internet connection
- The system will automatically try fallback models

### "Module not found"
- Run `pip install -r requirements.txt` to install dependencies
- Make sure you're using Python 3.8+

### Model keeps switching
- This is normal if your primary model is having issues
- The system automatically finds the most reliable model
- Configure multiple API keys for better reliability

## 🔮 Future Enhancements

- [ ] Add more AI model integrations (Claude, GPT-4, etc.)
- [ ] Database for caching responses
- [ ] Conversation history and context
- [ ] Visualization support (charts/graphs)
- [ ] Web interface option
- [ ] Multi-language support
- [ ] Voice input/output

## 🤝 Contributing

Contributions welcome! Feel free to:
- Add new AI model integrations
- Improve the fallback system
- Add visualization features
- Enhance data sources
- Improve documentation

## 📝 License

MIT

## 🙏 Acknowledgments

- Google Gemini for powerful AI capabilities
- Groq for ultra-fast inference
- OpenRouter for multi-model access
- Open-Meteo for free weather data
- Poe for web search capabilities

---

**Built with ❤️ for the agricultural and geospatial community**
