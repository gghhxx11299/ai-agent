# GitHub Pages Setup Guide

This guide will help you deploy the Multi-AI Agent frontend to GitHub Pages.

## Prerequisites

1. Your repository is already set up on GitHub
2. Your Render API is deployed and accessible at: `https://ai-agent-mak4.onrender.com`

## Steps to Enable GitHub Pages

### Option 1: Deploy from Main Branch (Recommended)

1. Go to your GitHub repository: `https://github.com/gghhxx11299/ai-agent`

2. Click on **Settings** (top right of the repository)

3. Scroll down to **Pages** in the left sidebar

4. Under **Source**, select:
   - **Branch**: `main`
   - **Folder**: `/ (root)`
   - Click **Save**

5. GitHub will build and deploy your site. Wait a few minutes.

6. Your site will be available at:
   `https://gghhxx11299.github.io/ai-agent/`

### Option 2: Deploy from docs/ Folder

If you prefer to use a `docs/` folder:

1. Create a `docs/` folder in your repository
2. Copy `index.html` to `docs/index.html`
3. In GitHub Settings > Pages, select:
   - **Branch**: `main`
   - **Folder**: `/docs`
   - Click **Save`

## Configuration

The `index.html` file is already configured to use your Render API:
- API URL: `https://ai-agent-mak4.onrender.com`
- The frontend automatically detects if it's running on GitHub Pages
- API connection status is displayed in the header

## Features

- ✅ Standalone HTML file (no build required)
- ✅ Auto-detects API URL based on hostname
- ✅ API connection status indicator
- ✅ Error handling for API connectivity
- ✅ Beautiful, responsive UI
- ✅ Real-time chat interface

## Troubleshooting

### API Not Connecting

If you see "API Unavailable":
1. Check that your Render deployment is running
2. Verify the API URL in `index.html` is correct
3. Check browser console for CORS errors
4. Ensure CORS is enabled in your Flask API (already configured)

### GitHub Pages Not Updating

1. Wait a few minutes after pushing changes
2. Clear browser cache
3. Check GitHub Actions for build errors (if using Actions)
4. Verify the file is in the root directory or docs folder

### CORS Errors

The Flask API already has CORS enabled. If you still see CORS errors:
1. Check that `flask-cors` is installed in requirements.txt
2. Verify `CORS(app)` is in your `api.py` file
3. Check Render logs for any CORS-related errors

## Custom Domain (Optional)

If you want to use a custom domain:
1. Go to GitHub Settings > Pages
2. Add your custom domain
3. Update DNS records as instructed by GitHub
4. Update the API URL in `index.html` if needed

## Testing Locally

To test the GitHub Pages version locally:
1. Open `index.html` in a web browser
2. Or use a local server:
   ```bash
   python3 -m http.server 8000
   ```
3. Visit `http://localhost:8000`

## Files Included

- `index.html` - Main frontend file (GitHub Pages compatible)
- `.nojekyll` - Prevents Jekyll processing
- `templates/index.html` - Original Flask template (for Render deployment)

## Support

If you encounter any issues:
1. Check the browser console for errors
2. Verify the Render API is running
3. Check GitHub Pages build logs
4. Ensure all files are committed and pushed to GitHub


