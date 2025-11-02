import streamlit as st
import requests
import re
import json
from datetime import datetime
from typing import Optional, Dict, Any
import google.generativeai as genai

# Page Configuration
st.set_page_config(
    page_title="YouTube Summarizer Pro",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "YouTube Summarizer Pro v2.0"}
)

# Custom CSS for Professional Styling
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
    }
    
    [data-testid="stMainBlockContainer"] {
        padding-top: 0;
        background: #0a0a0a;
        min-height: 100vh;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #2d2d2d;
        color: #ffffff;
        border-radius: 8px;
        padding: 10px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #ff8c00 !important;
        color: white !important;
    }
    
    .main-container {
        background: #ffffff;
        border-radius: 0px;
        padding: 3rem 2.5rem;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        margin: 0;
        border-top: 8px solid #ff8c00;
    }
    
    .header-section {
        text-align: center;
        margin-bottom: 3rem;
        padding-bottom: 2rem;
        border-bottom: 2px solid #ff8c00;
    }
    
    .header-section h1 {
        color: #0a0a0a;
        font-size: 3.2rem;
        font-weight: 900;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    
    .header-section h1 span {
        color: #ff8c00;
    }
    
    .header-section p {
        color: #666;
        font-size: 1.15rem;
        font-weight: 500;
    }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1.5rem;
        margin: 3rem 0;
    }
    
    .feature-card {
        background: linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%);
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
        border: 2px solid transparent;
    }
    
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 40px rgba(255, 140, 0, 0.2);
        border-color: #ff8c00;
    }
    
    .feature-card h3 {
        color: #ff8c00;
        margin-bottom: 0.8rem;
        font-size: 1.3rem;
        font-weight: 700;
    }
    
    .feature-card p {
        color: #666;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    .input-section {
        background: linear-gradient(135deg, #f9f9f9 0%, #ffffff 100%);
        padding: 2.5rem;
        border-radius: 12px;
        margin: 2.5rem 0;
        border-left: 6px solid #ff8c00;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
    }
    
    .input-label {
        font-weight: 800;
        color: #0a0a0a;
        margin-bottom: 1rem;
        font-size: 1.2rem;
        letter-spacing: 0.5px;
    }
    
    .result-card {
        background: #f5f5f5;
        border-left: 6px solid #ff8c00;
        padding: 2rem;
        border-radius: 8px;
        margin: 1.5rem 0;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
    }
    
    .result-card h3 {
        color: #0a0a0a;
        margin-bottom: 1rem;
        font-size: 1.2rem;
    }
    
    .stat-box {
        background: linear-gradient(135deg, #ff8c00 0%, #ff7700 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(255, 140, 0, 0.3);
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 900;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-size: 0.95rem;
        opacity: 0.95;
        font-weight: 600;
    }
    
    .error-box {
        background: #ffe5e5;
        border-left: 6px solid #cc0000;
        color: #990000;
        padding: 1.2rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    .success-box {
        background: #e5ffe5;
        border-left: 6px solid #00aa00;
        color: #006600;
        padding: 1.2rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    .warning-box {
        background: #fff5e5;
        border-left: 6px solid #ff9900;
        color: #994400;
        padding: 1.2rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    .url-preview {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 0.8rem;
        border: 2px solid #ff8c00;
        word-break: break-all;
        color: #0a0a0a;
        font-size: 0.95rem;
        font-weight: 500;
    }
    
    .sidebar-section {
        background: rgba(255, 140, 0, 0.1);
        padding: 1.8rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        border-left: 4px solid #ff8c00;
    }
    
    .sidebar-section h3 {
        color: #ff8c00;
        margin-bottom: 1rem;
        font-size: 1.1rem;
        font-weight: 700;
    }
    
    .chatbot-container {
        background: #f9f9f9;
        border-radius: 12px;
        padding: 2rem;
        margin-top: 2rem;
        border: 2px solid #ff8c00;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
    }
    
    .chat-message {
        margin-bottom: 1.2rem;
        padding: 1.2rem;
        border-radius: 8px;
        word-wrap: break-word;
        line-height: 1.6;
    }
    
    .chat-user {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
        color: white;
        margin-left: 2rem;
        border-bottom-right-radius: 0;
        border-left: 4px solid #ff8c00;
    }
    
    .chat-bot {
        background: white;
        color: #0a0a0a;
        margin-right: 2rem;
        border-left: 4px solid #ff8c00;
        border-bottom-left-radius: 0;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
    }
    
    .stButton > button {
        background-color: #ff8c00 !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background-color: #ff7700 !important;
        box-shadow: 0 8px 20px rgba(255, 140, 0, 0.3) !important;
    }
    
    .stTextInput > div > div > input {
        border-radius: 8px !important;
        border: 2px solid #ddd !important;
        padding: 12px !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #ff8c00 !important;
    }
    
    .stSelectbox > div > div > div {
        border-radius: 8px !important;
    }
    
    .tab-content {
        padding: 2rem 0;
    }
    
    .download-section {
        display: flex;
        gap: 1rem;
        margin-top: 2rem;
        flex-wrap: wrap;
    }
</style>
""", unsafe_allow_html=True)

# Constants
WEBHOOK_URL = "https://sushiiel7890.app.n8n.cloud/webhook/ytube"
YOUTUBE_REGEX = re.compile(r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+")
SUPPORTED_FORMATS = ["Summary", "Timestamps", "Key Points", "Full Transcript"]

# Session State Initialization
if "history" not in st.session_state:
    st.session_state.history = []
if "last_response" not in st.session_state:
    st.session_state.last_response = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "gemini_initialized" not in st.session_state:
    st.session_state.gemini_initialized = False

def extract_video_id(url: str) -> Optional[str]:
    """Extract YouTube video ID from URL"""
    patterns = [
        r"(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)",
        r"youtube\.com\/embed\/([^&\n?#]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def validate_youtube_url(url: str) -> bool:
    """Validate YouTube URL"""
    return bool(YOUTUBE_REGEX.match(url.strip()))

def call_webhook(url: str, format_type: str) -> Dict[str, Any]:
    """Call n8n webhook with YouTube URL"""
    payload = {
        "youtubeUrl": url.strip(),
        "format": format_type,
        "timestamp": datetime.now().isoformat()
    }
    response = requests.post(WEBHOOK_URL, json=payload, timeout=90)
    response.raise_for_status()
    return response.json()

def initialize_gemini(api_key: str):
    """Initialize Gemini API"""
    try:
        genai.configure(api_key=api_key)
        st.session_state.gemini_initialized = True
        return True
    except Exception as e:
        st.error(f"Failed to initialize Gemini: {e}")
        return False

def chat_with_gemini(user_message: str, summary_context: str = "") -> str:
    """Send message to Gemini and get response"""
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        # Build context with summary if available
        context = ""
        if summary_context:
            context = f"Context from YouTube video summary:\n{summary_context}\n\n"
        
        full_message = f"{context}User question: {user_message}"
        
        response = model.generate_content(full_message)
        return response.text
    except Exception as e:
        return f"Error communicating with Gemini: {str(e)}"

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.header("⚙️ Settings")
    
    output_format = st.selectbox(
        "Output Format",
        SUPPORTED_FORMATS,
        help="Choose how you want the summary to be formatted"
    )
    
    include_timestamps = st.checkbox("Include Timestamps", value=True)
    include_keywords = st.checkbox("Extract Keywords", value=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Gemini API Configuration
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.subheader("🤖 Gemini Setup")
    
    api_key_input = st.text_input(
        "Gemini API Key",
        type="password",
        help="Get your API key from Google AI Studio (aistudio.google.com)"
    )
    
    if api_key_input:
        if st.button("✓ Initialize Gemini", key="init_gemini"):
            if initialize_gemini(api_key_input):
                st.success("✅ Gemini initialized successfully!")
                st.session_state.gemini_api_key = api_key_input
            else:
                st.error("❌ Failed to initialize Gemini")
    
    if st.session_state.gemini_initialized:
        st.success("✅ Gemini is Ready")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # History Section
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.subheader("📋 History")
    
    if st.session_state.history:
        if st.button("🗑️ Clear History", key="clear_history"):
            st.session_state.history = []
            st.rerun()
        
        for idx, item in enumerate(reversed(st.session_state.history[-5:])):
            with st.expander(f"📌 {item['video_id'][:8]}... - {item['time']}"):
                st.write(f"**URL:** {item['url']}")
                st.write(f"**Format:** {item['format']}")
                if item['response']:
                    st.json(item['response'][:200])
    else:
        st.info("No history yet")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Info Section
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.subheader("ℹ️ About")
    st.markdown("""
    **YouTube Summarizer Pro** is an AI-powered tool that generates concise summaries of YouTube videos with an intelligent chatbot.
    
    ✨ Multiple summary formats
    🏷️ Keyword extraction
    ⏱️ Timestamp support
    💾 History tracking
    🤖 Gemini AI Chatbot
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# Main Content
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Header
st.markdown("""
<div class="header-section">
    <h1>🎬 YouTube <span>Summarizer Pro</span></h1>
    <p>Transform Your Videos into Instant Summaries with AI Chat Support</p>
</div>
""", unsafe_allow_html=True)

# Features Overview
st.markdown("""
<div class="feature-grid">
    <div class="feature-card">
        <h3>⚡ Fast Processing</h3>
        <p>Get summaries in seconds</p>
    </div>
    <div class="feature-card">
        <h3>🎯 Accurate</h3>
        <p>AI-powered analysis</p>
    </div>
    <div class="feature-card">
        <h3>📊 Multiple Formats</h3>
        <p>Choose your preferred output</p>
    </div>
    <div class="feature-card">
        <h3>🤖 AI Chat</h3>
        <p>Ask questions with Gemini</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Tabs for organization
tab1, tab2, tab3 = st.tabs(["📝 Summarizer", "💬 Chatbot", "📊 Analysis"])

with tab1:
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown('<p class="input-label">📌 Paste Your YouTube Link</p>', unsafe_allow_html=True)

    youtube_url = st.text_input(
        "YouTube URL",
        placeholder="https://youtu.be/6bnDzZDiCkA or https://www.youtube.com/watch?v=...",
        label_visibility="collapsed"
    )
    if youtube_url:
        st.markdown(f'<div class="url-preview">✓ {youtube_url}</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 1])
    with col2:
        summarize_clicked = st.button("✨ Summarize", use_container_width=True, key="summarize_btn")

    st.markdown('</div>', unsafe_allow_html=True)

    # Processing Logic
    if summarize_clicked:
        if not youtube_url.strip():
            st.markdown('<div class="error-box">⚠️ Please enter a YouTube URL</div>', unsafe_allow_html=True)
        elif not validate_youtube_url(youtube_url.strip()):
            st.markdown('<div class="warning-box">⚠️ That doesn\'t look like a valid YouTube URL. Please check and try again.</div>', unsafe_allow_html=True)
        else:
            video_id = extract_video_id(youtube_url.strip())
            
            try:
                with st.spinner("🔄 Processing your video..."):
                    response_data = call_webhook(youtube_url.strip(), output_format)
                
                st.session_state.last_response = response_data
                st.session_state.history.append({
                    "url": youtube_url.strip(),
                    "video_id": video_id or "unknown",
                    "format": output_format,
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "response": str(response_data)[:200]
                })
                
                st.markdown('<div class="success-box">✅ Summary generated successfully!</div>', unsafe_allow_html=True)
                
                # Display Results
                st.markdown("---")
                st.subheader("📊 Results")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"""
                    <div class="stat-box">
                        <div class="stat-value">{video_id[:8]}</div>
                        <div class="stat-label">Video ID</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div class="stat-box">
                        <div class="stat-value">{output_format}</div>
                        <div class="stat-label">Format</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col3:
                    st.markdown(f"""
                    <div class="stat-box">
                        <div class="stat-value">✓</div>
                        <div class="stat-label">Complete</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Response Display
                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                st.markdown("### 📝 Summary Output")
                
                try:
                    st.json(response_data)
                except Exception:
                    st.write(response_data)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Export Options
                st.markdown('<div class="download-section">', unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.download_button(
                        label="📥 Download JSON",
                        data=json.dumps(response_data, indent=2),
                        file_name=f"summary_{video_id or 'unknown'}.json",
                        mime="application/json"
                    )
                with col2:
                    st.download_button(
                        label="📄 Download Text",
                        data=str(response_data),
                        file_name=f"summary_{video_id or 'unknown'}.txt",
                        mime="text/plain"
                    )
                with col3:
                    if st.button("🔄 Summarize Another", use_container_width=True):
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            
            except requests.exceptions.Timeout:
                st.markdown('<div class="error-box">⏱️ Request timed out. The video might be too long. Please try again.</div>', unsafe_allow_html=True)
            except requests.exceptions.RequestException as e:
                st.markdown(f'<div class="error-box">❌ Error: {str(e)}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f'<div class="error-box">❌ Unexpected error: {str(e)}</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="chatbot-container">', unsafe_allow_html=True)
    st.subheader("🤖 AI Chat Assistant")
    
    if not st.session_state.gemini_initialized:
        st.warning("⚠️ Please initialize Gemini API in Settings (Sidebar) first!")
    else:
        st.info("💡 Ask any questions about the video summary or get help with any topic!")
        
        # Display chat history
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f'<div class="chat-message chat-user"><b>You:</b> {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message chat-bot"><b>AI Assistant:</b> {message["content"]}</div>', unsafe_allow_html=True)
        
        # Chat input
        user_input = st.text_input(
            "Your question",
            placeholder="Ask anything about the summary or any topic...",
            label_visibility="collapsed",
            key="chat_input"
        )
        
        col1, col2, col3 = st.columns([4, 1, 1])
        with col2:
            send_clicked = st.button("Send", use_container_width=True, key="send_chat")
        
        if send_clicked and user_input.strip():
            # Add user message to history
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input
            })
            
            # Get context from last response if available
            summary_context = ""
            if st.session_state.last_response:
                summary_context = str(st.session_state.last_response)[:1000]
            
            # Get response from Gemini
            with st.spinner("🤖 AI is thinking..."):
                bot_response = chat_with_gemini(user_input, summary_context)
            
            # Add bot response to history
            st.session_state.chat_history.append({
                "role": "bot",
                "content": bot_response
            })
            
            st.rerun()
        
        # Clear chat history button
        if st.button("🗑️ Clear Chat", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.subheader("📊 Analysis & Statistics")
    
    if st.session_state.history:
        st.markdown("### Summary Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Summaries", len(st.session_state.history))
        with col2:
            st.metric("Chat Messages", len(st.session_state.chat_history))
        with col3:
            st.metric("Unique Videos", len(set(h["video_id"] for h in st.session_state.history)))
        with col4:
            st.metric("Formats Used", len(set(h["format"] for h in st.session_state.history)))
        
        st.markdown("### Recent Activity")
        for idx, item in enumerate(reversed(st.session_state.history), 1):
            st.write(f"{idx}. **{item['video_id'][:12]}...** - Format: {item['format']} - {item['time']}")
    else:
        st.info("No analysis data yet. Start summarizing videos!")

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p style="font-weight: 600;">YouTube Summarizer Pro | Powered by n8n, Gemini AI & Streamlit</p>
    <p style="font-size: 0.9rem; margin-top: 0.5rem;">© 2025 All rights reserved</p>
</div>
""", unsafe_allow_html=True)
