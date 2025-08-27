import os
from flask import Flask, render_template, request, redirect, url_for, send_file
from werkzeug.utils import secure_filename
import io

from encryption import generate_and_save_key, load_key, encrypt_file, decrypt_file_data

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, '..', 'uploads')
KEYS_DIR = os.path.join(BASE_DIR, '..', 'keys')

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(KEYS_DIR, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOADS_DIR

@app.route('/')
def index():
    files = [f for f in os.listdir(UPLOADS_DIR) if f.endswith('.enc')]
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    if file:
        original_filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
        file.save(temp_path)
        key = generate_and_save_key(original_filename)
        encrypted_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{original_filename}.enc")
        encrypt_file(temp_path, encrypted_path, key)
        os.remove(temp_path)

    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_page(filename):
    original_filename = filename.replace('.enc', '')
    return render_template('download.html', filename=original_filename)

@app.route('/download/confirm/<filename>')
def download_file(filename):
    key = load_key(filename)
    if not key:
        return "Error: Encryption key not found. The file cannot be decrypted.", 404

    encrypted_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename}.enc")
    try:
        decrypted_data = decrypt_file_data(encrypted_path, key)
    except Exception as e:
        return f"Error: Decryption failed. The file may be corrupt or the key is incorrect. Details: {e}", 500

    return send_file(
        io.BytesIO(decrypted_data),
        as_attachment=True,
        download_name=filename
    )

if __name__ == '__main__':
    app.run(debug=True)
