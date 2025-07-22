import requests
import os
import tempfile
import zipfile

SKETCHFAB_TOKEN = "5dece4e1ebfc4954b08fcabab7462449"

def search_model_uid(query):
    print(f"🔍 Searching Sketchfab for: {query} car")
    url = "https://api.sketchfab.com/v3/search"
    params = {
        "q": f"{query} car",
        "type": "models",
        "downloadable": "true",
        "sort_by": "relevance"
    }
    headers = {"Authorization": f"Token {SKETCHFAB_TOKEN}"}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print("❌ Failed to search models:", response.status_code)
        return None

    results = response.json().get("results", [])
    if not results:
        print("❌ No models found.")
        return None

    uid = results[0]["uid"]
    name = results[0]["name"]
    print(f"✅ Found model: {name} (UID: {uid})")
    return uid

def download_model(uid, save_path):
    print(f"⬇️ Attempting download of model UID: {uid}")
    headers = {"Authorization": f"Token {SKETCHFAB_TOKEN}"}
    url = f"https://api.sketchfab.com/v3/models/{uid}/download"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"❌ Failed to fetch download info: {response.status_code}")
        return False

    data = response.json()
    gltf_info = data.get("gltf")

    if not gltf_info or not gltf_info.get("url"):
        print("❌ No download URL found.")
        return False

    zip_url = gltf_info["url"]

    try:
        with requests.get(zip_url, stream=True) as r:
            r.raise_for_status()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_zip:
                for chunk in r.iter_content(chunk_size=8192):
                    tmp_zip.write(chunk)
                tmp_zip_path = tmp_zip.name

        with zipfile.ZipFile(tmp_zip_path, 'r') as zip_ref:
            extract_dir = os.path.dirname(save_path)
            zip_ref.extractall(extract_dir)
            extracted_files = zip_ref.namelist()

            # Try to find .glb
            for file in extracted_files:
                if file.endswith(".glb"):
                    extracted_path = os.path.join(extract_dir, file)
                    os.rename(extracted_path, save_path)
                    print(f"✅ Extracted and saved GLB: {save_path}")
                    return True

            # If no .glb, look for .gltf
            for file in extracted_files:
                if file.endswith(".gltf"):
                    print(f"⚠️ Only .gltf format found: {file}")
                    print("👉 Please load this model using GLTFLoader in Three.js with full folder support.")
                    return True

            print("❌ No .glb or .gltf model found in ZIP.")
            return False

    except Exception as e:
        print("❌ Error downloading or extracting model:", e)
        return False

def fetch_and_download_model(car_name, save_path):
    uid = search_model_uid(car_name)
    if not uid:
        print("❌ No UID found, skipping download.")
        return
    success = download_model(uid, save_path)
    if not success:
        print("❌ Failed to download and extract model.")
