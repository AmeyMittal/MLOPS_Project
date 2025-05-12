# STUDY BOT - Audio Captioning and Q/A Chatbot

## Group 48
### Value Proposition
Our proposed machine learning system aims to significantly enhance the learning experience for students by integrating ML models into existing EdTech platforms. For eg - 
1. Brightspace (Contains Video lectures)
2. NPTEL (University Learning system in India which contains a plethora of live video classes)

### Target Audience
The primary audience for this system is students—particularly those engaged in online or remote education via EdTech platforms, learning management systems (LMS), and educational apps. 

### Status Quo in Existing Services
Students must watch long, dense lecture videos to find relevant content, making learning inefficient. They often take notes, rewatch segments, or use external tools, leading to wasted time, cognitive overload, and missed information. 

Value Added by the Machine Learning System: Our system lets students skip full lectures and get instant answers via an LLM-powered chatbot.

**Key Benefits**
* Saves Time – Query specific concepts instantly. 
* Focused Learning – Access only relevant topics. 
* Better Retention – Structured, revisitable answers. 
* Inclusive – Supports diverse learning needs. 

### Customer Scale
On high-traffic days like finals at NYU, the Brightspace portal can experience up to 2000 students revisiting lecture content. With an average of 20 chatbot queries per student, this can result in over 40K requests in a single day—highlighting the need for a scalable and responsive system.

### Business Metrics for Evaluation 
* The impact and success of this system will be evaluated based on the following key business metrics: 
* User Adoption Rate: Number of students who actively use the Q&A feature after lecture uploads. 
* Time Saved: Average reduction in time spent per lecture by users who use the feature compared to those who don’t. 
* Engagement Metrics: Increase in student interaction, question frequency, and repeat usage. 
* Customer Retention and Satisfaction: Positive feedback from users and higher platform retention due to enhanced learning experiences.


### Contributors

<!-- Table of contributors and their roles. 
First row: define responsibilities that are shared by the team. 
Then, each row after that is: name of contributor, their role, and in the third column, 
you will link to their contributions. If your project involves multiple repos, you will 
link to their contributions in all repos here. -->

