# talk2sign_app.py

import streamlit as st
import speech_recognition as sr
import tempfile
import os
from pathlib import Path

st.set_page_config(page_title="Talk2Sign", layout="wide")

st.markdown("<h1 style='color:#2c3e50; font-family:Poppins;'>🎤 Talk2Sign</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#555;'>Real-time voice-to-sign-language translator</p>", unsafe_allow_html=True)

# Init session state
if "transcript" not in st.session_state:
    st.session_state.transcript = ""
if "video_queue" not in st.session_state:
    st.session_state.video_queue = []

# Upload voice or use mic
st.markdown("### 1️⃣ Speak or Upload Audio")

audio_file = st.file_uploader("Upload an audio file (wav/mp3)", type=["wav", "mp3"])
use_mic = st.button("🎙️ Use Microphone")

if use_mic:
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Speak now...")
        audio = recognizer.listen(source, phrase_time_limit=5)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
        with open(tmp_audio.name, "wb") as f:
            f.write(audio.get_wav_data())
        audio_file = tmp_audio.name

# Transcribe
if audio_file:
    recognizer = sr.Recognizer()
    with sr.audiofile.AudioFile(audio_file) if isinstance(audio_file, str) else sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            st.session_state.transcript += " " + text
        except sr.UnknownValueError:
            st.error("Could not understand the audio.")
        except sr.RequestError:
            st.error("API unavailable. Try again later.")

# Display transcript
st.markdown("### 📝 Transcript")
st.text_area("Transcription", value=st.session_state.transcript.strip(), height=100)

# Download option
if st.session_state.transcript.strip():
    st.download_button("⬇️ Download Transcript", st.session_state.transcript.strip(), file_name="transcript.txt")

# Play Sign Language Videos
def filter_text_and_get_videos(text):
    stop_words = {'is', 'are', 'am', 'the', 'in', 'on', 'a', 'an', 'of', 'to', 'and', 'but', 'or', 'if', 'then', 'so', 'as', 'was', 'were', 'has', 'have', 'had'}
    words = text.lower().strip().split()
    filtered = [word.strip('.,?!') for word in words if word not in stop_words]
    return filtered

st.markdown("### 🧠 Translate to Sign Language")

if st.button("📺 Show Sign Language"):
    st.session_state.video_queue = []

    base_dir = Path("assets")  # Folder with your .mp4 videos
    words = filter_text_and_get_videos(st.session_state.transcript)

    for word in words:
        video_path = base_dir / f"{word.capitalize()}.mp4"
        if video_path.exists():
            st.session_state.video_queue.append(video_path)
        else:
            # Fallback: add letter videos
            for letter in word.upper():
                letter_video = base_dir / f"{letter}.mp4"
                if letter_video.exists():
                    st.session_state.video_queue.append(letter_video)

# Play queued videos
if st.session_state.video_queue:
    st.markdown("### 🎞️ Playing Videos")
    for video in st.session_state.video_queue:
        st.video(str(video))
