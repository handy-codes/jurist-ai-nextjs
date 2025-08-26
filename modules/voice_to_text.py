# FILE: modules/voice_to_text.py

import streamlit as st
import os
import json
from dotenv import load_dotenv
import httpx  # you need to pip install httpx

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# Hypothetical Groq endpoint
GROQ_API_URL = "https://api.groq.com/openai/v1/audio/transcriptions"


def voice_to_text_ui():
    st.header("🎤 Voice to Text - Legal AI Assistant (via Groq LLaMA 3)")

    audio_file = st.file_uploader(
        "Upload your voice recording (MP3, WAV, M4A)", type=["mp3", "wav", "m4a"])

    if audio_file is not None:
        with st.spinner("Transcribing audio using Groq LLaMA 3..."):
            try:
                if not GROQ_API_KEY:
                    st.error(
                        "No Groq API key found. Please set GROQ_API_KEY in your environment.")
                    return

                # Prepare multipart/form-data for file upload
                files = {
                    "file": (audio_file.name, audio_file, audio_file.type),
                    # keep the same model name or change based on Groq docs
                    "model": (None, "whisper-1"),
                    "response_format": (None, "json")
                }

                headers = {
                    "Authorization": f"Bearer {GROQ_API_KEY}"
                }

                with httpx.Client(timeout=30) as client:
                    response = client.post(
                        GROQ_API_URL, headers=headers, files=files)

                response.raise_for_status()
                data = response.json()
                # Assuming Groq returns the transcript as 'text' key, like OpenAI
                transcript_text = data.get("text", "")

                if transcript_text:
                    st.subheader("📝 Transcription")
                    st.write(transcript_text)
                    st.success("✅ Transcription completed successfully")
                    st.session_state['transcript_text'] = transcript_text
                else:
                    st.error("No transcription text found in the response.")

            except httpx.HTTPStatusError as e:
                st.error(
                    f"HTTP error: {e.response.status_code} - {e.response.text}")
            except Exception as e:
                st.error(f"Error during transcription: {e}")


# # FILE: modules/voice_to_text.py

# import streamlit as st
# import os
# from dotenv import load_dotenv

# load_dotenv()
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# def voice_to_text_ui():
#     st.header("🎤 Voice to Text - Legal AI Assistant")
#     st.write("Speak your legal question or issue and get instant transcription.")

#     audio_file = st.file_uploader("Upload your voice recording (MP3, WAV, M4A)", type=["mp3", "wav", "m4a"])

#     if audio_file is not None:
#         with st.spinner("Transcribing audio..."):
#             transcript_text = None

#             if OPENAI_API_KEY:
#                 try:
#                     import openai
#                     openai.api_key = OPENAI_API_KEY

#                     transcript = openai.Audio.transcribe("whisper-1", audio_file)
#                     transcript_text = transcript.text
#                 except Exception as e:
#                     st.error(f"OpenAI Whisper API error: {e}")
#             else:
#                 st.error("No OpenAI API key found. Please set OPENAI_API_KEY in your environment.")

#             if transcript_text:
#                 st.subheader("📝 Transcription")
#                 st.write(transcript_text)
#                 st.success("✅ Transcription completed successfully")


# # FILE: modules/voice_to_text.py

# import streamlit as st
# import os
# import requests
# from dotenv import load_dotenv

# load_dotenv()
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# def voice_to_text_ui():
#     st.header("🎤 Voice to Text - Legal AI Assistant")
#     st.write("Speak your legal question or issue and get instant transcription.")

#     audio_file = st.file_uploader("Upload your voice recording (MP3, WAV, M4A)", type=["mp3", "wav", "m4a"])

#     if audio_file is not None:
#         with st.spinner("Transcribing audio..."):
#             transcript_text = None

#             # Groq does not support audio transcription currently, fallback to OpenAI Whisper
#             if OPENAI_API_KEY:
#                 try:
#                     import openai
#                     openai.api_key = OPENAI_API_KEY

#                     # Use openai.Audio.transcribe for whisper-1 model
#                     transcript = openai.Audio.transcribe("whisper-1", audio_file)
#                     transcript_text = transcript.text
#                 except Exception as e:
#                     st.error(f"OpenAI Whisper API error: {e}")

#             else:
#                 st.error("No OpenAI API key found. Please set OPENAI_API_KEY in your environment.")

#             if transcript_text:
#                 st.subheader("📝 Transcription")
#                 st.write(transcript_text)
#                 st.success("✅ Transcription completed successfully")


# # FILE: modules/voice_to_text.py

# import streamlit as st
# import openai
# import os
# from dotenv import load_dotenv

# load_dotenv()
# openai.api_key = os.getenv("OPENAI_API_KEY")

# def voice_to_text_ui():
#     st.header("🎤 Voice to Text - Legal AI Assistant")
#     st.write("Speak your legal question or issue and get instant transcription.")

#     audio_file = st.file_uploader("Upload your voice recording (MP3, WAV, etc.)", type=["mp3", "wav", "m4a"])

#     if audio_file is not None:
#         with st.spinner("Transcribing audio..."):
#             transcript = openai.Audio.transcribe("whisper-1", audio_file)
#             st.subheader("📝 Transcription")
#             st.write(transcript.text)
#             st.success("✅ Transcription completed successfully")
