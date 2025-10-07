# Free Model Setup Guide

Your chatbot has been updated to use **FREE Groq API** instead of Claude API!

## What Changed

- **Free API with high limits** - Groq offers 70,000+ tokens/day for FREE
- **Super fast** - Groq is one of the fastest LLM APIs available
- **Free models available**: Mixtral, Llama 3, Gemma
- **No cost** - Completely free to use!

## Quick Start (2 Minutes!)

### Step 1: Get Your FREE API Key

1. Go to: **https://console.groq.com/**
2. Click "Sign Up" (free, no credit card required)
3. After signing in, go to "API Keys" section
4. Click "Create API Key"
5. Copy your key (starts with `gsk_...`)

### Step 2: Add Key to .env File

Open `C:\projects\chatbot\.env` and set:
```env
HUGGINGFACE_API_KEY=gsk_your_actual_key_here
```

### Step 3: Start the Server

```bash
python run_server.py
```

That's it! 🎉

## Available Free Models

You can change the model in `.env` by setting `HUGGINGFACE_MODEL` to:

- **mistral** (default) - Mixtral-8x7B - Best quality
- **llama** - Llama 3 8B - Fast and good
- **gemma** - Gemma 7B - Google's model

## Troubleshooting

### "API authentication required" error
- You need a free Groq API key
- Follow Step 1 above to get one (takes 2 minutes)
- Make sure it's added to `.env` file

### "Rate limit reached" error
- Wait 1 minute and try again
- Free tier has generous limits (70k tokens/day)
- Upgrade to Groq paid tier for higher limits (still very cheap)

### Still getting errors?
- Check that `requests` library is installed: `pip install requests`
- Verify `.env` has `LLM_PROVIDER=huggingface`
- Check server logs for detailed error messages
- Make sure your API key starts with `gsk_`

## Test Your Setup

1. Start the server
2. Open http://localhost:8000/health in browser
3. Should see: `{"status":"healthy",...}`
4. Open frontend and ask a question!

## Compare: Before vs After

| Feature | Before (Claude) | After (Groq) |
|---------|----------------|--------------|
| Cost | $15-30/month | **FREE** |
| API Key | Required & Paid | Required but FREE |
| Signup | Credit card needed | Email only |
| Models | Claude 3.5 | Mixtral, Llama 3, Gemma |
| Response Time | Fast | **Super Fast** |
| Quality | Excellent | Very Good |
| Free Tier | None | 70k tokens/day |

## Why Groq?

✅ **Truly Free** - 70,000 tokens per day (enough for ~500 conversations)
✅ **Super Fast** - One of the fastest LLM inference services
✅ **No Credit Card** - Just email signup
✅ **Great Models** - Mixtral 8x7B, Llama 3, and more
✅ **Easy to Use** - OpenAI-compatible API

Enjoy your free, fast chatbot! 🎉
