import gradio as gr
import requests
import re
import json
from datetime import datetime
from typing import Optional, Dict, Any
import google.generativeai as genai
import os

# Constants
WEBHOOK_URL = "https://sushiiel7890.app.n8n.cloud/webhook/ytube"
YOUTUBE_REGEX = re.compile(r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Initialize Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Global state for chat history
chat_history = []
summary_data = {}

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

def summarize_video(youtube_url: str, output_format: str) -> str:
    """Summarize YouTube video"""
    if not youtube_url.strip():
        return "❌ Error: Please enter a YouTube URL"
    
    if not validate_youtube_url(youtube_url.strip()):
        return "❌ Error: Invalid YouTube URL. Please check and try again."
    
    try:
        video_id = extract_video_id(youtube_url.strip())
        
        with gr.Progress() as progress:
            progress(0.5, desc="Processing your video...")
            
            payload = {
                "youtubeUrl": youtube_url.strip(),
                "format": output_format,
                "timestamp": datetime.now().isoformat()
            }
            response = requests.post(WEBHOOK_URL, json=payload, timeout=90)
            response.raise_for_status()
            response_data = response.json()
        
        progress(1.0, desc="Complete!")
        
        # Store summary data for chatbot context
        global summary_data
        summary_data = response_data
        
        # Format response
        result = f"""✅ **Summary Generated Successfully!**

📌 **Video ID:** {video_id}
📋 **Format:** {output_format}

**Summary Output:**
```json
{json.dumps(response_data, indent=2)}
```"""
        
        return result
    
    except requests.exceptions.Timeout:
        return "❌ Error: Request timed out. The video might be too long. Please try again."
    except requests.exceptions.RequestException as e:
        return f"❌ Error: Failed to process video - {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"

def download_json(output_format: str) -> tuple:
    """Generate downloadable JSON"""
    if not summary_data:
        return None, "No summary data available"
    
    filename = f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    data = json.dumps(summary_data, indent=2)
    return data, filename

def download_text(output_format: str) -> tuple:
    """Generate downloadable text"""
    if not summary_data:
        return None, "No summary data available"
    
    filename = f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    data = str(summary_data)
    return data, filename

def chat_with_ai(user_message: str, chat_state: list) -> tuple:
    """Chat with Gemini AI"""
    if not GEMINI_API_KEY:
        return chat_state + [("System", "❌ Gemini API is not configured.")], ""
    
    if not user_message.strip():
        return chat_state, ""
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        # Build context with summary if available
        context = ""
        if summary_data:
            context = f"Context from YouTube video summary:\n{str(summary_data)[:1000]}\n\n"
        
        full_message = f"{context}User question: {user_message}"
        response = model.generate_content(full_message)
        bot_response = response.text
        
        # Add to chat history
        chat_state = chat_state + [(user_message, bot_response)]
        
        return chat_state, ""
    
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        return chat_state + [("System", error_msg)], ""

def clear_chat() -> list:
    """Clear chat history"""
    return []

# Custom CSS
custom_css = """
body {
    font-family: 'Inter', 'Segoe UI', sans-serif;
    background: white;
}

.gradio-container {
    background: white;
}

.gr-header {
    background: linear-gradient(135deg, #ff8c00 0%, #ff9f1a 100%);
    color: white;
    padding: 2rem;
    border-radius: 0;
}

.gr-header h1 {
    font-size: 2.5rem;
    font-weight: 900;
    margin: 0;
    letter-spacing: -1px;
}

.gr-header p {
    margin-top: 0.5rem;
    font-size: 1rem;
    opacity: 0.95;
}

.tab-header {
    background: linear-gradient(135deg, #ff8c00 0%, #ff9f1a 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 8px;
    margin-bottom: 1.5rem;
}

.input-section {
    background: #f9f9f9;
    padding: 2rem;
    border-radius: 12px;
    border-left: 6px solid #ff8c00;
}

.result-box {
    background: #f9f9f9;
    border-left: 6px solid #ff8c00;
    padding: 1.5rem;
    border-radius: 8px;
}

.stat-box {
    background: linear-gradient(135deg, #ff8c00 0%, #ff9f1a 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 8px;
    text-align: center;
    font-weight: 600;
}

.chat-interface {
    background: #f9f9f9;
    border: 2px solid #ff8c00;
    border-radius: 12px;
    padding: 1.5rem;
}

.gr-button {
    background: #ff8c00 !important;
    color: white !important;
    font-weight: 600;
    border: none !important;
    border-radius: 8px !important;
}

.gr-button:hover {
    background: #ff7700 !important;
    box-shadow: 0 6px 15px rgba(255, 140, 0, 0.3) !important;
}

.gr-textbox, .gr-dropdown {
    border: 2px solid #ff8c00 !important;
    border-radius: 8px !important;
}

.gr-textbox:focus, .gr-dropdown:focus {
    border-color: #ff7700 !important;
    box-shadow: 0 0 0 3px rgba(255, 140, 0, 0.1) !important;
}

.gr-info {
    background: #fff5e5;
    border-left: 6px solid #ff8c00;
    color: #994400;
}

.gr-error {
    background: #ffe5e5;
    border-left: 6px solid #cc0000;
    color: #990000;
}

.gr-block {
    border: none !important;
}

.footer {
    text-align: center;
    color: #666;
    padding: 2rem 1rem;
    margin-top: 3rem;
    border-top: 2px solid #ff8c00;
}
"""

# Create Gradio Interface
with gr.Blocks(css=custom_css, theme=gr.themes.Soft()) as demo:
    
    # Header
    gr.HTML("""
    <div style="background: linear-gradient(135deg, #ff8c00 0%, #ff9f1a 100%); 
                color: white; padding: 2.5rem; text-align: center; border-radius: 0; margin: -1.5rem -1.5rem 2rem -1.5rem;">
        <h1 style="font-size: 2.8rem; font-weight: 900; margin: 0; letter-spacing: -1px;">
            YouTube Summarizer Pro
        </h1>
        <p style="margin-top: 0.5rem; font-size: 1.1rem; opacity: 0.95; font-weight: 500;">
            Transform Videos into Instant Summaries with AI Chat
        </p>
    </div>
    """)
    
    with gr.Tabs():
        
        # Summarizer Tab
        with gr.Tab("📝 Summarizer"):
            gr.HTML("<div style='background: #f9f9f9; padding: 1.5rem; border-radius: 8px; border-left: 6px solid #ff8c00; margin-bottom: 1.5rem;'><h3 style='margin: 0; color: #ff8c00;'>Enter YouTube Video Details</h3></div>")
            
            with gr.Row():
                youtube_url = gr.Textbox(
                    label="YouTube URL",
                    placeholder="https://youtu.be/6bnDzZDiCkA",
                    lines=1,
                    interactive=True
                )
            
            with gr.Row():
                output_format = gr.Dropdown(
                    choices=["Summary", "Timestamps", "Key Points", "Full Transcript"],
                    value="Summary",
                    label="Output Format",
                    interactive=True
                )
            
            with gr.Row():
                summarize_btn = gr.Button("✨ Summarize", size="lg", scale=2)
                clear_btn = gr.Button("🔄 Clear", scale=1)
            
            gr.HTML("<hr style='border: none; border-top: 2px solid #ff8c00; margin: 2rem 0;'>")
            
            summary_output = gr.Markdown(
                value="Enter a YouTube URL and click Summarize to get started!",
                label="Result"
            )
            
            with gr.Row():
                download_json_btn = gr.Button("📥 Download JSON", size="sm", scale=1)
                download_text_btn = gr.Button("📄 Download Text", size="sm", scale=1)
            
            # Connect buttons
            summarize_btn.click(
                fn=summarize_video,
                inputs=[youtube_url, output_format],
                outputs=summary_output
            )
            
            clear_btn.click(
                fn=lambda: ("", None),
                outputs=[youtube_url, summary_output]
            )
        
        # Chatbot Tab
        with gr.Tab("💬 Chatbot"):
            gr.HTML("<div style='background: #f9f9f9; padding: 1.5rem; border-radius: 8px; border-left: 6px solid #ff8c00; margin-bottom: 1.5rem;'><h3 style='margin: 0; color: #ff8c00;'>🤖 AI Chat Assistant</h3><p style='margin: 0.5rem 0 0 0; color: #666;'>Ask questions about the video summary or any topic!</p></div>")
            
            chat_display = gr.Chatbot(
                label="Chat History",
                show_label=True,
                value=[],
                scale=1
            )
            
            with gr.Row():
                chat_input = gr.Textbox(
                    label="Your Message",
                    placeholder="Type your question...",
                    lines=1,
                    scale=4,
                    interactive=True
                )
                send_btn = gr.Button("Send", size="lg", scale=1)
            
            with gr.Row():
                clear_chat_btn = gr.Button("🗑️ Clear Chat", scale=1)
                info_btn = gr.Button("ℹ️ Info", scale=1)
            
            # Connect chat buttons
            send_btn.click(
                fn=chat_with_ai,
                inputs=[chat_input, chat_display],
                outputs=[chat_display, chat_input]
            )
            
            clear_chat_btn.click(
                fn=clear_chat,
                outputs=chat_display
            )
            
            info_btn.click(
                fn=lambda: "💡 **How to use:**\n\n1. Summarize a video in the 'Summarizer' tab\n2. Ask questions about the summary here\n3. The AI will use the video context to answer your questions\n\n**Features:**\n- Context-aware responses\n- Multiple question support\n- Clear chat history anytime",
                outputs=None
            )
        
        # Analysis Tab
        with gr.Tab("📊 Analysis"):
            gr.HTML("<div style='background: #f9f9f9; padding: 1.5rem; border-radius: 8px; border-left: 6px solid #ff8c00; margin-bottom: 1.5rem;'><h3 style='margin: 0; color: #ff8c00;'>📊 Statistics & Information</h3></div>")
            
            with gr.Row():
                stat1 = gr.Stat(
                    value="0",
                    label="Total Summaries",
                    variant="huggingface"
                )
                stat2 = gr.Stat(
                    value="0",
                    label="Chat Messages",
                    variant="huggingface"
                )
            
            gr.HTML("""
            <div style='background: white; border: 2px solid #ff8c00; border-radius: 8px; padding: 2rem; text-align: center; margin-top: 2rem;'>
                <h3 style='color: #ff8c00; margin-top: 0;'>🚀 Getting Started</h3>
                <p style='color: #666;'>
                    1. Go to the <strong>Summarizer tab</strong><br>
                    2. Paste your YouTube URL<br>
                    3. Select output format<br>
                    4. Click <strong>Summarize</strong><br>
                    5. Use the <strong>Chatbot</strong> to ask questions
                </p>
            </div>
            """)
    
    # Footer
    gr.HTML("""
    <div style='text-align: center; color: #666; padding: 2rem 1rem; margin-top: 3rem; border-top: 2px solid #ff8c00;'>
        <p style='margin: 0.3rem 0; font-weight: 500;'>🎬 YouTube Summarizer Pro | Powered by n8n, Gemini AI & Gradio</p>
        <p style='font-size: 0.9rem; margin: 0.3rem 0;'>© 2025 All rights reserved</p>
    </div>
    """)

# Launch the app
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
