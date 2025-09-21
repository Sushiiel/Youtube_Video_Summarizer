# YouTube Summarizer App

This project provides an end-to-end **YouTube Video Summarizer** built with:

- [n8n](https://n8n.io/) (workflow automation platform)  
- [Streamlit](https://streamlit.io/) (frontend UI for user input)  
- [YouTube Data API](https://developers.google.com/youtube/v3) + LLM summarization  

Users can paste a YouTube link into a **Streamlit UI**, which triggers an **n8n workflow** via a webhook. The workflow extracts the video transcript, summarizes it using AI, and responds back to the frontend.

---

## Features

- Simple **UI with Streamlit** to enter a YouTube link.  
- Secure **Webhook integration with n8n**.  
- **YouTube video ID extraction** from multiple URL formats (`youtu.be`, `youtube.com/watch?v=`, `embed/`, etc.).  
- **Summarization node in n8n** generates a concise summary.  
- Supports both **development** (`/webhook-test/`) and **production** (`/webhook/`) endpoints.  

---

## Project Structure

- youtube_Video_summarizer.json # n8n workflow (import into n8n)
- streamlit_client.py # Streamlit frontend
- README.md # Documentation

  
---

## Setup Instructions

### 1. Import the n8n workflow

1. Log in to your [n8n.cloud](https://app.n8n.cloud) (or self-hosted n8n).  
2. Import `Youtube_Video_summarizer.json`.  
3. Ensure the workflow contains:  
   - **Webhook node** (`/webhook/ytube`)  
   - **Code node** (extracts YouTube Video ID)  
   - **YouTube API node** (fetches video details or transcript)  
   - **Summarization node** (LLM)  
   - **Respond node** (sends summary back to caller).  
4. Activate the workflow (toggle **Active**).  

---

### 2. Run the Streamlit app

Install dependencies:

```bash
pip install streamlit requests
streamlit run streamlit_client.py
