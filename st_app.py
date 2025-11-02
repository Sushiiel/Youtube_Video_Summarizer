import streamlit as st
import requests
import re
import json
from datetime import datetime
from typing import Optional, Dict, Any

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
        padding-top: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .main-container {
        background: white;
        border-radius: 15px;
        padding: 2.5rem;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
        margin-bottom: 2rem;
    }
    
    .header-section {
        text-align: center;
        margin-bottom: 2rem;
        padding-bottom: 2rem;
        border-bottom: 3px solid #667eea;
    }
    
    .header-section h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .header-section p {
        color: #666;
        font-size: 1.1rem;
        font-weight: 500;
    }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .feature-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
    }
    
    .feature-card h3 {
        color: #667eea;
        margin-bottom: 0.5rem;
        font-size: 1rem;
    }
    
    .feature-card p {
        color: #666;
        font-size: 0.9rem;
    }
    
    .input-section {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 12px;
        margin: 2rem 0;
        border-left: 5px solid #667eea;
    }
    
    .input-label {
        font-weight: 700;
        color: #333;
        margin-bottom: 0.8rem;
        font-size: 1.1rem;
    }
    
    .button-container {
        display: flex;
        gap: 1rem;
        justify-content: center;
        margin-top: 1.5rem;
        flex-wrap: wrap;
    }
    
    .result-card {
        background: #f0f4ff;
        border-left: 4px solid #667eea;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .stats-section {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stat-value {
        font-size: 1.8rem;
        font-weight: bold;
        margin-bottom: 0.3rem;
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    .error-box {
        background: #ffe5e5;
        border-left: 4px solid #ff4444;
        color: #cc0000;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .success-box {
        background: #e5ffe5;
        border-left: 4px solid #44ff44;
        color: #009900;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: #fff5e5;
        border-left: 4px solid #ffaa00;
        color: #996600;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .loading-spinner {
        text-align: center;
        color: #667eea;
        font-weight: 600;
    }
    
    .url-preview {
        background: white;
        padding: 0.8rem;
        border-radius: 6px;
        margin-top: 0.5rem;
        border: 1px solid #e0e0e0;
        word-break: break-all;
        color: #666;
        font-size: 0.9rem;
    }
    
    .sidebar-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
    }
    
    .sidebar-section h3 {
        color: #667eea;
        margin-bottom: 1rem;
        font-size: 1.1rem;
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
    **YouTube Summarizer Pro** is an AI-powered tool that generates concise summaries of YouTube videos.
    
    - ✨ Multiple summary formats
    - 🏷️ Keyword extraction
    - ⏱️ Timestamp support
    - 💾 History tracking
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# Main Content
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Header
st.markdown("""
<div class="header-section">
    <h1>🎬 YouTube Summarizer Pro</h1>
    <p>Transform Your Videos into Instant Summaries</p>
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
        <h3>🔄 One-Click</h3>
        <p>Simple, intuitive interface</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Input Section
st.markdown('<div class="input-section">', unsafe_allow_html=True)
st.markdown('<p class="input-label">📌 Paste Your YouTube Link</p>', unsafe_allow_html=True)

col1, col2 = st.columns([4, 1])
with col1:
    youtube_url = st.text_input(
        "YouTube URL",
        placeholder="https://youtu.be/6bnDzZDiCkA or https://www.youtube.com/watch?v=...",
        label_visibility="collapsed"
    )
    if youtube_url:
        st.markdown(f'<div class="url-preview">✓ {youtube_url}</div>', unsafe_allow_html=True)

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
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
        
        except requests.exceptions.Timeout:
            st.markdown('<div class="error-box">⏱️ Request timed out. The video might be too long. Please try again.</div>', unsafe_allow_html=True)
        except requests.exceptions.RequestException as e:
            st.markdown(f'<div class="error-box">❌ Error: {str(e)}</div>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="error-box">❌ Unexpected error: {str(e)}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #999; padding: 2rem;">
    <p>YouTube Summarizer Pro | Powered by n8n & Streamlit</p>
    <p style="font-size: 0.9rem;">© 2025 All rights reserved</p>
</div>
""", unsafe_allow_html=True)
