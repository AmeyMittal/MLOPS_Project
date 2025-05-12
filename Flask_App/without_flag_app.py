import os
import uuid
import requests
import boto3
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from mimetypes import guess_type
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=2)

# Authenticate with MinIO
s3 = boto3.client(
    's3',
    endpoint_url=os.environ['MINIO_URL'],  # e.g. http://minio:9000
    aws_access_key_id=os.environ['MINIO_USER'],
    aws_secret_access_key=os.environ['MINIO_PASSWORD'],
    region_name='us-east-1'  # required for boto3 but unused by MinIO
)

app = Flask(__name__)
os.makedirs(os.path.join(app.instance_path, 'uploads'), exist_ok=True)

FASTAPI_SERVER_URL = os.environ['FASTAPI_SERVER_URL']

# Upload audio file + transcript metadata to MinIO
def upload_production_bucket(audio_path, transcript, prediction_id):
    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    content_type = guess_type(audio_path)[0] or 'application/octet-stream'
    s3_key = f"transcripts/audio_{prediction_id}.mp3"
    bucket_name = "production"

    with open(audio_path, 'rb') as f:
        s3.upload_fileobj(f, bucket_name, s3_key, ExtraArgs={'ContentType': content_type})

    s3.put_object_tagging(
        Bucket=bucket_name,
        Key=s3_key,
        Tagging={
            'TagSet': [
                {'Key': 'transcript', 'Value': transcript[:250]},  # S3 tag values have length limits
                {'Key': 'timestamp', 'Value': timestamp}
            ]
        }
    )

def request_fastapi(audio_path):
    try:
        with open(audio_path, 'rb') as f:
            files = {'file': (os.path.basename(audio_path), f, 'audio/mpeg')}
            response = requests.post(f"{FASTAPI_SERVER_URL}/transcribe", files=files)
            response.raise_for_status()
            result = response.json()
            return result.get("transcript")
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        f = request.files['file']
        save_path = os.path.join(app.instance_path, 'uploads', secure_filename(f.filename))
        f.save(save_path)
        prediction_id = str(uuid.uuid4())

        transcript = request_fastapi(save_path)
        if transcript:
            executor.submit(upload_production_bucket, save_path, transcript, prediction_id)
            return f'<h5>Transcript:</h5><pre>{transcript}</pre>'
    return '<p style="color:red;">Failed to transcribe.</p>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
