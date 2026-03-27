# Quick Start Guide

## 5-Minute Setup

### Step 1: Set up Python environment
```bash
# Navigate to project folder
cd c:\Users\monis\Desktop\DevOps\AWS\YOUTUBE-RAG

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure OpenAI API Key
```bash
# Create .env file from template
copy .env.template .env

# Edit .env and paste your OpenAI API key
# Get it at: https://platform.openai.com/api-keys
```

### Step 3: Run the App
```bash
streamlit run app.py
```

Your browser opens to `http://localhost:8501` 🚀

## First Test Run

1. **Find a YouTube Channel URL**
   - Example: `https://www.youtube.com/@AbhishekVeeramalla/videos`

2. **Paste in "Channel URL" field**

3. **Click "🔄 Index Channel"**
   - First indexing takes 2-5 minutes for 100 videos
   - Fetching transcripts: ~30 seconds
   - Generating embeddings: ~2-3 minutes
   - Shows progress for each video

4. **Once indexed, ask a question**
   - Example: "What does Andrej Karpathy talk about transformers?"
   - Wait for the AI to search and generate answer
   - See answer + source video links

## Architecture at a Glance

```
YouTube Channel URL
    ↓
[yt-dlp] → Get all video IDs
    ↓
[YouTube Transcript API] → Get auto-captions
    ↓
[chunk_text] → Split into 500-word chunks (with 50-word overlap)
    ↓
[OpenAI Embeddings] → Generate semantic vectors (1536-dim)
    ↓
[ChromaDB] → Store chunks + embeddings + video URLs
    ↓
User Question
    ↓
[OpenAI Embeddings] → Embed the question
    ↓
[ChromaDB] → Find top 5 most similar chunks
    ↓
[GPT-4-mini] → Generate grounded answer using chunks
    ↓
📝 Answer + 📌 Source Video Links
```

## Cost Breakdown (per channel indexing)

- **Embeddings**: ~$0.01 per 100 videos (very cheap)
- **GPT-4-mini per query**: ~$0.002 per question
- **Total for 100 videos + 10 questions**: < $0.05

## Common Issues

| Issue | Solution |
|-------|----------|
| "No module named 'streamlit'" | Run `pip install -r requirements.txt` again |
| "OPENAI_API_KEY not found" | Check `.env` file exists and has correct key |
| Indexing hangs | Check internet connection; some videos may take longer |
| "gpt-4-mini not found" | Ensure your OpenAI account has access to GPT-4-mini |

## Next Steps

- Index your favorite creator's channel
- Ask questions you've always wondered about
- Explore the answers with source links
- Experiment with different question types

## Questions?

Refer to `README.md` for detailed documentation.
