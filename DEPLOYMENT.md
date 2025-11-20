# Deployment Guide

## Deploy to Render (Free Tier)

This guide will help you deploy your RAG Chatbot to Render for free.

### Prerequisites
- GitHub account with this repository pushed
- Render account (sign up at https://render.com)
- API Keys:
  - Groq API Key (free from https://console.groq.com)
  - Or Anthropic API Key (from https://console.anthropic.com)

### Step 1: Prepare Your Repository

1. Make sure all changes are committed and pushed to GitHub:
   ```bash
   git add .
   git commit -m "Add deployment configuration"
   git push
   ```

### Step 2: Deploy on Render

#### Option A: One-Click Deploy (Using render.yaml)

1. Go to https://render.com
2. Click **"New"** → **"Blueprint"**
3. Connect your GitHub repository
4. Select this repository
5. Render will automatically detect `render.yaml`
6. Click **"Apply"**

#### Option B: Manual Deploy

**Deploy Backend:**
1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `chatbot-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: `Free`
5. Add Environment Variables:
   - `GROQ_API_KEY`: Your Groq API key
   - `ANTHROPIC_API_KEY`: (Optional) Your Anthropic key
6. Click **"Create Web Service"**

**Deploy Frontend:**
1. Click **"New +"** → **"Static Site"**
2. Connect the same repository
3. Configure:
   - **Name**: `chatbot-frontend`
   - **Build Command**: Leave empty
   - **Publish Directory**: `frontend`
4. Click **"Create Static Site"**

### Step 3: Update Frontend API URL

After backend deployment, you'll get a URL like:
```
https://chatbot-backend-xxxx.onrender.com
```

Update the frontend to use this URL:

1. Open `frontend/script.js`
2. Find the line with `API_BASE`
3. Update it to your backend URL:
   ```javascript
   const API_BASE = 'https://chatbot-backend-xxxx.onrender.com';
   ```
4. Commit and push:
   ```bash
   git add frontend/script.js
   git commit -m "Update API base URL for production"
   git push
   ```

Render will automatically redeploy your frontend.

### Step 4: Initialize Vector Store

After deployment, you need to upload documents:

1. Visit your frontend URL: `https://chatbot-frontend-xxxx.onrender.com`
2. Go to the Documents page
3. Upload your PDF documents
4. Wait for processing to complete

### Alternative: Deploy to Other Platforms

#### Railway
1. Visit https://railway.app
2. Click "Deploy from GitHub repo"
3. Select your repository
4. Railway will auto-detect and deploy

#### Vercel (Frontend) + Render (Backend)
- Deploy frontend to Vercel for better performance
- Keep backend on Render
- Update API URL in Vercel environment variables

### Free Tier Limits

**Render Free Tier:**
- 750 hours/month (enough for always-on)
- Services sleep after 15 minutes of inactivity
- First request after sleep takes ~30 seconds to wake up

**Tips:**
- Use a service like UptimeRobot to ping your app every 14 minutes to prevent sleeping
- Or accept the cold start delay (free tier limitation)

### Environment Variables

Required:
- `GROQ_API_KEY` - Free API from Groq (70k tokens/day)

Optional:
- `ANTHROPIC_API_KEY` - If using Claude models
- `HUGGINGFACE_API_KEY` - If using HuggingFace models

### Monitoring

- Check logs in Render Dashboard
- Monitor API usage in Groq Console
- Set up email alerts for errors

### Troubleshooting

**Backend won't start:**
- Check Render logs for errors
- Verify all dependencies in requirements.txt
- Ensure environment variables are set

**Frontend can't connect to backend:**
- Verify API_BASE URL in script.js
- Check CORS settings in backend
- Ensure backend is running (not sleeping)

**Vector store not persisting:**
- Render free tier has ephemeral storage
- Documents need to be re-uploaded after service restarts
- Consider upgrading to paid tier for persistent storage

### Support

For issues:
1. Check Render logs
2. Review GitHub Issues
3. Check API key validity

---

🎉 Your chatbot is now live and accessible worldwide!
