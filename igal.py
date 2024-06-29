#!python

from flask import Flask, request, jsonify, send_from_directory, render_template
import os
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='static')
app.config['UPLOADED_PHOTOS_DEST'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Set maximum file size to 16 MB

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'photo' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file uploaded'}), 400

    file = request.files['photo']

    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No file selected'}), 400

    subdirectory = request.form.get('subdirectory', '')

    if subdirectory:
        upload_dir = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], subdirectory)
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
    else:
        upload_dir = app.config['UPLOADED_PHOTOS_DEST']

    filename = secure_filename(file.filename)
    file_path = os.path.join(upload_dir, filename)
    file.save(file_path)

    return jsonify({'status': 'success', 'filename': filename})

@app.route('/i/<subdirectory>/<filename>')
def serve_image(subdirectory, filename):
    upload_dir = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], subdirectory)
    return send_from_directory(upload_dir, filename)

@app.route('/i/<subdirectory>')
def gallery(subdirectory):
    upload_dir = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], subdirectory)
    if not os.path.exists(upload_dir):
        return "Subdirectory not found", 404

    files = [f for f in os.listdir(upload_dir) if os.path.isfile(os.path.join(upload_dir, f))]
    files.sort()
    return render_template('gallery.html', files=files, subdirectory=subdirectory)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOADED_PHOTOS_DEST']):
        os.makedirs(app.config['UPLOADED_PHOTOS_DEST'])
    app.run(host='0.0.0.0', port=17305, debug=True)
