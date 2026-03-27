"""
YouTube Channel RAG - Streamlit UI
Web interface for indexing and querying YouTube channels
"""

import streamlit as st
from main import index_channel, query_channel

# Page configuration
st.set_page_config(
    page_title="YouTube Channel RAG",
    page_icon="🎬",
    layout="wide"
)

# Title and description
st.title("🎬 YouTube Channel RAG")
st.caption("Ask anything across the entire channel")

# Initialize session state
if "indexed" not in st.session_state:
    st.session_state.indexed = False

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    max_videos = st.slider(
        "Max videos to index",
        min_value=5,
        max_value=500,
        value=100,
        step=5
    )

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Step 1: Index Channel")
    channel_url = st.text_input(
        "Channel URL",
        placeholder="https://www.youtube.com/@channelname/videos",
        help="Full YouTube channel URL"
    )

with col2:
    st.write("")  # Spacing
    st.write("")
    index_button = st.button(
        "🔄 Index Channel",
        use_container_width=True,
        key="index_button"
    )

# Handle indexing
if index_button:
    if not channel_url:
        st.error("Please enter a channel URL")
    else:
        with st.spinner("Indexing channel... this may take a few minutes"):
            success = index_channel(channel_url, max_videos)
            if success:
                st.session_state.indexed = True
                st.success("✅ Channel indexed! Start asking questions.")
            else:
                st.error("❌ Failed to index channel. Check the URL and try again.")

# Query section (only show if indexed)
if st.session_state.indexed:
    st.divider()
    st.subheader("Step 2: Ask Questions")
    
    question = st.text_input(
        "Your question",
        placeholder="e.g., What does this creator say about attention mechanisms?",
        help="Ask anything about the channel content"
    )
    
    col1, col2 = st.columns([2, 1])
    with col1:
        pass
    with col2:
        ask_button = st.button(
            "🔍 Ask",
            use_container_width=True,
            key="ask_button"
        )
    
    # Handle query
    if ask_button:
        if not question:
            st.error("Please enter a question")
        else:
            with st.spinner("Searching and generating answer..."):
                result = query_channel(question)
            
            st.divider()
            st.subheader("📝 Answer")
            st.write(result["answer"])
            
            if result["sources"]:
                st.subheader("📌 Sources")
                for url in result["sources"]:
                    st.markdown(f"- [{url}]({url})")
            else:
                st.info("No specific sources found for this query")
else:
    st.info("👈 Index a YouTube channel first using the form above")
