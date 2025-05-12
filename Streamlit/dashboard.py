# dashboard.py
import streamlit as st
from minio import Minio
from io import BytesIO
import pandas as pd
import os
import matplotlib.pyplot as plt
import plotly.express as px
from pydub import AudioSegment

# MinIO config
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "129.114.26.114:9000")
ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
BUCKET_NAME = "mlflow-artifacts"
PREFIX = "userfeedback/"

st.set_page_config(page_title="User Feedback Dashboard", layout="wide")
st.title("\U0001F4CA Interactive User Feedback Data Quality Dashboard")

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
            response = client.get_object(BUCKET_NAME, obj.object_name)
            transcript_data[base] = response.read().decode("utf-8")

    paired = wav_files & txt_files
    only_wav = wav_files - txt_files
    only_txt = txt_files - wav_files

    # Compute durations for all paired files
    durations = []
    for name in paired:
        try:
            audio_obj = client.get_object(BUCKET_NAME, f"{PREFIX}{name}.wav")
            audio_bytes = audio_obj.read()
            audio = AudioSegment.from_file(BytesIO(audio_bytes), format="wav")
            duration_sec = round(len(audio) / 1000.0, 2)
            durations.append(duration_sec)
        except Exception as e:
            st.warning(f"Could not process {name}.wav: {e}")

    st.subheader("Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total WAV Files", len(wav_files))
    col2.metric("Total TXT Files", len(txt_files))
    col3.metric("Paired Files", len(paired))

    if only_wav:
        st.warning(f"Unpaired WAV files: {len(only_wav)}")
        st.write(sorted(list(only_wav)))
    if only_txt:
        st.warning(f"Unpaired TXT files: {len(only_txt)}")
        st.write(sorted(list(only_txt)))

    st.divider()

    if paired:
        st.subheader("\U0001F50D Inspect Individual Files")
        selected_file = st.selectbox("Choose a paired file:", sorted(paired))

        if selected_file:
            # Show audio
            audio_obj = client.get_object(BUCKET_NAME, f"{PREFIX}{selected_file}.wav")
            audio_bytes = audio_obj.read()
            st.audio(audio_bytes, format="audio/wav")

            # Transcript
            text = transcript_data.get(selected_file, "")
            st.text_area("Transcript", value=text, height=150)

            # Word count and warnings
            word_count = len(text.split())
            st.write(f"Word Count: {word_count}")
            if word_count < 3:
                st.warning("⚠️ Very short transcript")

            # Duration
            audio = AudioSegment.from_file(BytesIO(audio_bytes), format="wav")
            duration_sec = round(len(audio) / 1000.0, 2)
            st.write(f"Duration: {duration_sec} seconds")
            if duration_sec < 1:
                st.error("❗ Very short audio")
            elif duration_sec > 30:
                st.warning("⚠️ Unusually long audio")

            st.checkbox("Mark for Review")

        # Global visualizations
        st.divider()
        st.subheader("\U0001F4C8 Global Data Insights")

        lengths = {k: len(v.split()) for k, v in transcript_data.items()}
        df_len = pd.Series(lengths).rename("Words")

        colA, colB = st.columns(2)

        with colA:
            st.markdown("**Transcript Word Count Distribution**")
            fig = px.histogram(df_len, nbins=20)
            st.plotly_chart(fig)

        with colB:
            if durations:
                st.markdown("**Audio Duration Distribution**")
                fig2 = px.histogram(durations, nbins=20, labels={'value': 'Duration (s)'})
                st.plotly_chart(fig2)

        st.download_button("Download Transcript Stats", data=df_len.to_csv(), file_name="transcript_lengths.csv")

except Exception as e:
    st.error(f"\u274C Error loading dashboard: {e}")

