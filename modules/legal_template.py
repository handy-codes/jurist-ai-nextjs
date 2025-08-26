# FILE: modules/legal_template.py
import streamlit as st
import os
import requests
from dotenv import load_dotenv
from utils.auth import login_required

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@login_required
def template_builder_ui():
    st.header("📝 Legal Template Generator")
    st.write("Draft NDAs, leases, contracts using AI trained on Nigerian legal structures.")

    template_type = st.selectbox("Choose document type", [
        "Non-Disclosure Agreement (NDA)",
        "Lease Agreement",
        "Employment Contract",
        "Service Agreement",
        "Partnership Agreement"
    ])

    key_terms = st.text_area("Enter key terms (e.g. parties, duration, location, obligations, etc.)")

    if st.button("Generate Document"):
        prompt = f"""
You are a Nigerian legal AI assistant. Draft a {template_type} based on the following key terms:
{key_terms}

The output should be formatted as a complete legal document under Nigerian law.
"""

        with st.spinner("Generating document..."):
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
                    "max_tokens": 1000,
                    "stream": False
                }
                response = requests.post(url, headers=headers, json=payload)
                if response.status_code == 200:
                    document = response.json()["choices"][0]["message"]["content"]
                else:
                    st.error(f"Groq API error: {response.status_code} {response.text}")
                    document = None

            # Fallback to OpenAI if Groq not available or error
            elif OPENAI_API_KEY:
                import openai
                openai.api_key = OPENAI_API_KEY
                try:
                    resp = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.3,
                        max_tokens=1000,
                    )
                    document = resp.choices[0].message.content
                except Exception as e:
                    st.error(f"OpenAI API error: {e}")
                    document = None
            else:
                st.error("No valid API key found. Please set GROQ_API_KEY or OPENAI_API_KEY in your environment.")
                document = None

        if document:
            st.subheader("📄 Generated Document")
            st.code(document, language="markdown")
            st.success("✅ Template generated")




# # FILE: modules/legal_templates.py
# import streamlit as st
# import openai
# import os
# from dotenv import load_dotenv

# load_dotenv()
# openai.api_key = os.getenv("OPENAI_API_KEY")

# def template_builder_ui():
#     st.header("📝 Legal Template Generator")
#     st.write("Draft NDAs, leases, contracts using AI trained on Nigerian legal structures.")

#     template_type = st.selectbox("Choose document type", [
#         "Non-Disclosure Agreement (NDA)",
#         "Lease Agreement",
#         "Employment Contract",
#         "Service Agreement",
#         "Partnership Agreement"
#     ])

#     key_terms = st.text_area("Enter key terms (e.g. parties, duration, location, obligations, etc.)")

#     if st.button("Generate Document"):
#         prompt = f"""
# You are a Nigerian legal AI assistant. Draft a {template_type} based on the following key terms:
# {key_terms}

# The output should be formatted as a complete legal document under Nigerian law.
# """
#         with st.spinner("Generating document..."):
#             response = openai.ChatCompletion.create(
#                 model="gpt-4",
#                 messages=[{"role": "user", "content": prompt}],
#                 temperature=0.3
#             )
#             document = response.choices[0].message.content

#         st.subheader("📄 Generated Document")
#         st.code(document, language="markdown")
#         st.success("✅ Template generated")
