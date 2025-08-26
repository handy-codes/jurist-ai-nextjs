# utils/voice_input.py
import streamlit as st
import speech_recognition as sr
import pyttsx3
import time
import os
from pydub import AudioSegment
from io import BytesIO

def record_and_transcribe():
    """Record audio from the user's microphone and transcribe it to text"""
    r = sr.Recognizer()
    
    with sr.Microphone() as source:
        st.info("Listening... Speak now")
        audio_data = r.record(source, duration=15)  # Record for 15 seconds max
        st.info("Processing...")
        
        try:
            text = r.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            st.error("Could not understand audio")
            return ""
        except sr.RequestError as e:
            st.error(f"Could not request results: {e}")
            return ""

def text_to_speech(text):
    """Convert text to speech and return as audio file"""
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)  # Female voice
    engine.setProperty('rate', 150)  # Speed percent
    
    # Save to temporary file
    filename = f"tts_{int(time.time())}.mp3"
    engine.save_to_file(text, filename)
    engine.runAndWait()
    
    # Return audio file
    return filename






# from streamlit_webrtc import webrtc_streamer, WebRtcMode, ClientSettings
# import av
# import queue
# from faster_whisper import WhisperModel
# import streamlit as st

# model = WhisperModel("base", compute_type="int8")
# audio_queue = queue.Queue()

# def audio_frame_callback(frame: av.AudioFrame):
#     audio = frame.to_ndarray().flatten().astype("float32") / 32768.0
#     audio_queue.put(audio)
#     return frame

# def transcribe_audio():
#     st.session_state.transcribed_text = ""
#     if not audio_queue.empty():
#         audio_input = list(audio_queue.queue)
#         audio_queue.queue.clear()
#         segments, _ = model.transcribe(audio_input, beam_size=5)
#         st.session_state.transcribed_text = " ".join([seg.text for seg in segments])

# def record_and_transcribe():
#     webrtc_streamer(
#         key="speech",
#         mode=WebRtcMode.SENDONLY,
#         audio_frame_callback=audio_frame_callback,
#         client_settings=ClientSettings(
#             media_stream_constraints={"audio": True, "video": False},
#             rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
#         ),
#     )
#     if st.button("🎙 Transcribe Voice"):
#         transcribe_audio()
