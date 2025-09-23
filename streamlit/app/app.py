import streamlit as st
import requests
import json
from pathlib import Path
from io import BytesIO
import soundfile as sf
from audiorecorder import audiorecorder  # fourni par streamlit-audiorecorder

FASTAPI_URL = "http://fastapi:10300/transcribe"

# Charger transcriptions de référence
with open("transcripts.json", "r", encoding="utf-8") as f:
    transcripts = json.load(f)

st.title("Démo Voice-to-Text (FastAPI - Whisper + Streamlit)")

st.sidebar.header("Modes de test")
mode = st.sidebar.radio(
    "Choisir une source audio", ["Samples CommonVoiceFR", "Upload fichier", "Microphone"]
)

# ===================== Mode 1 : CommonVoiceFR Samples =====================
if mode == "Samples CommonVoiceFR":
    sample_files = list(Path("samples").glob("*.mp3"))
    choice = st.selectbox("Choisir un sample", [f.name for f in sample_files])
    st.audio(str(Path("samples") / choice), format="audio/mp3")

    if st.button("Transcrire ce sample"):
        with open(Path("samples") / choice, "rb") as f:
            resp = requests.post(FASTAPI_URL, files={"file": f})
        if resp.status_code == 200:
            result = resp.json()
            st.subheader("Transcription prédite")
            for seg in result["segments"]:
                st.write(f"[{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['text']}")
            st.subheader("Transcription de référence")
            st.write(transcripts.get(choice, "Pas de référence disponible"))
        else:
            st.error(f"Erreur API: {resp.text}")

# ===================== Mode 2 : Upload fichier =====================
elif mode == "Upload fichier":
    uploaded_file = st.file_uploader("Choisir un fichier audio (mp3/wav)", type=["mp3", "wav"])
    if uploaded_file and st.button("Transcrire fichier uploadé"):
        resp = requests.post(FASTAPI_URL, files={"file": uploaded_file})
        if resp.status_code == 200:
            result = resp.json()
            st.subheader("Transcription prédite")
            for seg in result["segments"]:
                st.write(f"[{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['text']}")
        else:
            st.error(f"Erreur API: {resp.text}")

# ===================== Mode 3 : Microphone =====================
elif mode == "Microphone":
    st.write("Appuie sur **Start** pour enregistrer, parle, puis **Stop**")

    # Widget start/stop
    audio = audiorecorder("Start", "Stop")

    if len(audio) > 0:
        # Exporter en WAV vers un buffer mémoire
        buf = BytesIO()
        audio.export(buf, format="wav")
        buf.seek(0)

        # Lecture locale
        st.audio(buf, format="audio/wav")

        # Envoi au FastAPI
        resp = requests.post(
            FASTAPI_URL,
            files={"file": ("record.wav", buf, "audio/wav")}
        )

        if resp.status_code == 200:
            result = resp.json()
            text = " ".join([seg["text"] for seg in result["segments"]])
            st.subheader("Transcription")
            st.write(text)
        else:
            st.error(f"Erreur API: {resp.text}")

