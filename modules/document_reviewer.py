# FILE: modules/document_reviewer.py
import streamlit as st
import fitz  # PyMuPDF
import os
import requests
from dotenv import load_dotenv
from utils.auth import login_required

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def extract_text_from_pdf(uploaded_file):
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        text = "\n".join(page.get_text() for page in doc)
    return text

def summarize_and_flag(text):
    prompt = f"""
You are a Nigerian legal expert AI. Analyze the following legal document and:
1. Summarize its purpose.
2. Highlight any risks or legal red flags.
3. Suggest any missing or weak clauses.

Document:
{text}
"""

    # Try Groq API first
    if GROQ_API_KEY:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROQ_API_KEY}"
        }
        payload = {
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 1500,
            "stream": False
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            st.error(f"Groq API error: {response.status_code} {response.text}")

    # Fallback to OpenAI GPT-4
    if OPENAI_API_KEY:
        import openai
        openai.api_key = OPENAI_API_KEY
        try:
            resp = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1500,
            )
            return resp.choices[0].message.content
        except Exception as e:
            st.error(f"OpenAI API error: {e}")
            return None

    st.error("No valid API key found. Please set GROQ_API_KEY or OPENAI_API_KEY in your environment.")
    return None

@login_required
def document_review_ui():
    st.header("📜 Upload Legal Document for Review")
    uploaded_file = st.file_uploader("Upload PDF file", type=["pdf"])

    if uploaded_file is not None:
        with st.spinner("Reading and analyzing document..."):
            text = extract_text_from_pdf(uploaded_file)
            st.subheader("📝 Extracted Text (Preview)")
            st.text_area("", text[:3000], height=300)

            analysis = summarize_and_flag(text)

        if analysis:
            st.subheader("🧠 AI Analysis Summary")
            st.write(analysis)
            st.success("✅ Review Complete")




