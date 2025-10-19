import streamlit as st
import requests
import re

WEBHOOK_URL="https://sushiiel33.app.n8n.cloud/webhook/ytube"

st.set_page_config(page_title="YouTube Summarizer",layout="centered")
st.title("YouTube Summarizer")

YOUTUBE_REGEX=re.compile(r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+")

youtube_url=st.text_input("Paste a YouTube link:",placeholder="https://youtu.be/6bnDzZDiCkA")

if st.button("Summarize"):
    if not youtube_url.strip():
        st.error("Please enter a YouTube URL.")
    elif not YOUTUBE_REGEX.match(youtube_url.strip()):
        st.warning("That doesn't look like a valid YouTube URL.")
    else:
        payload={"youtubeUrl":youtube_url.strip()}
        try:
            with st.spinner("Sending request to workflow..."):
                resp=requests.post(WEBHOOK_URL,json=payload,timeout=90)
                resp.raise_for_status()
            st.success("Workflow triggered successfully!")
            try:
                data=resp.json()
                st.subheader("Response from n8n")
                st.json(data)
            except Exception:
                st.subheader("Response from n8n")
                st.write(resp.text)
        except requests.exceptions.Timeout:
            st.error("Request timed out. Try again later.")
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to call webhook: {e}")