| Name                   | Responsible for             | Link to their commits in this repo                                                                 |
|------------------------|-----------------------------|------------------------------------------------------------------------------------------------------|
| Amratanshu Shrivastava | Model training              | [Commits](https://github.com/AmeyMittal/StudyBot-Audio-Captioning-and-Q-A-chatbot-/commits/main?author=amratanshu) |
| Amey Mittal            | Model serving and inference | [Commits](https://github.com/AmeyMittal/StudyBot-Audio-Captioning-and-Q-A-chatbot-/commits/main?author=ameymittal) |
| Neha Patil             | Data pipeline               | [Commits](https://github.com/AmeyMittal/StudyBot-Audio-Captioning-and-Q-A-chatbot-/commits/main?author=patilneha08) |
| Ruchi Jha              | Continuous X pipeline       | [Commits](https://github.com/AmeyMittal/StudyBot-Audio-Captioning-and-Q-A-chatbot-/commits/main?author=RuchiMJha)   |




### System diagram

![System Diagram](system-diagram.png)

<!-- Overall digram of system. Doesn't need polish, does need to show all the pieces. 
Must include: all the hardware, all the containers/software platforms, all the models, 
all the data. -->

### Summary of outside materials

<!-- In a table, a row for each dataset, foundation model. 
Name of data/model, conditions under which it was created (ideally with links/references), 
conditions under which it may be used. -->

### 📚 Datasets and Models Used
| Item                                                                                                           | How it was Created                                                                                                                                                                                                                                                                                                           | Conditions of Use                                                                                                               |
|---------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| [NPTEL2020 Dataset](https://github.com/AI4Bharat/NPTEL2020-Indian-English-Speech-Dataset/blob/master/README.md) | A Speech-to-Text dataset created by AI4Bharat using lecture recordings from the NPTEL platform. Audio was segmented and manually transcribed. Clips with noise or poor quality were filtered out to ensure high transcription accuracy, representing diverse Indian English accents.                         | Released under a Creative Commons license for **research and educational use**.                                                |
| [Whisper (OpenAI)](https://github.com/openai/whisper)                                                           | A multilingual speech recognition model trained on 680,000 hours of web audio. Handles diverse accents, background noise, and both English and non-English speech using a transformer-based architecture for robust ASR performance.                                                                   | Released under the **MIT License** – free for **commercial and non-commercial** use with modification and distribution rights. |




### Summary of infrastructure requirements

<!-- Itemize all your anticipated requirements: What (`m1.medium` VM, `gpu_mi100`), 
how much/when, justification. Include compute, floating IPs, persistent storage. 
The table below shows an example, it is not a recommendation. -->

| Requirement                       | How many/when                      | Justification                                                                                             |
|-----------------------------------|------------------------------------|-----------------------------------------------------------------------------------------------------------|
| m1.medium VMs                     | 3 for entire project duration     | One for the QA API service, one for Whisper inference, one for managing background tasks like data cleanup and user feedback processing |
| GPU (Compute GigaIO A100)         | Four 6-hour leases                 | Used for training and re-training tasks                                                                   |
| Floating IPs                      | 1 for entire project duration, 1 for sporadic use | One stable IP for the API endpoint, one temporary IP for occasional testing or re-deployment         |
| Block storage                     | 30 GB for persistent storage       | To store audio files, transcripts, processed feedback, and logs across model runs            |
| Object storage                    | 10GB total, expandable as needed   | For storing raw audio (NPTEL dataset), model checkpoints, and backups                                    |


### Detailed design plan

### Training and Re-Training Strategy

File Links ->

Following Commits by Amratanshu: https://github.com/amratanshu

Server provisioning jupyter notebooks -> https://github.com/AmeyMittal/StudyBot-Audio-Captioning-and-Q-A-chatbot-/tree/main/provisioning

For details regarding training pipeline and commands, view this readme -> https://github.com/AmeyMittal/StudyBot-Audio-Captioning-and-Q-A-chatbot-/blob/main/training-readme/training-readme.md

To view training screenshots, view folder here -> https://github.com/AmeyMittal/StudyBot-Audio-Captioning-and-Q-A-chatbot-/tree/main/training-readme

Requirements (pip dependencies for training) -> https://github.com/AmeyMittal/StudyBot-Audio-Captioning-and-Q-A-chatbot-/blob/main/model-training/requirements.txt

Data preparation file -> https://github.com/AmeyMittal/StudyBot-Audio-Captioning-and-Q-A-chatbot-/blob/main/model-training/prepare_nptel_dataset.py

Training Jupyter Notebook -> https://github.com/AmeyMittal/StudyBot-Audio-Captioning-and-Q-A-chatbot-/blob/main/model-training/audio_trancripting%20-%20gpu.ipynb

Training Python executable file -> https://github.com/AmeyMittal/StudyBot-Audio-Captioning-and-Q-A-chatbot-/blob/main/model-training/train_whisper_small.py

Retraining Python executable file -> https://github.com/AmeyMittal/StudyBot-Audio-Captioning-and-Q-A-chatbot-/blob/main/model-training/retraining.py

Docker file to set up mlflow, minio, minio bucket creation, postgres -> https://github.com/AmeyMittal/StudyBot-Audio-Captioning-and-Q-A-chatbot-/blob/main/ansible/k8s/docker-compose-data.yaml


#### Whisper ASR Model - Fine Tuning

- **Initial Training**  
  Fine-tuned Whisper-small ASR(Audio Speech Recognition - Transcription) model on the full [NPTEL2020](https://github.com/AI4Bharat/NPTEL2020-Indian-English-Speech-Dataset/blob/master/README.md) dataset to adapt to Indo-English lecture audio.

- **Re-Training Trigger**  
  Retraining is initiated when the system accumulates more than **100 incorrect transcripts**. Users are prompted to correct these transcripts, and their inputs are used as **new ground truth** for fine-tuning.

- **GPU Resources**  
  Used Compute-GigaIO leases (NVIDIA A100 80 GB) for both training and re-training tasks.

- **Experiment Tracking**  
  All training runs, dataset versions, and fine-tuning iterations are logged using **MLflow** for reproducibility and transparency.


### Experiment Tracking & Training Infrastructure

#### Experiment Tracking

- **MLflow** used for:  
  - Logging hyperparameters  
  - Capturing system metrics  
  - Recording model performance metrics  
  - Storing model artifacts (full deserialized weights in `model.safetensors`), tokenizer & config files, and training arguments  
  - These are all stored in a MinIO bucket called `mlflow-artifacts`

- **MinIO** used for:  
  - Connected to our block storage backend  
  - Bucket `userfeedback` contains user-uploaded WAV files and corrected transcripts (misclassification cases)  
  - This bucket provides new data to the re-training workflow  


### Model serving and monitoring platforms

<!-- Make sure to clarify how you will satisfy the Unit 6 and Unit 7 requirements, 
and which optional "difficulty" points you are attempting. -->

#### Model Serving Strategy

**Strategy**  
Whisper is deployed as containerized FastAPI endpoints, hostel on KVM@TACC.
Flask is used to make the UI/UX
Prometheus & Grafana is used to scrape the UI and generate dashboards for system performance

**Flask** used for:
- Flask app serves a web interface where users can upload .wav audio files.
- It sends the files to a FastAPI backend for transcription using Whisper and displays the generated transcript.
- The app also uploads audio and transcript metadata to MinIO and allows users to flag incorrect outputs and give the correct one.

**FastAPI** used for:
- FastAPI server receives audio files from the Flask frontend for transcription.
- It runs the Whisper model (via CPU) to generate transcripts from the uploaded .wav files.
- The server returns the transcript to Flask and exposes Prometheus-compatible metrics for monitoring.

**MinIO** used for:
- Bucket `production` is made where WAV files are getting stored with 3 tags, transcript, flagged, timestamp
- Bucket `userfeedback` is made where WAV files are getting stored with 2 tags, corrected_transcript, timestamp
- This bucket provides new data to the re-training workflow 

**Prometheus** used for:
- scrapes fastapi server by sending HTTP requests to /metrics 
- And it sends to grafana for analysing the data 

**Grafana** used for:
- Grafana queries Prometheus
- It pulls data from Prometheus using PromQL (Prometheus Query Language)
- Then displays this data in real-time via dashboards and panels.

### Data pipeline

This section incorporates both offline and online data pipelines, persistent storage management, and an interactive data dashboard.

---

###  Offline Data Storage (Object Storage)

- **Object Storage Name:** `object-persist-project48`  
  **Location:** CHI@TACC (Chameleon Cloud)

- **Source Dataset:**  
  [NPTEL Indian English Speech Dataset (AI4Bharat)](https://github.com/AI4Bharat/NPTEL2020-Indian-English-Speech-Dataset)  
  The dataset was originally provided in segmented files: nptel-test.tar.gz.partaa,  partab,  partac


- **Preprocessing Steps:**
1. Concatenated the split archive files
2. Extracted the combined `.tar.gz` file
3. Curated a 10GB subset for faster access
4. Uploaded to Hugging Face for programmatic retrieval:  
    [Hugging Face Dataset](https://huggingface.co/datasets/nehapatil08/nptel-dataset/resolve/main/nptelfinal.zip)

- **ETL Pipeline:**
- Implemented using Docker Compose
- Extracts and unzips the dataset into a shared volume
- Runs `pair_files.py` to ensure `.wav` and `.txt` files are properly paired
- Unpaired or corrupt files are excluded
- Final paired data is uploaded to the object storage

---

###  Persistent Block Storage

- **Block Storage Name:** `block-persist-project48`  
**Location:** KVM@TACC (Chameleon Cloud)

 **Purpose:** Stores critical non-Git tracked artifacts used across the pipeline such as:
- MLflow training artifacts
- MinIO-stored audio feedback
- Evaluation outputs
- Container image layers
- Model binaries and metadata

---

###  Online Data & Stream Simulation

- Real-time user feedback is simulated via `.wav` and `.txt` files uploaded to MinIO.
- These files replicate data that would typically be sent during live model inference.
- Online inference scripts read from MinIO, validate input, and return predictions.

---

###  Interactive Streamlit Dashboard

An interactive dashboard was built with **Streamlit** to visualize feedback data stored in MinIO.

- **Dashboard Source:** `dashboard.py`
- **MinIO Bucket Path:** `mlflow-artifacts/userfeedback/`

#### Key Features:
- Connects to MinIO and lists feedback files
- Validates and pairs `.wav` audio and `.txt` transcripts

##### Displays:
- Audio preview and transcript
- Word count, transcript warnings
- Audio duration and anomaly alerts

##### Provides global insights:
- Word count distributions
- Audio length distributions

##### Includes tools to:
- Mark samples for review
- Export transcript statistics as CSV

---

This pipeline ensures robust offline storage, consistent data validation, and real-time readiness for ML model feedback loops — along with a user-friendly data monitoring dashboard.


**File links by Neha Patil**


Commits - [https://github.com/AmeyMittal/StudyBot-Audio-Captioning-and-Q-A-chatbot-/commits/main/?author=patilneha08]


Streamlit README- [https://github.com/AmeyMittal/StudyBot-Audio-Captioning-and-Q-A-chatbot-/blob/main/Streamlit/README.md]


py file to setup Streamlit dashboard- [https://github.com/AmeyMittal/StudyBot-Audio-Captioning-and-Q-A-chatbot-/blob/main/Streamlit/dashboard.py]


Docker file for Streamlit - [https://github.com/AmeyMittal/StudyBot-Audio-Captioning-and-Q-A-chatbot-/blob/main/Streamlit/Dockerfile]


yaml file for ETL of nptel dataset - [https://github.com/AmeyMittal/StudyBot-Audio-Captioning-and-Q-A-chatbot-/blob/main/data-persist-chi/docker/docker-composefinal-etl.yaml]


README for ETL on how to run docker compose - [https://github.com/AmeyMittal/StudyBot-Audio-Captioning-and-Q-A-chatbot-/blob/main/data-persist-chi/docker/README.md]


py file to ensure wav and txt files are in pairs- [https://github.com/AmeyMittal/StudyBot-Audio-Captioning-and-Q-A-chatbot-/blob/main/data-persist-chi/docker/pair_files.py]


README for running object storage and persistent block storage files for creation - [https://github.com/AmeyMittal/StudyBot-Audio-Captioning-and-Q-A-chatbot-/blob/main/infrastructure/README.md]


py file for persistent block storage - [https://github.com/AmeyMittal/StudyBot-Audio-Captioning-and-Q-A-chatbot-/blob/main/infrastructure/provision_block_storage.py]


sh file for object storage creation - [https://github.com/AmeyMittal/StudyBot-Audio-Captioning-and-Q-A-chatbot-/blob/main/infrastructure/provision_object_storage.sh]


### Continuous X

- Installed Terraform v1.10.5 manually in the Chameleon Jupyter environment.
- Set the system PATH to include the local Terraform binary.
- Copied clouds.yaml to /work/studybot-iac/tf/kvm/clouds.yaml.
- Navigated to the Terraform directory and initialized Terraform (terraform init).
- Set Terraform environment variables TF_VAR_suffix=project48 and TF_VAR_key=id_rsa_chameleon2.
- Ran terraform validate, terraform plan, and terraform apply -auto-approve to provision infrastructure.
- Installed ansible-core==2.16.9 and ansible==9.8.0 using pip.
- Set environment variables for Ansible and Python user base.
- Copied ansible.cfg to the working directory.
- Ran ansible -i inventory.yml all -m ping to test node connectivity.
- Installed Kubespray dependencies using requirements.txt.
- Ran pre_k8s_configure.yml Ansible playbook to prepare nodes.
- Used Kubespray to deploy Kubernetes via cluster.yml.
- Ran post_k8s_configure.yml to finalize Kubernetes setup.
- Ran argocd_add_platform.yml to install and configure ArgoCD on the cluster.
- Ran workflow_build_init.yml to set up Argo Workflows.









<!-- #### Infrastructure-as-Code (IaC)

**Strategy**  
All infrastructure components (VMs, GPUs, networking) are provisioned using `python-chi` scripts. Service setup and configuration are automated using **Ansible** and **Helm**.

**Structure**  
- Git repository is organized with:
  - `provisioning/` – Python-CHI scripts for resource creation
  - `service-config/` – Ansible roles and Helm charts for deployment

**Justification**  
- Prevents manual setup errors
- Ensures repeatability and reproducibility
- Supports versioning and auditability

**Infrastructure Resources**  
- 3 `m1.medium` VMs
- 1 persistent floating IP
- GPU blocks (MI100, A100) scheduled programmatically

#### Cloud-Native Architecture

**Strategy**  
All services are containerized (Whisper inference, RAG chatbot, retraining monitor, background tasks) and deployed as microservices. Services communicate via REST APIs.

**Deployment**  
- Each service runs in a separate **Kubernetes pod**
- Helm used for pod and service configuration

**Justification**  
- Enables modular, isolated, and scalable deployments
- Eases service updates and monitoring

**Resources**  
- 4 Dockerized services, deployed one per VM

---

#### CI/CD and Continuous Training

**Strategy**  
A hybrid **GitHub Actions + Argo Workflows** pipeline retrains Whisper when the system detects over 100 bad transcripts.

**Pipeline Stages**  
`trigger → train → evaluate → test → package → deploy`

**Justification**  
- Automates the retraining process
- Ensures consistent, testable, and production-ready updates
- Reduces manual intervention and turnaround time

**Metrics**  
- Retraining triggered after 100+ transcript errors
- 2 Retraining blocks/week allocated on `MI100` GPUs

 -->
