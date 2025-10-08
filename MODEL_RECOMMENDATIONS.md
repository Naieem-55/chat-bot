# Best Free Models for RAG Chatbot (2025)

## 🎯 Current Setup

Your chatbot is currently using:
- **LLM**: Llama 3.1 8B Instant (via Groq API)
- **Embedding**: sentence-transformers/all-MiniLM-L6-v2 (384 dimensions)
- **Free Tier**: 500,000 tokens/day

## 📊 LLM Model Comparison (Groq API)

### Available Free Models on Groq

| Model | Size | Speed | Quality | Best For | Config Value |
|-------|------|-------|---------|----------|--------------|
| **Llama 3.1 8B Instant** ⚡ | 8B | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Fast responses, quick RAG | `mistral` (current) |
| **Llama 3.3 70B Versatile** 🏆 | 70B | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Best quality, complex reasoning | `llama` |
| **Gemma 2 9B IT** 💡 | 9B | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Balanced speed/quality | `gemma` |

### Recommendations by Use Case

**🏆 Best Overall for RAG**: **Llama 3.3 70B**
- Matches Llama 3.1 405B performance
- Superior reasoning and context understanding
- Better at using retrieved context accurately
- Ideal for customer support where quality matters

**⚡ Best for Speed**: **Llama 3.1 8B Instant** (current)
- Fastest response times
- Good enough for simple FAQs
- Lower token consumption
- Best for high-volume use cases

**⚖️ Best Balance**: **Gemma 2 9B IT**
- Good speed + quality trade-off
- Efficient token usage
- Solid RAG performance

## 🔍 Embedding Model Comparison

### Top Free Embedding Models for RAG

| Model | Dimensions | Size | Speed | Accuracy | Best For |
|-------|------------|------|-------|----------|----------|
| **all-MiniLM-L6-v2** ⚡ | 384 | 22M | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Speed, small datasets (current) |
| **BAAI/bge-base-en-v1.5** 🏆 | 768 | 109M | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Best accuracy |
| **intfloat/e5-base-v2** 💡 | 768 | 110M | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Versatile, balanced |
| **all-mpnet-base-v2** | 768 | 120M | ⭐⭐⭐ | ⭐⭐⭐⭐ | High quality retrieval |
| **NV-Embed-v2** 🚀 | 4096 | Large | ⭐⭐ | ⭐⭐⭐⭐⭐ | State-of-the-art (NVIDIA) |
| **EmbeddingGemma** 📱 | 768 | 308M | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | On-device, multilingual |

### Embedding Model Recommendations

**🏆 Best for Accuracy**: **BAAI/bge-base-en-v1.5**
- 85%+ retrieval accuracy
- Industry-leading performance
- 768 dimensions for rich semantic capture

**⚡ Best for Speed**: **all-MiniLM-L6-v2** (current)
- Fastest embedding generation
- Smallest model size (22M)
- Good for real-time applications

**⚖️ Best Balance**: **intfloat/e5-base-v2**
- Excellent accuracy/speed trade-off
- State-of-the-art open source
- Competitive with commercial models

## 🎯 Recommended Configurations

### Configuration 1: Maximum Quality (Recommended for Customer Support)
```env
# .env configuration
LLM_PROVIDER=huggingface
HUGGINGFACE_MODEL=llama  # Uses Llama 3.3 70B
EMBEDDING_MODEL=BAAI/bge-base-en-v1.5
```
**Pros**: Best accuracy, superior reasoning, excellent context understanding
**Cons**: Slower responses, higher token usage

### Configuration 2: Balanced Performance (Current + Upgrade)
```env
# .env configuration
LLM_PROVIDER=huggingface
HUGGINGFACE_MODEL=gemma  # Uses Gemma 2 9B
EMBEDDING_MODEL=intfloat/e5-base-v2
```
**Pros**: Good speed + quality, efficient tokens, great embeddings
**Cons**: Medium on everything

### Configuration 3: Maximum Speed (Current Setup)
```env
# .env configuration
LLM_PROVIDER=huggingface
HUGGINGFACE_MODEL=mistral  # Uses Llama 3.1 8B
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```
**Pros**: Fastest responses, lowest token usage, real-time performance
**Cons**: Lower accuracy for complex questions

## 🔄 How to Switch Models

### Change LLM Model:
Edit `.env` file:
```bash
HUGGINGFACE_MODEL=llama  # or gemma, or mistral
```

Restart server:
```bash
start.bat
```

### Change Embedding Model:
1. Edit `.env`:
```bash
EMBEDDING_MODEL=BAAI/bge-base-en-v1.5
```

2. Re-ingest your data (embeddings need to be regenerated):
```bash
python scripts/ingest_data.py
```

3. Restart server:
```bash
start.bat
```

## 📈 Token Usage Considerations

### Groq Free Tier Limits
- **500,000 tokens/day** across all requests
- Shared across requests per minute (RPM) and tokens per minute (TPM)
- Returns 429 error when exceeded

### Token Efficiency Tips
1. **Use smaller models** (8B) for simple queries
2. **Limit conversation history** (currently 10 messages)
3. **Reduce max_tokens** if responses are too long
4. **Use retrieval filtering** to reduce context size

## 🎯 Final Recommendation

**For a customer support RAG chatbot, upgrade to:**

```env
HUGGINGFACE_MODEL=llama  # Llama 3.3 70B
EMBEDDING_MODEL=BAAI/bge-base-en-v1.5
```

**Why?**
- 70B model dramatically improves answer quality
- BGE embeddings improve retrieval accuracy by ~10-15%
- Still completely free via Groq
- Better handles complex customer questions
- More accurate use of retrieved context

**Trade-off**: Slightly slower responses (~1-2s longer), but much better quality.

## 🔬 Testing Different Models

Run this to test a model without changing production:
```python
python scripts/test_chatbot.py
```

Compare responses between models by temporarily changing `HUGGINGFACE_MODEL` in `.env`.
