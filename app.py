from fastapi import FastAPI, UploadFile, File
import whisper
import tempfile
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="Whisper Transcription API")

# Load Whisper model (small)
model = whisper.load_model("small")

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        result = model.transcribe(tmp_path)
        return {"transcript": result["text"]}
    except Exception as e:
        return {"error": str(e)}

Instrumentator().instrument(app).expose(app)
