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
Both Whisper and LLaMA are deployed as containerized **FastAPI** endpoints, each hosted on separate VMs with GPU support.

- **Whisper Endpoint**: Supports real-time transcription (ASR) with online inference.
- **LLaMA Endpoint**: Powers context-aware question answering using a RAG pipeline.

**Deployment Diagram**  
Two containerized services:
- `Whisper API`: Deployed on a GPU-enabled VM
- `RAG Chatbot API`: Deployed on a separate GPU-enabled VM with high VRAM

**Justification**  
- **Whisper** must maintain inference latency under 2 seconds for ~30-second audio clips to be usable in real-time scenarios.
- **LLaMA** requires over 40 GB of GPU VRAM to support at least three concurrent users interacting with lecture-based content.

**Optimizations**  
- **Whisper**: Uses FP16 precision and **ONNX Runtime** to reduce latency and resource usage.
- **RAG System**: Utilizes **4-bit quantized** version of LLaMA for memory efficiency.

**Additional Evaluation**  
Whisper was benchmarked across CPU, GPU, and lightweight variants to assess the cost-performance tradeoff and optimize deployment choices.

### Data pipeline

<!-- Make sure to clarify how you will satisfy the Unit 8 requirements,  and which 
optional "difficulty" points you are attempting. -->

### Continuous X

<!-- Make sure to clarify how you will satisfy the Unit 3 requirements,  and which 
optional "difficulty" points you are attempting. -->









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
