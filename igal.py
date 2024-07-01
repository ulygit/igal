#!python

from flask import Flask, request, jsonify, send_from_directory, render_template
import os
import yaml
from werkzeug.utils import secure_filename

def load_config():
    config = {
        'UPLOADED_PHOTOS_DEST': 'uploads',
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16 MB
        'HOST': '127.0.0.1',
        'PORT': 8080
    }
    
    if os.path.exists('config.yaml'):
        with open('config.yaml', 'r') as f:
            yaml_config = yaml.safe_load(f)
            config.update(yaml_config)
    
    return config

config = load_config()

app = Flask(__name__, static_folder='static')
app.config['UPLOADED_PHOTOS_DEST'] = config['UPLOADED_PHOTOS_DEST']
app.config['MAX_CONTENT_LENGTH'] = config['MAX_CONTENT_LENGTH']

def get_version_id():
    vcid_path = os.path.join(os.path.dirname(__file__), 'vcid')
    if os.path.exists(vcid_path):
        with open(vcid_path, 'r') as f:
            return f.read().strip()
    return 'Unknown'

@app.route('/')
def index():
    version_id = get_version_id()
    return render_template('index.html', version_id=version_id)

@app.route('/check_gallery/<gallery>')
def check_gallery(gallery):
    upload_dir = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], gallery)
    exists = os.path.exists(upload_dir)
    return jsonify({'exists': exists})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'photo' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file uploaded'}), 400

    file = request.files['photo']

    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No file selected'}), 400

    gallery = request.form.get('gallery', '')

    if gallery:
        upload_dir = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], gallery)
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
    else:
        upload_dir = app.config['UPLOADED_PHOTOS_DEST']

    filename = secure_filename(file.filename)
    file_path = os.path.join(upload_dir, filename)
    file.save(file_path)

    return jsonify({'status': 'success', 'filename': filename})

@app.route('/i/<gallery>/<filename>')
def serve_image(gallery, filename):
    upload_dir = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], gallery)
    return send_from_directory(upload_dir, filename)

@app.route('/i/<gallery>')
def gallery(gallery):
    upload_dir = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], gallery)
    if not os.path.exists(upload_dir):
        return "Gallery not found", 404

    files = [f for f in os.listdir(upload_dir) if os.path.isfile(os.path.join(upload_dir, f))]
    files.sort()
    version_id = get_version_id()
    return render_template('gallery.html', files=files, gallery=gallery, version_id=version_id)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOADED_PHOTOS_DEST']):
        os.makedirs(app.config['UPLOADED_PHOTOS_DEST'])
    app.run(host=config['HOST'], port=config['PORT'], debug=True)
