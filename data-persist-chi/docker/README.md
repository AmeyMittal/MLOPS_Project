# ETL Pipeline for NPTEL Dataset 

This part of the **StudyBot** project contains an ETL pipeline specifically for processing the **NPTEL lecture dataset**.

Originally, the dataset was **120GB** in size and provided in segmented files:  
`nptel-test.tar.gz.partaa`, `partab`, and `partac`.  
After concatenating and extracting the full archive, a **10GB subset** was curated and uploaded to Hugging Face for easier and faster downstream access.

---

##  Dataset Source

**Original Dataset:** [https://github.com/AI4Bharat/NPTEL2020-Indian-English-Speech-Dataset]

**Hugging Face Link:** [https://huggingface.co/datasets/nehapatil08/nptel-dataset/resolve/main/nptelfinal.zip)

**Structure:**

nptelfinal/

├── wav/ # Audio files

└── txt/ # Transcriptions

##  What Does This Module Do?

The `docker-composefinal-etl.yaml` file in this folder defines a **3-step ETL process**:

1. **Extract**  
   Downloads and extracts the `nptelfinal.zip` dataset from Hugging Face into a shared Docker volume (`audio_data`).

2. **Transform**  
   Pairs `.wav` and `.txt` files based on filename using the `pair_files.py` script and stores the matched pairs in a new `paired/` directory.

3. **Load**  
   Uploads the `paired/` directory to a the object store object-persist-project48 using `rclone`.

   Run the ETL Pipeline

> Prerequisites: Docker, Docker Compose, and rclone installed

### Step 1: Extract
```bash
docker compose -f ~/StudyBot-Audio-Captioning-and-Q-A-chatbot-/data-persist-chi/docker/docker-composefinal-etl.yaml run extract-data
```

### Step 2: Transform
```bash
docker compose -f ~/StudyBot-Audio-Captioning-and-Q-A-chatbot-/data-persist-chi/docker/docker-composefinal-etl.yaml run transform-data
```

### Step 3: Load
```bash
export RCLONE_CONTAINER=object-persist-project48
docker compose -f ~/StudyBot-Audio-Captioning-and-Q-A-chatbot-/data-persist-chi/docker/docker-composefinal-etl.yaml run load-data
```

## Validation

### UI:

Check that the paired/ folder appears in the object store 

### CLI:

```bash
rclone ls chi_tacc:object-persist-project48
```

You should see .wav and .txt files with matching names.


## What pair_files.py Does

Scans wav/ and txt/ inside nptelfinal/

Finds files with matching names (e.g., lecture1.wav & lecture1.txt)

Copies matched pairs to paired/

Warns if any unmatched files are found

Prints count of successfully paired files
