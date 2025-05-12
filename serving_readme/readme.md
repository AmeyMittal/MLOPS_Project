SSH into http://129.114.26.83/

Then create the 3 docker files:
- docker-compose-production-new.yaml
- docker-compose-labelstudio.yaml
- docker-compose-prometheus.yaml

Ports on which each service is running:

- fastapi_server : 8000
- grafana : 3000
- prometheus : 9090
- flask : 5000
- miniIo: 9001
- Label Studio: 8080

**System Strategy** 
This system is designed to simulate a real-world machine learning feedback loop for audio transcription. It combines model inference, user interaction, monitoring, feedback collection, and re-training orchestration using containerized microservices. The workflow is deployed on a KVM@TACC virtual machine using Docker Compose.

**Whisper Model Deployment**
- The Whisper model (small) is deployed using FastAPI, wrapped in a Docker container.
- The server accepts .wav audio files from a frontend and returns real-time transcriptions.
- Inference is performed on CPU, suitable for lightweight virtualized environments like KVM@TACC.

**Flask Application (UI/UX Layer)**
- Flask provides a lightweight web interface where users can:
- Upload .wav files for transcription.
- View the returned transcript on the same page.
- Play the uploaded audio to verify transcription accuracy.
- Submit corrected transcripts if the model output is wrong.
- Click a “🚩 Flag” icon to mark incorrect predictions.
- Flask also handles:
- Saving uploaded files to a temporary local directory.
- Sending the files to the FastAPI backend.
- Asynchronously uploading audio and transcript metadata to MinIO for persistence.

**FastAPI Backend (Model Server)**
FastAPI hosts the Whisper inference model and provides a /transcribe endpoint.
It:
- Accepts multipart .wav files.
- Runs the Whisper model to generate a transcript.
- Returns the transcript in JSON format.
- Exposes Prometheus-compatible /metrics to track:
- Inference time
- Number of requests
- Success/failure status codes

**MinIO (Object Store for Audio & Metadata)**
- Acts as an S3-compatible storage layer.
- Two buckets are configured:

**1.production**: stores original .wav uploads from Flask, tagged with:
- transcript: Whisper-generated transcription
- timestamp: Upload time
- flagged: Set to "true" if the user flags an error

**2.userfeedback**: stores .wav files + corrected user transcripts, tagged with:
- corrected_transcript: manually submitted transcription
- timestamp: Time of feedback submission
- This structure supports both traceability and retrieval for continuous re-training.


**Prometheus (Monitoring & Metrics Scraper)**
Prometheus is configured to scrape FastAPI's /metrics endpoint periodically.
Captures metrics like:
- Inference request latency
- Request success/failure count
- Uptime and throughput

**Grafana (Dashboard Visualization)**
Grafana pulls data from Prometheus using PromQL queries.
Provides live dashboards to observe:
- Current inference load
- Error rates
- Transcription latency
- Overall system health
Enables to monitor system bottlenecks and debug deployment performance in real time.

**Label Studio (Human-in-the-Loop Feedback Loop)**
Label Studio serves as the annotation layer in the retraining pipeline.
It:
- Connects to the production and userfeedback buckets in MinIO.
- Displays .wav files to human annotators via a web interface.
- Allows users to listen to audio and submit corrected transcripts for poorly transcribed data.
- Stores corrected labels in userfeedback, which can be exported for retraining Whisper or other models.
- Label Studio closes the loop, making the system interactive and self-improving over time.

