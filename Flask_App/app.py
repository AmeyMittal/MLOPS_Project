import os
import uuid
import requests
import boto3
from flask import Flask, request, render_template, send_from_directory
from werkzeug.utils import secure_filename
from mimetypes import guess_type
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=2)

# Authenticate with MinIO
s3 = boto3.client(
    's3',
    endpoint_url=os.environ['MINIO_URL'],
    aws_access_key_id=os.environ['MINIO_USER'],
    aws_secret_access_key=os.environ['MINIO_PASSWORD'],
    region_name='us-east-1'
)

app = Flask(__name__)
os.makedirs(os.path.join(app.instance_path, 'uploads'), exist_ok=True)

FASTAPI_SERVER_URL = os.environ['FASTAPI_SERVER_URL']

# S3 Key helpers
def get_object_key(prediction_id):
    return f"transcripts/audio_{prediction_id}.wav"

def get_feedback_key(prediction_id):
    return f"user_feedback/audio_{prediction_id}.wav"

# Upload transcript to 'production' bucket
def upload_production_bucket(audio_path, transcript, prediction_id):
    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    content_type = guess_type(audio_path)[0] or 'application/octet-stream'
    s3_key = get_object_key(prediction_id)
    bucket_name = "production"

    with open(audio_path, 'rb') as f:
        s3.upload_fileobj(f, bucket_name, s3_key, ExtraArgs={'ContentType': content_type})

    s3.put_object_tagging(
        Bucket=bucket_name,
        Key=s3_key,
        Tagging={
            'TagSet': [
                {'Key': 'transcript', 'Value': transcript[:250]},
                {'Key': 'timestamp', 'Value': timestamp}
            ]
        }
    )

# Upload correction to 'userfeedback' bucket
def upload_user_feedback(audio_path, correction_text, prediction_id):
    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    s3_key = get_feedback_key(prediction_id)
    bucket_name = "userfeedback"

    with open(audio_path, 'rb') as f:
        s3.upload_fileobj(f, bucket_name, s3_key, ExtraArgs={'ContentType': 'audio/wav'})

    s3.put_object_tagging(
        Bucket=bucket_name,
        Key=s3_key,
        Tagging={
            'TagSet': [
                {'Key': 'corrected_transcript', 'Value': correction_text[:250]},
                {'Key': 'timestamp', 'Value': timestamp}
            ]
        }
    )

# FastAPI inference
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
        filename = secure_filename(f.filename)
        save_path = os.path.join(app.instance_path, 'uploads', filename)
        f.save(save_path)
        prediction_id = str(uuid.uuid4())

        transcript = request_fastapi(save_path)
        if transcript:
            s3_key = get_object_key(prediction_id)
            executor.submit(upload_production_bucket, save_path, transcript, prediction_id)

            audio_url = f"/uploads/{filename}"
            flag_icon = f'''
                <form method="POST" action="/flag/{s3_key}" style="display:inline">
                    <button type="submit" class="btn btn-outline-warning btn-sm">🚩</button>
                </form>'''

            # Feedback box
            feedback_form = f'''
                <form method="POST" action="/feedback/{prediction_id}" style="margin-top:15px">
                    <label for="correction">Submit corrected transcript (optional):</label><br>
                    <textarea name="correction" rows="3" cols="60" placeholder="Enter corrected transcript here..."></textarea><br>
                    <input type="hidden" name="file" value="{filename}">
                    <button type="submit" class="btn btn-success btn-sm">Submit Correction</button>
                </form>'''

            return f'''
                <h5>Transcript:</h5><pre>{transcript}</pre>
                <audio controls>
                    <source src="{audio_url}" type="audio/wav">
                </audio><br>
                {flag_icon}
                {feedback_form}
            '''

    return '<p style="color:red;">Failed to transcribe.</p>'

@app.route('/feedback/<prediction_id>', methods=['POST'])
def feedback(prediction_id):
    correction_text = request.form.get("correction", "").strip()
    filename = request.form.get("file")
    audio_path = os.path.join(app.instance_path, 'uploads', filename)
    if correction_text and os.path.exists(audio_path):
        executor.submit(upload_user_feedback, audio_path, correction_text, prediction_id)
    return '<p style="color:green;">Thank you for your correction!</p><a href="/">Go back</a>'

@app.route('/flag/<path:key>', methods=['POST'])
def flag_object(key):
    bucket = "production"
    current_tags = s3.get_object_tagging(Bucket=bucket, Key=key)['TagSet']
    tags = {t['Key']: t['Value'] for t in current_tags}
    if "flagged" not in tags:
        tags["flagged"] = "true"
        tag_set = [{'Key': k, 'Value': v} for k, v in tags.items()]
        s3.put_object_tagging(Bucket=bucket, Key=key, Tagging={'TagSet': tag_set})
    return '', 204

# Serve uploaded audio
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.join(app.instance_path, 'uploads'), filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
