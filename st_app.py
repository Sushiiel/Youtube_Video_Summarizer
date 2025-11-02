import streamlit as st
import requests
import re
import json
from datetime import datetime
from typing import Optional, Dict, Any
import google.generativeai as genai
import os

# Page Configuration
st.set_page_config(
    page_title="YouTube Summarizer Pro",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Orange and White Only
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
    }
    
    html, body, [data-testid="stAppViewContainer"] {
        background: white !important;
    }
    
    [data-testid="stMainBlockContainer"] {
        padding-top: 1rem;
        background: white;
        min-height: 100vh;
    }
    
    [data-testid="stSidebar"] {
        background: #ffffff;
    }
    
    [data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {
        border-left: 4px solid #ff8c00;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 2px solid #ff8c00;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f5f5f5;
        color: #333;
        border-radius: 8px 8px 0 0;
        padding: 12px 24px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #ff8c00 !important;
        color: white !important;
    }
    
    .main-header {
        background: linear-gradient(135deg, #ff8c00 0%, #ff9f1a 100%);
        color: white;
        padding: 2.5rem;
        border-radius: 0;
        margin: 0 0 2rem 0;
        box-shadow: 0 4px 15px rgba(255, 140, 0, 0.2);
        text-align: center;
    }
    
    .main-header h1 {
        font-size: 2.8rem;
        font-weight: 900;
        margin: 0;
        letter-spacing: -1px;
    }
    
    .main-header p {
        font-size: 1rem;
        opacity: 0.95;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    .content-wrapper {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 1rem;
    }
    
    .input-section {
        background: #f9f9f9;
        padding: 2rem;
        border-radius: 12px;
        margin: 2rem 0;
        border: 2px solid #ff8c00;
    }
    
    .input-label {
        font-weight: 800;
        color: #333;
        margin-bottom: 1rem;
        font-size: 1.1rem;
        letter-spacing: 0.5px;
    }
    
    .result-card {
        background: #f9f9f9;
        border-left: 6px solid #ff8c00;
        padding: 2rem;
        border-radius: 8px;
        margin: 1.5rem 0;
        box-shadow: 0 4px 12px rgba(255, 140, 0, 0.1);
    }
    
    .result-card h3 {
        color: #ff8c00;
        margin-bottom: 1rem;
        font-size: 1.2rem;
        font-weight: 700;
    }
    
    .stat-box {
        background: linear-gradient(135deg, #ff8c00 0%, #ff9f1a 100%);
        color: white;
        padding: 1.8rem;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(255, 140, 0, 0.2);
    }
    
    .stat-value {
        font-size: 1.8rem;
        font-weight: 900;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-size: 0.9rem;
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
        border-left: 6px solid #ff8c00;
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
        color: #333;
        font-size: 0.95rem;
        font-weight: 500;
    }
    
    .sidebar-section {
        background: #f9f9f9;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        border-left: 4px solid #ff8c00;
    }
    
    .sidebar-section h3 {
        color: #ff8c00;
        margin-bottom: 1rem;
        font-size: 1rem;
        font-weight: 700;
    }
    
    .chatbot-container {
        background: #f9f9f9;
        border-radius: 12px;
        padding: 2rem;
        margin-top: 1.5rem;
        border: 2px solid #ff8c00;
    }
    
    .chat-message {
        margin-bottom: 1rem;
        padding: 1rem;
        border-radius: 8px;
        word-wrap: break-word;
        line-height: 1.6;
    }
    
    .chat-user {
        background: #ff8c00;
        color: white;
        margin-left: 1rem;
        border-bottom-right-radius: 0;
        border-left: none;
    }
    
    .chat-bot {
        background: white;
        color: #333;
        margin-right: 1rem;
        border-left: 4px solid #ff8c00;
        border-bottom-left-radius: 0;
        box-shadow: 0 2px 8px rgba(255, 140, 0, 0.1);
    }
    
    .stButton > button {
        background-color: #ff8c00 !important;
        color: white !important;
        border: none !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background-color: #ff7700 !important;
        box-shadow: 0 6px 15px rgba(255, 140, 0, 0.3) !important;
    }
    
    .stTextInput > div > div > input {
        border-radius: 8px !important;
        border: 2px solid #ff8c00 !important;
        padding: 12px !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #999 !important;
    }
    
    .stSelectbox > div > div > div {
        border-radius: 8px !important;
        border: 2px solid #ff8c00 !important;
    }
    
    .stCheckbox > label {
        font-weight: 600;
    }
    
    .footer {
        text-align: center;
        color: #666;
        padding: 2rem 1rem;
        margin-top: 3rem;
        border-top: 2px solid #ff8c00;
    }
    
    .footer p {
        margin: 0.3rem 0;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Constants
WEBHOOK_URL = "https://sushiiel7890.app.n8n.cloud/webhook/ytube"
YOUTUBE_REGEX = re.compile(r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+")
SUPPORTED_FORMATS = ["Summary", "Timestamps", "Key Points", "Full Transcript"]
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

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

def initialize_gemini():
    """Initialize Gemini API"""
    if not GEMINI_API_KEY:
        return False
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        st.session_state.gemini_initialized = True
        return True
    except Exception as e:
        st.error(f"Failed to initialize Gemini: {e}")
        return False

def chat_with_gemini(user_message: str, summary_context: str = "") -> str:
    """Send message to Gemini and get response"""
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        context = ""
        if summary_context:
            context = f"Context from YouTube video summary:\n{summary_context}\n\n"
        
        full_message = f"{context}User question: {user_message}"
        response = model.generate_content(full_message)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# Initialize Gemini on app start
if GEMINI_API_KEY and not st.session_state.gemini_initialized:
    initialize_gemini()

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
    
    # Gemini Status
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.subheader("🤖 Gemini Status")
    
    if st.session_state.gemini_initialized:
        st.success("✅ Gemini API Connected")
    else:
        st.error("❌ Gemini API Not Available")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # History Section
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.subheader("📋 History")
    
    if st.session_state.history:
        if st.button("🗑️ Clear History", key="clear_history", use_container_width=True):
            st.session_state.history = []
            st.rerun()
        
        st.markdown("**Recent Summaries:**")
        for item in reversed(st.session_state.history[-5:]):
            with st.expander(f"📌 {item['video_id'][:8]}... - {item['time']}"):
                st.write(f"**Format:** {item['format']}")
    else:
        st.info("No history yet")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Main Header
st.markdown("""
<div class="main-header">
    <h1>YouTube Summarizer Pro</h1>
    <p>Transform Videos into Instant Summaries with AI Chat</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="content-wrapper">', unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["📝 Summarizer", "💬 Chatbot", "📊 Analysis"])

with tab1:
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown('<p class="input-label">Paste Your YouTube Link</p>', unsafe_allow_html=True)

    youtube_url = st.text_input(
        "YouTube URL",
        placeholder="https://youtu.be/6bnDzZDiCkA",
        label_visibility="collapsed"
    )
    
    if youtube_url:
        st.markdown(f'<div class="url-preview">✓ {youtube_url}</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        summarize_clicked = st.button("✨ Summarize", use_container_width=True, key="summarize_btn")

    st.markdown('</div>', unsafe_allow_html=True)

    # Processing Logic
    if summarize_clicked:
        if not youtube_url.strip():
            st.markdown('<div class="error-box">⚠️ Please enter a YouTube URL</div>', unsafe_allow_html=True)
        elif not validate_youtube_url(youtube_url.strip()):
            st.markdown('<div class="warning-box">⚠️ Invalid YouTube URL. Please check and try again.</div>', unsafe_allow_html=True)
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
                
                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                st.markdown("### Summary Output")
                
                try:
                    st.json(response_data)
                except Exception:
                    st.write(response_data)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.download_button(
                        label="📥 Download JSON",
                        data=json.dumps(response_data, indent=2),
                        file_name=f"summary_{video_id or 'unknown'}.json",
                        mime="application/json",
                        use_container_width=True
                    )
                with col2:
                    st.download_button(
                        label="📄 Download Text",
                        data=str(response_data),
                        file_name=f"summary_{video_id or 'unknown'}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                with col3:
                    if st.button("🔄 Summarize Another", use_container_width=True):
                        st.rerun()
            
            except requests.exceptions.Timeout:
                st.markdown('<div class="error-box">⏱️ Request timed out. Try again.</div>', unsafe_allow_html=True)
            except requests.exceptions.RequestException as e:
                st.markdown(f'<div class="error-box">❌ Error: {str(e)}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f'<div class="error-box">❌ Unexpected error: {str(e)}</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="chatbot-container">', unsafe_allow_html=True)
    st.subheader("🤖 AI Chat Assistant")
    
    if not st.session_state.gemini_initialized:
        st.warning("⚠️ Gemini API is not configured. Please contact administrator.")
    else:
        st.info("💡 Ask questions about the video summary or any topic!")
        
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f'<div class="chat-message chat-user"><b>You:</b> {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message chat-bot"><b>AI:</b> {message["content"]}</div>', unsafe_allow_html=True)
        
        user_input = st.text_input(
            "Your question",
            placeholder="Ask anything...",
            label_visibility="collapsed",
            key="chat_input"
        )
        
        col1, col2 = st.columns([4, 1])
        with col2:
            send_clicked = st.button("Send", use_container_width=True, key="send_chat")
        
        if send_clicked and user_input.strip():
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input
            })
            
            summary_context = ""
            if st.session_state.last_response:
                summary_context = str(st.session_state.last_response)[:1000]
            
            with st.spinner("🤖 AI is thinking..."):
                bot_response = chat_with_gemini(user_input, summary_context)
            
            st.session_state.chat_history.append({
                "role": "bot",
                "content": bot_response
            })
            
            st.rerun()
        
        if st.button("🗑️ Clear Chat", use_container_width=True, key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.subheader("📊 Analysis & Statistics")
    
    if st.session_state.history:
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
            st.write(f"{idx}. **{item['video_id'][:12]}...** - {item['format']} - {item['time']}")
    else:
        st.info("No data yet. Start summarizing!")

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    <p>🎬 YouTube Summarizer Pro | Powered by n8n, Gemini AI & Streamlit</p>
    <p>© 2025 All rights reserved</p>
</div>
""", unsafe_allow_html=True)
