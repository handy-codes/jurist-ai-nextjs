# FILE: modules/query_builder.py
import streamlit as st
import os
import requests
from dotenv import load_dotenv
from utils.auth import login_required

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@login_required
def query_builder_ui():
    st.header("📂 AI Legal Query Builder")
    st.write("Compose structured legal queries with ease.")

    party = st.text_input("Party Involved (e.g., Landlord, Employer, Government)")
    issue = st.text_input("Legal Issue (e.g., Breach of contract, Land dispute, Arrest)")
    location = st.text_input("Location or Jurisdiction")
    context = st.text_area("Case Context (short background, relevant clauses or sections)")

    if st.button("Generate Legal Query"):
        query_prompt = f"""
You are a legal assistant helping prepare structured legal queries under Nigerian law.

Here is the case:
Party: {party}
Issue: {issue}
Location: {location}
Context: {context}

Compose a concise legal question that could be used to query Nigerian law databases.
"""

        with st.spinner("Generating legal query..."):
            # Use Groq API if available
            if GROQ_API_KEY:
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {GROQ_API_KEY}"
                }
                payload = {
                    "model": "llama3-8b-8192",
                    "messages": [{"role": "user", "content": query_prompt}],
                    "temperature": 0.3,
                    "max_tokens": 400,
                    "stream": False
                }
                response = requests.post(url, headers=headers, json=payload)
                if response.status_code == 200:
                    structured_query = response.json()["choices"][0]["message"]["content"]
                else:
                    st.error(f"Groq API error: {response.status_code} {response.text}")
                    structured_query = None

            # Fallback to OpenAI if Groq API key missing or error
            elif OPENAI_API_KEY:
                import openai
                openai.api_key = OPENAI_API_KEY
                try:
                    resp = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": query_prompt}],
                        temperature=0.3,
                        max_tokens=400,
                    )
                    structured_query = resp.choices[0].message.content
                except Exception as e:
                    st.error(f"OpenAI API error: {e}")
                    structured_query = None

            else:
                st.error("No valid API key found. Please set GROQ_API_KEY or OPENAI_API_KEY in your environment.")
                structured_query = None

        if structured_query:
            st.subheader("🧠 AI-Generated Legal Query")
            st.code(structured_query)
            st.success("✅ Legal query created")





# # FILE: modules/query_builder.py
# import streamlit as st
# import openai
# import os
# from dotenv import load_dotenv

# load_dotenv()
# openai.api_key = os.getenv("OPENAI_API_KEY")

# def query_builder_ui():
#     st.header("📂 AI Legal Query Builder")
#     st.write("Compose structured legal queries with ease.")

#     party = st.text_input("Party Involved (e.g., Landlord, Employer, Government)")
#     issue = st.text_input("Legal Issue (e.g., Breach of contract, Land dispute, Arrest)")
#     location = st.text_input("Location or Jurisdiction")
#     context = st.text_area("Case Context (short background, relevant clauses or sections)")

#     if st.button("Generate Legal Query"):
#         query_prompt = f"""
# You are a legal assistant helping prepare structured legal queries under Nigerian law.

# Here is the case:
# Party: {party}
# Issue: {issue}
# Location: {location}
# Context: {context}

# Compose a concise legal question that could be used to query Nigerian law databases.
# """

#         with st.spinner("Generating legal query..."):
#             response = openai.ChatCompletion.create(
#                 model="gpt-4",
#                 messages=[{"role": "user", "content": query_prompt}],
#                 temperature=0.3
#             )
#             structured_query = response.choices[0].message.content

#         st.subheader("🧠 AI-Generated Legal Query")
#         st.code(structured_query)
#         st.success("✅ Legal query created")
