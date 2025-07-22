from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import shutil
from main import extract_clean_text, extract_car_info, save_json, check_or_download_model

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = '../uploads'
FRONTEND_MODELS_FOLDER = '../frontend/models'
FRONTEND_JSON_PATH = '../frontend/car_info.json'

@app.route('/upload', methods=['POST'])
def upload_brochure():
    if 'pdf' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    pdf = request.files['pdf']
    if pdf.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    pdf_path = os.path.join(UPLOAD_FOLDER, 'brochure.pdf')
    pdf.save(pdf_path)

    try:
        text = extract_clean_text(pdf_path)
        info = extract_car_info(text)
        save_json(info)

        # Move JSON to frontend
        shutil.copyfile('car_info.json', FRONTEND_JSON_PATH)

        # Download model to frontend
        check_or_download_model(info["name"])

        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
