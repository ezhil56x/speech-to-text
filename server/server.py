from fastapi import FastAPI, UploadFile
from faster_whisper import WhisperModel

model = WhisperModel("base.en", compute_type="int8")

app = FastAPI()

@app.post("/transcribe")
async def transcribe(file: UploadFile):
    audio_path = f"/tmp/{file.filename}"
    with open(audio_path, "wb") as f:
        f.write(await file.read())

    segments, _ = model.transcribe(audio_path)
    result = " ".join([segment.text for segment in segments])
    return {"text": result}
