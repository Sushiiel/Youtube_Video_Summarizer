from flask import Flask, render_template_string, request, jsonify
import requests
import re
import json
from datetime import datetime
from typing import Optional
import google.generativeai as genai
import os

app = Flask(__name__)

# Constants
WEBHOOK_URL = "https://sushiiel7890.app.n8n.cloud/webhook/ytube"
YOUTUBE_REGEX = re.compile(r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Initialize Gemini
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except:
        pass

# Store data in memory
app.summary_data = {}
app.chat_history = []

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

def chat_with_gemini(user_message: str) -> str:
    """Chat with Gemini AI"""
    if not GEMINI_API_KEY:
        return "❌ Gemini API is not configured."
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        context = ""
        
        if app.summary_data:
            context = f"Context from YouTube video summary:\n{str(app.summary_data)[:1000]}\n\n"
        
        full_message = f"{context}User question: {user_message}"
        response = model.generate_content(full_message)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube Summarizer Pro</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: white;
            color: #333;
        }
        
        .header {
            background: linear-gradient(135deg, #ff8c00 0%, #ff9f1a 100%);
            color: white;
            padding: 3rem 2rem;
            text-align: center;
            box-shadow: 0 4px 15px rgba(255, 140, 0, 0.2);
        }
        
        .header h1 {
            font-size: 2.8rem;
            font-weight: 900;
            letter-spacing: -1px;
            margin-bottom: 0.5rem;
        }
        
        .header p {
            font-size: 1.1rem;
            opacity: 0.95;
            font-weight: 500;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
            padding: 2rem 1rem;
        }
        
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 2rem;
            border-bottom: 2px solid #ff8c00;
            flex-wrap: wrap;
        }
        
        .tab-btn {
            background: #f5f5f5;
            color: #333;
            border: none;
            padding: 12px 24px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            border-radius: 8px 8px 0 0;
            transition: all 0.3s ease;
        }
        
        .tab-btn.active {
            background: #ff8c00;
            color: white;
        }
        
        .tab-btn:hover {
            background: #ff9f1a;
            color: white;
        }
        
        .tab-content {
            display: none;
            animation: fadeIn 0.3s ease;
        }
        
        .tab-content.active {
            display: block;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .input-section {
            background: #f9f9f9;
            padding: 2rem;
            border-radius: 12px;
            border-left: 6px solid #ff8c00;
            margin-bottom: 2rem;
        }
        
        .input-section h3 {
            color: #ff8c00;
            margin-bottom: 1.5rem;
            font-size: 1.2rem;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 600;
            color: #333;
        }
        
        input[type="text"],
        select,
        textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #ff8c00;
            border-radius: 8px;
            font-size: 1rem;
            font-family: inherit;
            transition: all 0.3s ease;
        }
        
        input[type="text"]:focus,
        select:focus,
        textarea:focus {
            outline: none;
            border-color: #ff7700;
            box-shadow: 0 0 0 3px rgba(255, 140, 0, 0.1);
        }
        
        .button-group {
            display: flex;
            gap: 1rem;
            margin-top: 2rem;
            flex-wrap: wrap;
        }
        
        button {
            background: #ff8c00;
            color: white;
            border: none;
            padding: 12px 24px;
            font-size: 1rem;
            font-weight: 600;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        button:hover {
            background: #ff7700;
            box-shadow: 0 6px 15px rgba(255, 140, 0, 0.3);
        }
        
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
            box-shadow: none;
        }
        
        .output-box {
            background: #f9f9f9;
            border-left: 6px solid #ff8c00;
            padding: 2rem;
            border-radius: 8px;
            margin-top: 2rem;
            max-height: 600px;
            overflow-y: auto;
            word-wrap: break-word;
            white-space: normal;
        }
        
        .output-box h4 {
            color: #ff8c00;
            margin-bottom: 1rem;
            font-size: 1.1rem;
        }
        
        .output-box pre {
            background: white;
            padding: 1.5rem;
            border-radius: 6px;
            border: 1px solid #ddd;
            overflow-x: visible;
            overflow-y: auto;
            font-size: 0.95rem;
            line-height: 1.6;
            white-space: pre-wrap;
            word-wrap: break-word;
            max-height: 500px;
        }
        
        .summary-section {
            background: white;
            padding: 1.5rem;
            border-radius: 6px;
            border: 1px solid #ddd;
            margin-bottom: 1rem;
            line-height: 1.8;
        }
        
        .summary-section h5 {
            color: #ff8c00;
            margin-bottom: 0.8rem;
            font-size: 1rem;
        }
        
        .summary-section p {
            color: #333;
            margin-bottom: 0.8rem;
            text-align: justify;
        }
        
        .summary-list {
            color: #333;
            margin-left: 1.5rem;
            line-height: 1.8;
        }
        
        .summary-list li {
            margin-bottom: 0.8rem;
        }
        
        .success {
            background: #e5ffe5;
            border-left: 6px solid #00aa00;
            color: #006600;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        
        .error {
            background: #ffe5e5;
            border-left: 6px solid #cc0000;
            color: #990000;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        
        .info {
            background: #fff5e5;
            border-left: 6px solid #ff8c00;
            color: #994400;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .stat-box {
            background: linear-gradient(135deg, #ff8c00 0%, #ff9f1a 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 8px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 1.8rem;
            font-weight: 900;
            margin-bottom: 0.5rem;
        }
        
        .stat-label {
            font-size: 0.9rem;
            opacity: 0.95;
        }
        
        .chat-box {
            background: white;
            border: 2px solid #ff8c00;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            max-height: 400px;
            overflow-y: auto;
        }
        
        .chat-message {
            margin-bottom: 1rem;
            padding: 1rem;
            border-radius: 8px;
        }
        
        .chat-user {
            background: #ff8c00;
            color: white;
            margin-left: 1rem;
            border-bottom-right-radius: 0;
        }
        
        .chat-bot {
            background: #f9f9f9;
            color: #333;
            margin-right: 1rem;
            border-left: 4px solid #ff8c00;
            border-bottom-left-radius: 0;
        }
        
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #ff8c00;
            border-radius: 50%;
            border-top-color: transparent;
            animation: spin 0.8s linear infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .footer {
            text-align: center;
            color: #666;
            padding: 2rem 1rem;
            margin-top: 3rem;
            border-top: 2px solid #ff8c00;
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2rem;
            }
            
            .button-group {
                flex-direction: column;
            }
            
            button {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎬 YouTube Summarizer Pro</h1>
        <p>Transform Videos into Instant Summaries with AI Chat</p>
    </div>
    
    <div class="container">
        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('summarizer')">📝 Summarizer</button>
            <button class="tab-btn" onclick="switchTab('chatbot')">💬 Chatbot</button>
            <button class="tab-btn" onclick="switchTab('analytics')">📊 Analytics</button>
        </div>
        
        <!-- Summarizer Tab -->
        <div id="summarizer" class="tab-content active">
            <div class="input-section">
                <h3>Enter YouTube Video Details</h3>
                
                <div class="form-group">
                    <label for="youtube-url">YouTube URL</label>
                    <input type="text" id="youtube-url" placeholder="https://youtu.be/6bnDzZDiCkA">
                </div>
                
                <div class="form-group">
                    <label for="output-format">Output Format</label>
                    <select id="output-format">
                        <option>Summary</option>
                        <option>Timestamps</option>
                        <option>Key Points</option>
                        <option>Full Transcript</option>
                    </select>
                </div>
                
                <div class="button-group">
                    <button onclick="summarizeVideo()">✨ Summarize</button>
                    <button onclick="clearSummary()" style="background: #999;">🔄 Clear</button>
                </div>
            </div>
            
            <div id="summary-output"></div>
        </div>
        
        <!-- Chatbot Tab -->
        <div id="chatbot" class="tab-content">
            <div class="input-section">
                <h3>🤖 AI Chat Assistant</h3>
                <p style="color: #666; margin-bottom: 1rem;">Ask questions about the video summary or any topic!</p>
                
                <div class="chat-box" id="chat-history"></div>
                
                <div class="form-group">
                    <label for="chat-input">Your Message</label>
                    <textarea id="chat-input" placeholder="Type your question..." rows="3"></textarea>
                </div>
                
                <div class="button-group">
                    <button onclick="sendMessage()">Send</button>
                    <button onclick="clearChat()" style="background: #999;">🗑️ Clear Chat</button>
                </div>
            </div>
        </div>
        
        <!-- Analytics Tab -->
        <div id="analytics" class="tab-content">
            <div class="input-section">
                <h3>📊 Statistics & Information</h3>
                
                <div class="stats">
                    <div class="stat-box">
                        <div class="stat-value" id="stat-summaries">0</div>
                        <div class="stat-label">Total Summaries</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value" id="stat-messages">0</div>
                        <div class="stat-label">Chat Messages</div>
                    </div>
                </div>
                
                <div style="background: white; border: 2px solid #ff8c00; border-radius: 8px; padding: 2rem; text-align: center;">
                    <h3 style="color: #ff8c00; margin-bottom: 1rem;">🚀 Getting Started</h3>
                    <p style="color: #666; line-height: 1.8;">
                        1. Go to the <strong>Summarizer tab</strong><br>
                        2. Paste your YouTube URL<br>
                        3. Select output format<br>
                        4. Click <strong>Summarize</strong><br>
                        5. Use the <strong>Chatbot</strong> to ask questions
                    </p>
                </div>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>🎬 YouTube Summarizer Pro | Powered by n8n, Gemini AI & Flask</p>
        <p style="font-size: 0.9rem;">© 2025 All rights reserved</p>
    </div>
    
    <script>
        let summaryCount = 0;
        let messageCount = 0;
        
        function escapeHtml(text) {
            const map = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            };
            return text.replace(/[&<>"']/g, m => map[m]);
        }
        
        function switchTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }
        
        async function summarizeVideo() {
            const url = document.getElementById('youtube-url').value;
            const format = document.getElementById('output-format').value;
            const outputDiv = document.getElementById('summary-output');
            
            if (!url.trim()) {
                outputDiv.innerHTML = '<div class="error">❌ Please enter a YouTube URL</div>';
                return;
            }
            
            outputDiv.innerHTML = '<div class="info"><div class="loading"></div> Processing...</div>';
            
            try {
                const response = await fetch('/api/summarize', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url, format })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    summaryCount++;
                    document.getElementById('stat-summaries').textContent = summaryCount;
                    
                    const summary = data.summary;
                    let summaryHTML = `
                        <div class="success">✅ Summary generated successfully!</div>
                        <div class="stats">
                            <div class="stat-box">
                                <div class="stat-value">${data.video_id}</div>
                                <div class="stat-label">Video ID</div>
                            </div>
                            <div class="stat-box">
                                <div class="stat-value">${format}</div>
                                <div class="stat-label">Format</div>
                            </div>
                        </div>
                        <div class="output-box">
                            <h4>📝 Summary Output</h4>
                    `;
                    
                    if (summary.title) {
                        summaryHTML += `<div class="summary-section">
                            <h5>📌 Title</h5>
                            <p>${escapeHtml(summary.title)}</p>
                        </div>`;
                    }
                    
                    if (summary.description) {
                        summaryHTML += `<div class="summary-section">
                            <h5>📖 Description</h5>
                            <p>${escapeHtml(summary.description).substring(0, 300)}...</p>
                        </div>`;
                    }
                    
                    if (summary.summary) {
                        summaryHTML += `<div class="summary-section">
                            <h5>✨ Key Summary</h5>
                            <p>${escapeHtml(summary.summary)}</p>
                        </div>`;
                    }
                    
                    if (summary.topics && summary.topics.length > 0) {
                        summaryHTML += `<div class="summary-section">
                            <h5>🎯 Topics Covered</h5>
                            <ul class="summary-list">
                                ${summary.topics.map(topic => `<li>${escapeHtml(topic)}</li>`).join('')}
                            </ul>
                        </div>`;
                    }
                    
                    summaryHTML += `<div class="summary-section">
                        <h5>🔗 Full Data</h5>
                        <pre>${JSON.stringify(summary, null, 2)}</pre>
                    </div></div>`;
                    
                    outputDiv.innerHTML = summaryHTML;
                } else {
                    outputDiv.innerHTML = `<div class="error">❌ ${data.error}</div>`;
                }
            } catch (error) {
                outputDiv.innerHTML = `<div class="error">❌ Error: ${error.message}</div>`;
            }
        }
        
        function clearSummary() {
            document.getElementById('youtube-url').value = '';
            document.getElementById('summary-output').innerHTML = '';
        }
        
        async function sendMessage() {
            const input = document.getElementById('chat-input');
            const message = input.value.trim();
            
            if (!message) return;
            
            const chatHistory = document.getElementById('chat-history');
            
            // Add user message
            const userDiv = document.createElement('div');
            userDiv.className = 'chat-message chat-user';
            userDiv.textContent = 'You: ' + message;
            chatHistory.appendChild(userDiv);
            
            input.value = '';
            chatHistory.scrollTop = chatHistory.scrollHeight;
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message })
                });
                
                const data = await response.json();
                
                // Add bot message
                const botDiv = document.createElement('div');
                botDiv.className = 'chat-message chat-bot';
                botDiv.textContent = 'AI: ' + data.response;
                chatHistory.appendChild(botDiv);
                
                messageCount += 2;
                document.getElementById('stat-messages').textContent = messageCount;
                chatHistory.scrollTop = chatHistory.scrollHeight;
            } catch (error) {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'chat-message chat-bot';
                errorDiv.textContent = 'AI: Error - ' + error.message;
                chatHistory.appendChild(errorDiv);
            }
        }
        
        function clearChat() {
            document.getElementById('chat-history').innerHTML = '';
            fetch('/api/clear-chat', { method: 'POST' });
            messageCount = 0;
            document.getElementById('stat-messages').textContent = '0';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/summarize', methods=['POST'])
def summarize():
    data = request.json
    youtube_url = data.get('url', '').strip()
    output_format = data.get('format', 'Summary')
    
    if not youtube_url:
        return jsonify({'success': False, 'error': 'Please enter a YouTube URL'})
    
    if not YOUTUBE_REGEX.match(youtube_url):
        return jsonify({'success': False, 'error': 'Invalid YouTube URL'})
    
    try:
        video_id = extract_video_id(youtube_url)
        
        payload = {
            "youtubeUrl": youtube_url,
            "format": output_format,
            "timestamp": datetime.now().isoformat()
        }
        
        response = requests.post(WEBHOOK_URL, json=payload, timeout=90)
        response.raise_for_status()
        response_data = response.json()
        
        app.summary_data = response_data
        
        return jsonify({
            'success': True,
            'video_id': video_id[:8] if video_id else 'unknown',
            'summary': response_data
        })
    
    except requests.exceptions.Timeout:
        return jsonify({'success': False, 'error': 'Request timed out'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'response': 'Please enter a message'})
    
    response_text = chat_with_gemini(user_message)
    app.chat_history.append({'user': user_message, 'bot': response_text})
    
    return jsonify({'response': response_text})

@app.route('/api/clear-chat', methods=['POST'])
def clear_chat_route():
    app.chat_history = []
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=False
    )
