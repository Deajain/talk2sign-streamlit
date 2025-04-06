import streamlit as st
from pathlib import Path
import os

st.set_page_config(page_title="Talk2Sign", layout="wide")

st.markdown("<h1 style='color:#2c3e50; font-family:Poppins;'>🎤 Talk2Sign</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#555;'>Real-time voice-to-sign-language translator</p>", unsafe_allow_html=True)

# Init session state
if "transcript" not in st.session_state:
    st.session_state.transcript = ""
if "video_queue" not in st.session_state:
    st.session_state.video_queue = []

# Upload voice
st.markdown("### 1️⃣ Speak or Upload Audio")
audio_file = st.file_uploader("Upload an audio file (wav/mp3)", type=["wav", "mp3"])

# 🧠 JavaScript Voice Input
st.markdown("Or use your microphone:")
st.components.v1.html("""
    <script>
    const synth = window.speechSynthesis;
    var recognition;
    if (!('webkitSpeechRecognition' in window)) {
        document.write("Speech recognition not supported in this browser.");
    } else {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        function startRecognition() {
            document.getElementById('status').innerText = "Listening...";
            recognition.start();
        }

        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            const streamlitInput = window.parent.document.querySelector('textarea[data-testid="stTextArea"]');
            if (streamlitInput) {
                streamlitInput.value += transcript + " ";
                streamlitInput.dispatchEvent(new Event('input', { bubbles: true }));
            }
            document.getElementById('status').innerText = "Done!";
        };

        recognition.onerror = function(event) {
            document.getElementById('status').innerText = "Error: " + event.error;
        };
    }
    </script>

    <button onclick="startRecognition()">🎙️ Start Talking</button>
    <p id="status"></p>
""", height=150)

# Transcript text area
st.markdown("### 📝 Transcript")
st.session_state.transcript = st.text_area("Transcription", value=st.session_state.transcript.strip(), height=100)

# Download option
if st.session_state.transcript.strip():
    st.download_button("⬇️ Download Transcript", st.session_state.transcript.strip(), file_name="transcript.txt")

# Sign language translation logic
def filter_text_and_get_videos(text):
    stop_words = {'is', 'are', 'am', 'the', 'in', 'on', 'a', 'an', 'of', 'to', 'and', 'but', 'or', 'if', 'then', 'so', 'as', 'was', 'were', 'has', 'have', 'had'}
    words = text.lower().strip().split()
    filtered = [word.strip('.,?!') for word in words if word not in stop_words]
    return filtered

st.markdown("### 🧠 Translate to Sign Language")

if st.button("📺 Show Sign Language"):
    st.session_state.video_queue = []

    base_dir = Path("assets")  # Your video folder
    words = filter_text_and_get_videos(st.session_state.transcript)

    for word in words:
        video_path = base_dir / f"{word.capitalize()}.mp4"
        if video_path.exists():
            st.session_state.video_queue.append(video_path)
        else:
            for letter in word.upper():
                letter_video = base_dir / f"{letter}.mp4"
                if letter_video.exists():
                    st.session_state.video_queue.append(letter_video)

# Show the videos
if st.session_state.video_queue:
    st.markdown("### 🎞️ Playing Videos")
    for video in st.session_state.video_queue:
        st.video(str(video))
