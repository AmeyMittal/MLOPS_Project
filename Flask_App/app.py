import os
import requests
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename

app = Flask(__name__)
os.makedirs(os.path.join(app.instance_path, 'uploads'), exist_ok=True)

FASTAPI_SERVER_URL = os.environ['FASTAPI_SERVER_URL']

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
    transcript = None
    if request.method == 'POST':
        f = request.files['file']
        save_path = os.path.join(app.instance_path, 'uploads', secure_filename(f.filename))
        f.save(save_path)
        transcript = request_fastapi(save_path)
        if transcript:
            return f'<h5>Transcript:</h5><pre>{transcript}</pre>'
    return '<p style="color:red;">Failed to transcribe.</p>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
