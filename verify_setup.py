"""
Test script to verify YouTube Channel RAG setup
Run this before starting the main app
"""

import sys
import os
from dotenv import load_dotenv

print("=" * 60)
print("YouTube Channel RAG - Setup Verification")
print("=" * 60)

# Test 1: Check environment variables
print("\n[1/5] Checking environment variables...")
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if api_key and api_key != "your_openai_api_key_here":
    print("   ✅ OPENAI_API_KEY is set")
else:
    print("   ❌ OPENAI_API_KEY not found or invalid")
    print("      → Copy .env.template to .env and add your OpenAI API key")
    sys.exit(1)

# Test 2: Check required libraries
print("\n[2/5] Checking required libraries...")
required_libs = [
    "streamlit",
    "openai",
    "chromadb",
    "youtube_transcript_api",
    "yt_dlp",
    "dotenv"
]

missing_libs = []
for lib in required_libs:
    try:
        __import__(lib)
        print(f"   ✅ {lib}")
    except ImportError:
        print(f"   ❌ {lib} - NOT INSTALLED")
        missing_libs.append(lib)

if missing_libs:
    print(f"\n   Install missing libraries with:")
    print(f"   pip install {' '.join(missing_libs)}")
    sys.exit(1)

# Test 3: Test OpenAI connection
print("\n[3/5] Testing OpenAI connection...")
try:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    
    # Make a simple test call
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input="test"
    )
    print("   ✅ OpenAI API is accessible")
except Exception as e:
    print(f"   ❌ OpenAI API error: {str(e)}")
    print("      → Check your API key and internet connection")
    sys.exit(1)

# Test 4: Test ChromaDB
print("\n[4/5] Testing ChromaDB...")
try:
    import chromadb
    client = chromadb.Client()
    col = client.get_or_create_collection(name="test")
    col.add(
        documents=["test"],
        embeddings=[[0.1] * 1536],
        ids=["test"]
    )
    print("   ✅ ChromaDB is working")
except Exception as e:
    print(f"   ❌ ChromaDB error: {str(e)}")
    sys.exit(1)

# Test 5: Test Streamlit import
print("\n[5/5] Testing Streamlit...")
try:
    import streamlit as st
    print(f"   ✅ Streamlit {st.__version__} is installed")
except Exception as e:
    print(f"   ❌ Streamlit error: {str(e)}")
    sys.exit(1)

# Success!
print("\n" + "=" * 60)
print("✅ All checks passed! Ready to run the app.")
print("=" * 60)
print("\nTo start the application, run:")
print("  streamlit run app.py")
print("\n" + "=" * 60)
