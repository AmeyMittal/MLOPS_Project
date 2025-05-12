# dashboard.py
import streamlit as st
from minio import Minio
from io import BytesIO
import pandas as pd
import os
import matplotlib.pyplot as plt
from pydub import AudioSegment

# MinIO config
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "129.114.26.114:9000")
ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "project48")
SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "project48")
BUCKET_NAME = "mlflow-artifacts"
PREFIX = "userfeedback/"

st.title("User Feedback Data Quality Dashboard")

try:
    client = Minio(
        MINIO_ENDPOINT,
        access_key=ACCESS_KEY,
        secret_key=SECRET_KEY,
        secure=False
    )

    with st.spinner("Fetching objects from MinIO..."):
        objects = list(client.list_objects(BUCKET_NAME, prefix=PREFIX, recursive=True))

    wav_files = set()
    txt_files = set()
    transcript_data = {}

    for obj in objects:
        filename = obj.object_name.replace(PREFIX, "")
        base, ext = os.path.splitext(filename)
        if ext == ".wav":
            wav_files.add(base)
        elif ext == ".txt":
            txt_files.add(base)
            # Read the text content
            response = client.get_object(BUCKET_NAME, obj.object_name)
            transcript_data[base] = response.read().decode("utf-8")

    paired = wav_files & txt_files
    only_wav = wav_files - txt_files
    only_txt = txt_files - wav_files

    st.subheader("Overview")
    st.write(f"Total WAV files: {len(wav_files)}")
    st.write(f"Total TXT files: {len(txt_files)}")
    st.write(f"\u2705 Paired files: {len(paired)}")
    st.write(f"\u274C Unpaired WAV files: {len(only_wav)}")
    st.write(f"\u274C Unpaired TXT files: {len(only_txt)}")

    if only_wav:
        st.subheader("Unpaired WAV files")
        st.write(sorted(list(only_wav)))
    if only_txt:
        st.subheader("Unpaired TXT files")
        st.write(sorted(list(only_txt)))

    # Transcript length analysis
    if transcript_data:
        st.subheader("Transcript Length Distribution (in words)")
        lengths = {k: len(v.split()) for k, v in transcript_data.items()}
        df_len = pd.Series(lengths).sort_values()
        fig, ax = plt.subplots()
        df_len.plot(kind='hist', bins=20, ax=ax)
        st.pyplot(fig)

    # Audio duration analysis
    durations = []
    for name in paired:
        try:
            obj = client.get_object(BUCKET_NAME, f"{PREFIX}{name}.wav")
            audio = AudioSegment.from_file(BytesIO(obj.read()), format="wav")
            durations.append(len(audio) / 1000.0)
        except Exception as e:
            st.warning(f"Failed to read {name}.wav: {e}")

    if durations:
        st.subheader("Audio Duration Distribution (in seconds)")
        fig2, ax2 = plt.subplots()
        pd.Series(durations).plot(kind='hist', bins=20, ax=ax2)
        st.pyplot(fig2)

except Exception as e:
    st.error(f"\u274C Error loading dashboard: {e}")
