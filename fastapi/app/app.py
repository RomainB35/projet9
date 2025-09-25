from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from faster_whisper import WhisperModel
import shutil
import os
import uuid

app = FastAPI(title="ASR Whisper API")

# Charger le modèle une fois au démarrage (modèle CTranslate2 local)
MODEL_PATH = "/app/models/whisper-large-v3-french-distil-dec16-ct2/ctranslate2"
model = WhisperModel(MODEL_PATH, device="cpu", compute_type="int8")

class Segment(BaseModel):
    start: float
    end: float
    text: str

class Transcription(BaseModel):
    language_detected: str
    segments: list[Segment]

@app.post("/transcribe", response_model=Transcription)
async def transcribe(file: UploadFile = File(...)):
    # Vérification plus souple du format audio
    filename = file.filename.lower()
    if not (filename.endswith(".wav") or filename.endswith(".mp3")):
        raise HTTPException(status_code=400, detail="Format audio non supporté (wav ou mp3 uniquement).")

    # Sauvegarder temporairement le fichier
    temp_filename = f"/tmp/{uuid.uuid4().hex}_{file.filename}"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Transcrire
    segments, info = model.transcribe(
        temp_filename,
        beam_size=5,
        language="fr",
        condition_on_previous_text=False
    )

    # Supprimer le fichier temporaire
    os.remove(temp_filename)

    # Construire la réponse
    result = {
        "language_detected": info.language,
        "segments": [{"start": s.start, "end": s.end, "text": s.text} for s in segments]
    }

    return result

