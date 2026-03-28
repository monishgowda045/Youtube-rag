"""
YouTube Channel RAG - Core Backend Functions
Fetches, processes, embeds, and queries YouTube channel transcripts
"""

import os
import sys
import json
import signal
import traceback
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


def timeout_handler(signum, frame):
    """Signal handler for timeout"""
    raise TimeoutError("Operation timed out")


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
    video_ids = []
    try:
        print(f"   Creating YoutubeDL instance with options: extract_flat={ydl_opts.get('extract_flat')}, playlistend={ydl_opts.get('playlistend')}")
        sys.stdout.flush()
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"   Extracting videos from: {channel_url}")
            sys.stdout.flush()
            
            # Try to extract info
            try:
                print(f"   Calling extract_info...")
                sys.stdout.flush()
                info = ydl.extract_info(channel_url, download=False)
                print(f"   extract_info completed, got response type: {type(info)}")
                sys.stdout.flush()
            except Exception as e:
                print(f"   ❌ extract_info failed: {str(e)}")
                traceback.print_exc()
                sys.stdout.flush()
                raise
            
            print(f"   Got info, processing entries...")
            sys.stdout.flush()
            
            if info and 'entries' in info:
                print(f"   Found entries dict, entries count: {len(info.get('entries', []))}")
                sys.stdout.flush()
                print(f"   Extracting video IDs...")
                sys.stdout.flush()
                entries = info.get('entries', [])
                for idx, entry in enumerate(entries):
                    if entry and 'id' in entry:
                        video_ids.append(entry['id'])
                        if (idx + 1) % 10 == 0:
                            print(f"   ... extracted {idx + 1}/{len(entries)} IDs")
                            sys.stdout.flush()
                print(f"   Got {len(video_ids)} entries before filtering")
                sys.stdout.flush()
                # Filter out channel IDs (those starting with UC and are 24 chars)
                video_ids = [vid for vid in video_ids if not (vid.startswith('UC') and len(vid) == 24)]
                print(f"   After filtering: {len(video_ids)} video IDs")
                sys.stdout.flush()
            else:
                print(f"   No entries found in response")
                sys.stdout.flush()
        print(f"   ✅ Found {len(video_ids)} videos")
        sys.stdout.flush()
    except Exception as e:
        print(f"   ❌ Error fetching videos: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
        print(f"   Possible solutions:")
        print(f"   1. Use format: https://www.youtube.com/@channelname/videos")
        print(f"   2. Or use: https://www.youtube.com/c/channelname/videos")
        print(f"   3. Check internet connection and YouTube URL validity")
        sys.stdout.flush()
        return []
    
    if not video_ids:
        print(f"   ❌ No actual video IDs found. Try a different URL format.")
    
    print(f"🎬 get_channel_video_ids returning {len(video_ids)} video IDs")
    sys.stdout.flush()
    return video_ids


def get_transcript(video_id: str) -> str:
    """
    Fetch transcript for a single YouTube video.
    """
    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.fetch(video_id)
        
        if transcript_list:
            transcript_text = " ".join([item.get("text", "") if isinstance(item, dict) else str(getattr(item, "text", "")) for item in transcript_list])
            return transcript_text if transcript_text.strip() else None
        return None
    except Exception as e:
        # Try auto-generated captions as fallback
        try:
            api = YouTubeTranscriptApi()
            transcript_list = api.fetch(video_id, languages=['en', 'en-US'])
            if transcript_list:
                transcript_text = " ".join([item.get("text", "") if isinstance(item, dict) else str(getattr(item, "text", "")) for item in transcript_list])
                return transcript_text if transcript_text.strip() else None
        except Exception as e2:
            pass
        
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


def index_channel(channel_url: str, max_videos: int = 10) -> bool:
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
    print(f"🎬 Calling get_channel_video_ids...")
    sys.stdout.flush()
    video_ids = get_channel_video_ids(channel_url, max_videos)
    print(f"✅ get_channel_video_ids returned, got {len(video_ids)} videos")
    sys.stdout.flush()
    if not video_ids:
        print("❌ No videos found")
        sys.stdout.flush()
        return False
    
    print(f"📺 Found {len(video_ids)} total videos, fetching transcripts...")
    sys.stdout.flush()
    
    indexed_count = 0
    no_transcript_count = 0
    
    try:
        for idx, video_id in enumerate(video_ids, 1):
            try:
                print(f"   ▶️ Video {idx}/{len(video_ids)}: {video_id}")
                sys.stdout.flush()
                
                # Get transcript
                transcript = get_transcript(video_id)
                if not transcript:
                    print(f"   ⏭️  Skipped")
                    sys.stdout.flush()
                    no_transcript_count += 1
                    continue
                
                print(f"   ✅ Got transcript ({len(transcript)} chars)")
                sys.stdout.flush()
                
                # Chunk text
                chunks = chunk_text(transcript)
                
                # Process each chunk
                for chunk_idx, chunk in enumerate(chunks):
                    try:
                        # Get embedding
                        embedding = get_embedding(chunk)
                        
                        # Store in memory
                        video_url = f"https://www.youtube.com/watch?v={video_id}"
                        doc_id = f"{video_id}_chunk_{chunk_idx}"
                        _vector_store["documents"].append(chunk)
                        _vector_store["embeddings"].append(embedding)
                        _vector_store["ids"].append(doc_id)
                        _vector_store["metadatas"].append({
                            "video_id": video_id,
                            "url": video_url,
                            "chunk_index": chunk_idx
                        })
                    except Exception as e:
                        print(f"   ❌ Chunk error: {str(e)}")
                        sys.stdout.flush()
                        continue
                
                indexed_count += 1
            except Exception as e:
                print(f"   ❌ Video error: {str(e)}")
                sys.stdout.flush()
                continue
    except Exception as e:
        print(f"   ❌ CRITICAL: {str(e)}")
        sys.stdout.flush()
    
    print(f"\n📊 Indexing Summary:")
    sys.stdout.flush()
    print(f"   ✅ Videos with transcripts indexed: {indexed_count}")
    sys.stdout.flush()
    print(f"   ⏭️  Videos without transcripts: {no_transcript_count}")
    sys.stdout.flush()
    print(f"   📝 Total chunks created: {len(_vector_store['documents'])}")
    sys.stdout.flush()
    
    if indexed_count == 0:
        print(f"\n❌ ERROR: No videos with transcripts found!")
        sys.stdout.flush()
        print(f"   YouTube videos need auto-generated or manual captions to work with this app.")
        sys.stdout.flush()
        print(f"   Try a different channel or enable captions for videos.")
        sys.stdout.flush()
        return False
    
    print(f"\n✅ Successfully indexed {indexed_count} videos!\n")
    sys.stdout.flush()
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
