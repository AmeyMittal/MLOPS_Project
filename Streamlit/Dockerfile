# Dockerfile
FROM python:3.10-slim

# Install system dependencies for audio processing
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

# Set work directory
WORKDIR /app

# Copy dashboard code
COPY dashboard.py .

# Install Python dependencies
RUN pip install --no-cache-dir streamlit pandas matplotlib minio pydub

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "dashboard.py", "--server.address=0.0.0.0", "--server.port=8501"]
