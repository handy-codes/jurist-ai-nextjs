# FILE: modules/law_search.py
import streamlit as st
import os
import requests
from dotenv import load_dotenv
from utils.auth import login_required

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@login_required
def law_search_ui():
    st.header("🔍 Nigerian Law Search")
    st.write("Search Nigerian laws and acts (e.g., NDLEA Act, EFCC Act, Land Use Act)")

    query = st.text_input("Enter a legal term, section, or phrase to search Nigerian law")

    if st.button("Search Law") and query:
        prompt = f"""
You are a legal AI assistant trained in Nigerian law. Explain the following legal query:

Query: {query}

Ensure your explanation references the appropriate Nigerian Act or legal framework.
"""

        with st.spinner("Searching legal database..."):
            # Try Groq API with LLaMA 3 if API key exists
            if GROQ_API_KEY:
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {GROQ_API_KEY}"
                }
                payload = {
                    "model": "llama3-8b-8192",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 500,
                    "stream": False
                }
                response = requests.post(url, headers=headers, json=payload)
                if response.status_code == 200:
                    explanation = response.json()["choices"][0]["message"]["content"]
                else:
                    st.error(f"Groq API error: {response.status_code} {response.text}")
                    explanation = None

            # Fallback to OpenAI API if Groq key missing or error
            elif OPENAI_API_KEY:
                import openai
                openai.api_key = OPENAI_API_KEY
                try:
                    resp = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.2,
                        max_tokens=500,
                    )
                    explanation = resp.choices[0].message.content
                except Exception as e:
                    st.error(f"OpenAI API error: {e}")
                    explanation = None

            else:
                st.error("No valid API key found. Please set GROQ_API_KEY or OPENAI_API_KEY in your environment.")
                explanation = None

        if explanation:
            st.subheader("📚 Explanation")
            st.write(explanation)
            st.success("✅ Law explained successfully")





# # FILE: modules/law_search.py
# import streamlit as st
# import openai
# import os
# from dotenv import load_dotenv

# load_dotenv()
# openai.api_key = os.getenv("OPENAI_API_KEY")

# def law_search_ui():
#     st.header("🔍 Nigerian Law Search")
#     st.write("Search Nigerian laws and acts (e.g., NDLEA Act, EFCC Act, Land Use Act)")

#     query = st.text_input("Enter a legal term, section, or phrase to search Nigerian law")

#     if st.button("Search Law") and query:
#         prompt = f"""
# You are a legal AI assistant trained in Nigerian law. Explain the following legal query:

# Query: {query}

# Ensure your explanation references the appropriate Nigerian Act or legal framework.
# """

#         with st.spinner("Searching legal database..."):
#             response = openai.ChatCompletion.create(
#                 model="gpt-4",
#                 messages=[{"role": "user", "content": prompt}],
#                 temperature=0.2
#             )
#             explanation = response.choices[0].message.content

#         st.subheader("📚 Explanation")
#         st.write(explanation)
#         st.success("✅ Law explained successfully")
