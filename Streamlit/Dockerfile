# Dockerfile
FROM python:3.10-slim

# Install system dependencies for audio processing and plotting
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

# Set working directory
WORKDIR /app

# Copy dashboard script
COPY dashboard.py .

# Install Python dependencies
RUN pip install --no-cache-dir streamlit pandas matplotlib plotly minio pydub

# Expose the Streamlit port
EXPOSE 8501

# Run the Streamlit dashboard
CMD ["streamlit", "run", "dashboard.py", "--server.address=0.0.0.0", "--server.port=8501"]
