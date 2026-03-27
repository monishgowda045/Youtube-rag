"""
YouTube Channel RAG - Core Backend Functions
Fetches, processes, embeds, and queries YouTube channel transcripts
"""

import os
import json
from typing import List, Dict
from dotenv import load_dotenv
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# In-memory vector store (no ChromaDB dependency)
_vector_store = {
    "documents": [],
    "embeddings": [],
    "ids": [],
    "metadatas": []
}


def get_channel_video_ids(channel_url: str, max_videos: int = 100) -> List[str]:
    """
    Fetch all video IDs from a YouTube channel.
    
    Args:
        channel_url: Full YouTube channel URL
        max_videos: Maximum number of videos to fetch (default 100)
    
    Returns:
        List of video IDs
    """
    print(f"🎬 Fetching video IDs from channel...")
    print(f"   Original URL: {channel_url}")
    
    # Normalize URL to ensure we get the /videos tab
    channel_url = channel_url.rstrip('/')
    
    # Convert various URL formats to the /videos tab format
    if '@' in channel_url and not channel_url.endswith('/videos'):
        # Handle @channelname format
        if channel_url.endswith('/videos'):
            pass  # Already has /videos
        else:
            channel_url = channel_url + '/videos'
    elif '/c/' in channel_url and not channel_url.endswith('/videos'):
        # Handle /c/channelid format
        channel_url = channel_url + '/videos'
    
    print(f"   Normalized URL: {channel_url}")
    
    ydl_opts = {
        'extract_flat': True,
        'quiet': False,
        'no_warnings': False,
        'playlistend': max_videos,
    }
    video_ids = []{}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"   Extracting videos from: {channel_url}")
            info = ydl.extract_info(channel_url, download=False)
            if info and 'entries' in info:
                video_ids = [entry['id'] for entry in info.get('entries', []) if entry and 'id' in entry]
                # Filter out channel IDs (those starting with UC and are 24 chars)
                video_ids = [vid for vid in video_ids if not (vid.startswith('UC') and len(vid) == 24)]
            else:
                print(f"   No entries found in response")
        print(f"   ✅ Found {len(video_ids)} videos")
    except Exception as e:
        print(f"   ❌ Error fetching videos: {str(e)}")
        print(f"   Possible solutions:")
        print(f"   1. Use format: https://www.youtube.com/@channelname/videos")
        print(f"   2. Or use: https://www.youtube.com/c/channelname/videos")
        print(f"   3. Check internet connection and YouTube URL validity")
        return []
    
    if not video_ids:
        print(f"   ❌ No actual video IDs found. Try a different URL format.")
    
    return video_ids


