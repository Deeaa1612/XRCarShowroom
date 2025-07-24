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
        return jsonify({'error': 'No PDF file uploaded'}), 400

    file = request.files['pdf']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    temp_path = os.path.join(UPLOAD_FOLDER, 'uploaded_brochure.pdf')
    file.save(temp_path)

    try:
        text = extract_clean_text(temp_path)
        info = extract_car_info(text)

        # Set model URL expected by frontend
        model_filename = info["name"].lower().replace(" ", "_") + ".glb"
        info["modelUrl"] = f"models/{model_filename}"

        save_json(info)
        shutil.copyfile("car_info.json", FRONTEND_JSON_PATH)
        check_or_download_model(info["name"])

        os.remove(temp_path)
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
