#  User Feedback Dashboard (Streamlit + MinIO)

This module provides an interactive **Streamlit dashboard** to visualize and inspect user feedback data (audio + transcripts) stored in a **MinIO bucket**. It's part of the larger **StudyBot** project for lecture transcription and QA.

---

##  Dockerized Dashboard

The included `Dockerfile` sets up a lightweight container to run the dashboard:

- **Base:** `python:3.10-slim`
- **Installs:** `ffmpeg`, `streamlit`, `matplotlib`, `plotly`, `pandas`, `minio`, `pydub`
- **Exposes:** Port `8501` for Streamlit UI

To build and run:
```bash
docker build -t Streamlit-dashboard .
docker run -p 8501:8501 -e MINIO_ACCESS_KEY=xxx -e MINIO_SECRET_KEY=xxx Streamlit-dashboard
```

**Requirements**

Docker

MinIO bucket with .wav and .txt files

Set env vars: MINIO_ACCESS_KEY, MINIO_SECRET_KEY

## What dashboard.py Does

Connects to a MinIO bucket (mlflow-artifacts/userfeedback/)

Finds and validates .wav and .txt file pairs


## Displays:

Audio + transcript preview

Word count, audio duration, warnings

Global stats: word count & audio length distributions

Allows users to mark samples for review and download stats



## Access the Dashboard

Once running, open your browser to:
http://localhost:8501