def get_transcript(video_id: str) -> str:
    """
    Fetch transcript for a single YouTube video.
    
    Args:
        video_id: YouTube video ID
    
    Returns:
        Transcript text, or None if unavailable
    """
    try:
        # Create API instance and fetch transcript
        api = YouTubeTranscriptApi()
        transcript_list = api.fetch(video_id)
        if transcript_list:
            # Concatenate all transcript items - handle both dict and object formats
            transcript_text = []
            for item in transcript_list:
                if isinstance(item, dict):
                    transcript_text.append(item.get("text", ""))
                else:
                    # Handle FetchedTranscriptSnippet objects
                    transcript_text.append(str(getattr(item, "text", "")))
            transcript = " ".join(transcript_text)
            return transcript if transcript else None
        return None
    except Exception as e:
        # Video may not have captions - skip silently
        return None


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks to preserve context.
    
    Args:
        text: Input text to chunk
        chunk_size: Words per chunk (default 500)
        overlap: Overlapping words between chunks (default 50)
    
    Returns:
        List of text chunks
    """
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i : i + chunk_size])
        chunks.append(chunk)
    
    return chunks


def get_embedding(text: str) -> List[float]:
    """
    Generate embedding for text using OpenAI.
    
    Args:
        text: Text to embed
    
    Returns:
        Embedding vector (1536 dimensions)
    """
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


def index_channel(channel_url: str, max_videos: int = 100) -> bool:
    """
    Main workflow: fetch, transcode, embed, and store all channel videos.
    
    Args:
        channel_url: YouTube channel URL
        max_videos: Maximum videos to process
    
    Returns:
        True if successful, False otherwise
    """
    global _vector_store
    _vector_store = {
        "documents": [],
        "embeddings": [],
        "ids": [],
        "metadatas": []
    }
    
    print(f"\n🔄 Starting channel indexing...")
    
    # Get video IDs
    video_ids = get_channel_video_ids(channel_url, max_videos)
    if not video_ids:
        print("❌ No videos found")
        return False
    
    print(f"📺 Found {len(video_ids)} total videos, fetching transcripts...")
    
    indexed_count = 0
    no_transcript_count = 0
    
    for idx, video_id in enumerate(video_ids, 1):
        # Get transcript
        transcript = get_transcript(video_id)
        if not transcript:
            no_transcript_count += 1
            print(f"   ⏭️  Video {idx}/{len(video_ids)}: No transcript available (skipping)")
            continue
        
        print(f"   ✅ Video {idx}/{len(video_ids)}: Got transcript ({len(transcript)} chars)")
        
        # Chunk text
        chunks = chunk_text(transcript)
        
        # Process each chunk
        for chunk_idx, chunk in enumerate(chunks):
            try:
                # Get embedding
                embedding = get_embedding(chunk)
                
                # Prepare metadata
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                doc_id = f"{video_id}_chunk_{chunk_idx}"
                
                # Store in memory
                _vector_store["documents"].append(chunk)
                _vector_store["embeddings"].append(embedding)
                _vector_store["ids"].append(doc_id)
                _vector_store["metadatas"].append({
                    "video_id": video_id,
                    "url": video_url,
                    "chunk_index": chunk_idx
                })
            except Exception as e:
                print(f"   Error processing chunk: {str(e)}")
                continue
        
        indexed_count += 1
    
    print(f"\n📊 Indexing Summary:")
    print(f"   ✅ Videos with transcripts indexed: {indexed_count}")
    print(f"   ⏭️  Videos without transcripts: {no_transcript_count}")
    print(f"   📝 Total chunks created: {len(_vector_store['documents'])}")
    
    if indexed_count == 0:
        print(f"\n❌ ERROR: No videos with transcripts found!")
        print(f"   YouTube videos need auto-generated or manual captions to work with this app.")
        print(f"   Try a different channel or enable captions for videos.")
        return False
    
    print(f"\n✅ Successfully indexed {indexed_count} videos!\n")
    return True


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    import math
    dot_product = sum(x * y for x, y in zip(a, b))
    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(x * x for x in b))
    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0
    return dot_product / (magnitude_a * magnitude_b)


def query_channel(question: str) -> Dict[str, any]:
    """
    Query the indexed channel and get grounded answer.
    
    Args:
        question: User question
    
    Returns:
        Dict with "answer" and "sources" (list of video URLs)
    """
    global _vector_store
    
    if not _vector_store["embeddings"]:
        return {
            "answer": "❌ No indexed videos found. Please index a channel first.",
            "sources": []
        }
    
    # Embed question
    q_embedding = get_embedding(question)
    
    # Find top 5 most similar chunks using cosine similarity
    similarities = []
    for i, embedding in enumerate(_vector_store["embeddings"]):
        sim = cosine_similarity(q_embedding, embedding)
        similarities.append((sim, i))
    
    # Sort by similarity (descending) and get top 5
    similarities.sort(reverse=True)
    top_indices = [idx for sim, idx in similarities[:5]]
    
    # Extract context and sources
    context_parts = []
    sources = set()
    
    for idx in top_indices:
        context_parts.append(_vector_store["documents"][idx])
        metadata = _vector_store["metadatas"][idx]
        if "url" in metadata:
            sources.add(metadata["url"])
    
    context = "\n\n".join(context_parts)
    
    # Generate answer using GPT-4-mini
    prompt = f"""Answer the question using ONLY the YouTube transcript context below.
Include which video(s) the information came from.

Question: {question}

Context:
{context}

Answer:"""
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        answer = response.choices[0].message.content
    except Exception as e:
        answer = f"Error generating answer: {str(e)}"
    
    return {
        "answer": answer,
        "sources": list(sources)
    }
