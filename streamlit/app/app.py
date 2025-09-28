import streamlit as st
import requests
import json
from pathlib import Path
from io import BytesIO
from audiorecorder import audiorecorder

FASTAPI_URL = "http://fastapi:10300/transcribe"

# Charger transcriptions CommonVoice
with open("samples_commonvoice21/transcripts.json", "r", encoding="utf-8") as f:
    transcripts_commonvoice = json.load(f)

# Charger transcriptions VoxPopuli
with open("samples_voxpopuli/transcripts.json", "r", encoding="utf-8") as f:
    transcripts_voxpopuli = json.load(f)

st.title("Démo transcription audio FR")

st.sidebar.header("Modes de test")
mode = st.sidebar.radio(
    "Choisir une source audio",
    ["Samples VoxPopuli", "Samples CommonVoice21FR", "Upload fichier", "Microphone"]
)

# ===================== Mode 1 : VoxPopuli Samples =====================
if mode == "Samples VoxPopuli":
    sample_files = list(Path("samples_voxpopuli").glob("*.wav"))
    choice = st.selectbox("Choisir un sample", [f.name for f in sample_files])
    st.audio(str(Path("samples_voxpopuli") / choice), format="audio/wav")

    if st.button("Transcrire ce sample VoxPopuli"):
        with open(Path("samples_voxpopuli") / choice, "rb") as f:
            resp = requests.post(FASTAPI_URL, files={"file": f})
        if resp.status_code == 200:
            result = resp.json()
            st.subheader("Transcription prédite")
            for seg in result["segments"]:
                st.write(f"[{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['text']}")
            st.subheader("Transcription de référence")
            st.write(transcripts_voxpopuli.get(choice, "Pas de référence disponible"))
        else:
            st.error(f"Erreur API: {resp.text}")

# ===================== Mode 2 : CommonVoiceFR Samples =====================
elif mode == "Samples CommonVoice21FR":
    sample_files = list(Path("samples_commonvoice21").glob("*.mp3"))
    choice = st.selectbox("Choisir un sample", [f.name for f in sample_files])
    st.audio(str(Path("samples_commonvoice21") / choice), format="audio/mp3")

    if st.button("Transcrire ce sample"):
        with open(Path("samples_commonvoice21") / choice, "rb") as f:
            resp = requests.post(FASTAPI_URL, files={"file": f})
        if resp.status_code == 200:
            result = resp.json()
            st.subheader("Transcription prédite")
            for seg in result["segments"]:
                st.write(f"[{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['text']}")
            st.subheader("Transcription de référence")
            st.write(transcripts_commonvoice.get(choice, "Pas de référence disponible"))
        else:
            st.error(f"Erreur API: {resp.text}")


# ===================== Mode 3 : Upload fichier =====================
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

# ===================== Mode 4 : Microphone =====================
elif mode == "Microphone":
    st.write("Appuie sur **Start** pour enregistrer, parle, puis **Stop**")

    audio = audiorecorder("Start", "Stop")

    if len(audio) > 0:
        buf = BytesIO()
        audio.export(buf, format="wav")
        buf.seek(0)

        st.audio(buf, format="audio/wav")

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

