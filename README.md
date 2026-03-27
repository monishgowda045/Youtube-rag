<<<<<<< HEAD
# YouTube Channel RAG

Transform any YouTube channel into a searchable knowledge base. Ask questions across hundreds of videos without watching a single one.

## How It Works

1. **Fetch Transcripts**: Uses YouTube's free transcript API to extract auto-generated captions
2. **Chunk & Embed**: Splits transcripts into overlapping chunks and generates semantic embeddings (OpenAI)
3. **Vector Storage**: Stores embeddings in ChromaDB for fast similarity search
4. **Query & Answer**: Retrieves relevant chunks and uses GPT-4-mini to generate grounded answers

## Tech Stack

- **Transcripts**: youtube-transcript-api (free YouTube captions)
- **Embeddings**: OpenAI text-embedding-3-small (semantic understanding)
- **Vector DB**: ChromaDB (lightweight local storage)
- **LLM**: GPT-4-mini (cost-effective, sufficient for transcript Q&A)
- **UI**: Streamlit (rapid web development)

## Setup

### 1. Clone the repository
```bash
cd c:\Users\monis\Desktop\DevOps\AWS\YOUTUBE-RAG
```

### 2. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up OpenAI API key
```bash
# Copy the template
copy .env.template .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-...
```

Get your API key at: https://platform.openai.com/api-keys

### 5. Verify your setup (optional but recommended)
```bash
python verify_setup.py
```

This will check that all dependencies are installed, your API key is valid, and the app is ready to use.

### 6. Run the application
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## Windows Users

If you encounter GCC compiler errors or pip installation issues on Windows:

1. **Automatic fix** (recommended):
   ```bash
   python setup_windows.py
   ```

2. **Manual fix**: See [WINDOWS_SETUP.md](WINDOWS_SETUP.md) for detailed troubleshooting

For more Windows-specific issues, check [WINDOWS_FIX.md](WINDOWS_FIX.md)

## Usage

1. **Paste YouTube Channel URL** (e.g., `https://www.youtube.com/@AndrejKarpathy/videos`)
2. **Click "Index Channel"** - fetches and processes transcripts (takes ~1-5 minutes depending on channel size)
3. **Ask Questions** - e.g., "What does this creator say about attention mechanisms?"
4. **View Answers** with citations to source videos

## Example Queries

- "Summarize all videos about LangChain from this channel"
- "What does this creator say about RAG systems?"
- "Find every time the creator mentioned transformers"
- "What are the three main topics discussed across videos?"

## Project Structure

```
YOUTUBE-RAG/
├── app.py                    # Streamlit web UI
├── main.py                   # Core backend logic (transcripts, embeddings, queries)
├── requirements.txt          # Python package dependencies
├── requirements-lite.txt     # Lightweight dependency list
├── .env                      # Your OpenAI API key (DO NOT COMMIT)
├── .env.template             # Template for .env file
├── .gitignore                # Git ignore rules
├── verify_setup.py           # Setup verification script
├── setup_windows.py          # Windows-specific setup helper
├── README.md                 # This file
├── QUICKSTART.md             # 5-minute quick start guide
├── IMPLEMENTATION.md         # Detailed implementation notes
├── WINDOWS_SETUP.md          # Windows setup troubleshooting
├── WINDOWS_FIX.md            # Windows GCC compiler fixes
└── venv/                     # Virtual environment (created during setup)
```

### File Descriptions

- **app.py**: Streamlit UI handling channel indexing and question answering
- **main.py**: Core functions for fetching transcripts, chunking, embeddings, and vectorized search
- **verify_setup.py**: Run this to check if everything is correctly installed
- **setup_windows.py**: Automated script for Windows pip/dependency issues

## Important Notes

- **API Costs**: Uses OpenAI API for embeddings (~$0.02 per 1 million tokens). GPT-4-mini is very cost-effective (~$0.15 per 1M input tokens)
- **First Run**: Indexing takes time (1-2 min per 100 videos depending on internet speed)
- **Local Storage**: ChromaDB stores data locally in memory/cache - persists during session
- **Rate Limits**: YouTube allows free transcript access; be mindful of API rate limits if indexing very large channels

## Troubleshooting

### "Failed to index channel. Check the URL and try again"
- Verify the YouTube channel URL is correct (e.g., `https://www.youtube.com/@channelname/videos`)
- Ensure you have internet connection
- Some videos may not have transcripts available - the app will skip these automatically

### "No transcripts available for this video"
- Not all YouTube videos have captions enabled
- The app automatically skips videos without transcripts
- Try a different channel with more videos that have captions

### "OPENAI_API_KEY not found or invalid"
- Make sure `.env` file exists in the project root directory
- Verify your API key is copied correctly from https://platform.openai.com/api-keys
- Check that `.env` contains: `OPENAI_API_KEY=sk-proj-...`

### "You exceeded your current quota"
- Your OpenAI API account has reached its usage limit or has no active payment method
- Update your billing information at https://platform.openai.com/account/billing/overview
- If new account, you may need to add a valid payment method

### GCC/MinGW compiler errors (Windows)
- Run `python setup_windows.py` to automatically fix
- Or see [WINDOWS_SETUP.md](WINDOWS_SETUP.md) for manual fixes

### "Out of memory"
- ChromaDB stores embeddings in memory
- For channels with 1000+ videos, processing may slow down
- The app processes videos sequentially to minimize memory usage

## Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get up and running in 5 minutes
- **[IMPLEMENTATION.md](IMPLEMENTATION.md)** - Deep dive into how the app works
- **[WINDOWS_SETUP.md](WINDOWS_SETUP.md)** - Windows-specific setup and troubleshooting
- **[WINDOWS_FIX.md](WINDOWS_FIX.md)** - Solutions for Windows compiler/pip issues

## Future Enhancements

- Persistent storage across sessions (save indexed channels)
- Multi-channel support (search across multiple channels)
- Custom summarization per video
- Export Q&A results to PDF
- User authentication for shared instances
- Streaming responses for real-time answers

## License

MIT
=======
# Youtube-rag
>>>>>>> e625abc81d7e2a89ee36cf0061fbb93f320ab5aa
