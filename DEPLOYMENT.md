# Deployment Guide for Multi-AI Agent System

## 🚀 Deploying to Render.com

This guide will help you deploy the Multi-AI Agent API to Render.com.

### Prerequisites

1. A GitHub account with this repository
2. A Render.com account (free tier available)
3. API keys for at least one AI service (Gemini, Groq, or OpenRouter)

---

## Deployment Steps

### 1. Prepare Your Repository

Make sure your repository has these files (already included):
- `api.py` - Flask web application
- `Procfile` - Tells Render how to run the app
- `render.yaml` - Render configuration
- `requirements.txt` - Python dependencies
- `start.sh` - Startup script

### 2. Deploy to Render

#### Option A: Using Render Dashboard (Recommended)

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com/
   - Sign up or log in

2. **Create New Web Service**
   - Click "New +" button
   - Select "Web Service"

3. **Connect Your Repository**
   - Choose "Connect GitHub" or "Connect GitLab"
   - Select your `ai-agent` repository
   - Click "Connect"

4. **Configure Service**
   ```
   Name: multi-ai-agent (or your preferred name)
   Region: Oregon (US West) or closest to you
   Branch: main
   Root Directory: leave empty
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn api:app --bind 0.0.0.0:$PORT --timeout 120 --workers 2
   ```

5. **Select Plan**
   - Choose "Free" plan (perfect for testing)

6. **Add Environment Variables**
   Click "Advanced" and add these environment variables:

   **Required (at least one):**
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   GROQ_API_KEY=your_groq_api_key_here
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   ```

   **Optional:**
   ```
   FLASK_ENV=production
   PYTHON_VERSION=3.10.13
   ```

7. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (2-5 minutes)
   - Your API will be live at: `https://your-app-name.onrender.com`

#### Option B: Using render.yaml (Infrastructure as Code)

1. The `render.yaml` file is already configured
2. Go to Render Dashboard
3. Click "New +" → "Blueprint"
4. Connect your repository
5. Render will automatically detect `render.yaml`
6. Add your environment variables in the dashboard
7. Click "Apply" to deploy

### 3. Verify Deployment

Once deployed, test your API:

**Health Check:**
```bash
curl https://your-app-name.onrender.com/health
```

**Query Endpoint:**
```bash
curl -X POST https://your-app-name.onrender.com/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the weather in London?"}'
```

**Visit in Browser:**
```
https://your-app-name.onrender.com/
```
You should see the API documentation.

---

## API Endpoints

### `GET /` - API Information
Returns service info and available endpoints

### `GET /health` - Health Check
Check if the service is running properly

### `GET /status` - System Status
Get detailed system status including AI models and features

### `GET /models` - List AI Models
See which AI models are available

### `POST /query` - Send Query
```json
{
  "query": "Your question here"
}
```

### `POST /chat` - Chat (Alias)
Same as `/query` endpoint

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | One of three | Google Gemini API key (recommended) |
| `GROQ_API_KEY` | One of three | Groq API key (free & fast) |
| `OPENROUTER_API_KEY` | One of three | OpenRouter API key |
| `PORT` | Auto-set | Render automatically sets this |
| `FLASK_ENV` | Optional | Set to `production` for prod |

**Get API Keys:**
- Gemini: https://makersuite.google.com/app/apikey (FREE)
- Groq: https://console.groq.com/keys (FREE)
- OpenRouter: https://openrouter.ai/keys (Paid)

---

## Troubleshooting

### "Application exited early"
**Problem:** The app is trying to run as a terminal chatbot
**Solution:** Make sure the Start Command is set to:
```bash
gunicorn api:app --bind 0.0.0.0:$PORT --timeout 120 --workers 2
```

### "No AI models available"
**Problem:** No API keys are configured
**Solution:** Add at least one API key (GEMINI_API_KEY, GROQ_API_KEY, or OPENROUTER_API_KEY) in Render environment variables

### "Module not found" errors
**Problem:** Dependencies not installed
**Solution:** Make sure Build Command is set to:
```bash
pip install -r requirements.txt
```

### Timeout errors
**Problem:** AI responses taking too long
**Solution:** The timeout is already set to 120 seconds in the start command. If needed, increase `--timeout` value.

### Free tier sleeping
**Problem:** Render free tier spins down after inactivity
**Solution:**
- First request after sleep takes 30-60 seconds (cold start)
- Consider upgrading to paid tier for always-on service
- Use a uptime monitor to ping your service every 10 minutes

---

## Performance Tips

### Free Tier Limitations
- App spins down after 15 minutes of inactivity
- 750 hours/month of runtime
- Cold starts take 30-60 seconds
- Perfect for testing and demos

### Optimization
1. **Use Groq for faster responses** (set `GROQ_API_KEY` as primary)
2. **Enable all AI fallbacks** for reliability
3. **Monitor logs** in Render dashboard
4. **Cache responses** if needed (future feature)

---

## Updating Your Deployment

When you push changes to GitHub:
1. Commit your changes: `git commit -m "your message"`
2. Push to GitHub: `git push origin main`
3. Render automatically rebuilds and deploys (auto-deploy enabled by default)

To disable auto-deploy:
- Go to Render Dashboard → Your Service → Settings
- Toggle "Auto-Deploy" off

---

## Local Development

To run locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY=your_key_here
export GROQ_API_KEY=your_key_here

# Run the API
python api.py
```

Visit: http://localhost:5000

---

## Production Checklist

- [ ] At least one AI API key configured
- [ ] Environment variables set in Render
- [ ] Build command: `pip install -r requirements.txt`
- [ ] Start command uses `gunicorn api:app`
- [ ] Health check responds at `/health`
- [ ] Test query endpoint works
- [ ] Auto-deploy enabled (optional)
- [ ] Custom domain configured (optional)

---

## Support

**Documentation:**
- API Docs: Visit your deployed URL
- Repository: https://github.com/gghhxx11299/ai-agent

**Common Issues:**
- Check Render logs in the dashboard
- Verify environment variables are set
- Test endpoints with curl or Postman
- Ensure you have at least one valid API key

---

## Cost

**Render Free Tier:**
- ✅ Perfect for this application
- ✅ 750 hours/month free
- ✅ Auto-sleep after 15 min inactivity
- ✅ Free SSL/TLS certificates
- ✅ Automatic deploys from GitHub

**Upgrade to Paid ($7/month):**
- Always-on service (no sleeping)
- More memory and CPU
- Better for production use
- Custom domains

---

## Next Steps

1. ✅ Deploy to Render
2. ✅ Test all endpoints
3. 🔧 Configure custom domain (optional)
4. 📱 Build a frontend (optional)
5. 📊 Add analytics (optional)
6. 🔐 Add authentication (optional)

**Congratulations! Your Multi-AI Agent is now live! 🎉**
