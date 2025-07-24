import fitz  # PyMuPDF
import re
import json
import os
import subprocess
from unidecode import unidecode
from sketchfab_fetcher import fetch_and_download_model

def extract_clean_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    clean_text = unidecode(text)
    clean_text = re.sub(r"\s+", " ", clean_text)
    return clean_text.lower()

def call_ollama_mistral(prompt, system_prompt):
    try:
        result = subprocess.run(
            ["ollama", "run", "mistral"],
            input=json.dumps({
                "system": system_prompt,
                "prompt": prompt
            }),
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print("❌ Ollama call failed:", e.stderr)
        return None

def extract_car_info(text):
    info = {
        "name": "unknown_car",
        "speed": "unknown",
        "acceleration": "unknown",
        "handling": "unknown",
        "safety": "unknown"
    }

    known_brands = [
        "hyundai", "toyota", "honda", "kia", "tata", "mahindra", "maruti",
        "suzuki", "ford", "nissan", "porsche", "audi", "bmw", "mercedes"
    ]
    brand_pattern = r"|".join(known_brands)
    full_name_match = re.search(rf"({brand_pattern})(\s+[a-z0-9]+){{1,3}}", text)
    if full_name_match:
        raw_name = full_name_match.group(0).strip()
        print(f"📝 Raw extracted name: {raw_name}")

        print("🧠 Validating name using Mistral via Ollama...")
        system_prompt = (
            "You are a helpful assistant extracting proper car names from brochures. "
            "Given a noisy string from a brochure like 'Hyundai Grand i10 Nios safety features', "
            "extract only the clean car name without extra marketing or feature-related terms. "
            "Do not include things like 'features', 'safety', 'top speed', etc. "
            "Only return the clean car name. Example outputs: 'Hyundai Grand i10 Nios', 'Kia Seltos', 'Maruti Suzuki Baleno'."
        )
        cleaned_name = call_ollama_mistral(prompt=raw_name, system_prompt=system_prompt)
        if cleaned_name:
            info["name"] = cleaned_name.lower().strip()
        else:
            info["name"] = raw_name.lower().strip()

    speed_match = re.search(r"(\d{2,3}(\.\d+)?)(\s*(km/l|kmph|km/h|ps|bhp|kw))", text)
    if speed_match:
        info["speed"] = f"{speed_match.group(1)} {speed_match.group(4)}"

    accel_match = re.search(r"0[-–]100\s*km/h\s*[:\-]?\s*(\d+\.?\d*)\s*s", text)
    if accel_match:
        info["acceleration"] = f"{accel_match.group(1)} s"
    else:
        info["acceleration"] = "not mentioned"

    if any(term in text for term in ["vehicle stability control", "hill hold", "cornering", "torque vectoring", "electronic stability"]):
        info["handling"] = "excellent"
    elif "traction control" in text:
        info["handling"] = "good"

    safety_keywords = ["abs", "airbags", "ebd", "isofix", "collision", "lane assist", "seatbelt", "hill-start", "speed alert", "emergency stop"]
    safety_score = sum(1 for kw in safety_keywords if kw in text)
    if safety_score >= 5:
        info["safety"] = "5/5"
    elif safety_score >= 3:
        info["safety"] = "4/5"
    elif safety_score >= 1:
        info["safety"] = "3/5"

    feature_keywords = [
        "alloy wheels", "diamond cut", "led tail lamps", "projector headlamps", "cruise control",
        "rear ac vent", "wireless charger", "voice recognition", "hill-start assist",
        "vehicle stability management", "touchscreen", "android auto", "apple carplay",
        "rear parking camera", "airbags", "smart key", "push button start",
        "footwell lighting", "sunroof", "cng", "ambient lighting", "head-up display",
        "reverse camera", "steering mounted controls", "glove box", "tyre pressure monitoring",
        "rear defogger", "fog lamps", "automatic climate control", "multi info display"
    ]
    features_found = [kw for kw in feature_keywords if kw in text]
    info["features"] = features_found

    return info

def save_json(info):
    with open("car_info.json", "w") as f:
        json.dump(info, f, indent=4)
    print("✅ Saved car_info.json")

def check_or_download_model(car_name):
    model_name = car_name.lower().replace(" ", "_") + ".glb"
    model_path = f"../frontend/models/{model_name}"
    if os.path.exists(model_path):
        print(f"✅ Model already exists: {model_path}")
    else:
        print(f"📦 Model not found. Attempting download for: {car_name}")
        fetch_and_download_model(car_name, model_path)

def main():
    pdf_path = "../uploads/brochure.pdf"

    print("📄 Extracting text from brochure...")
    text = extract_clean_text(pdf_path)

    print("🔍 Extracting car details...")
    info = extract_car_info(text)

    save_json(info)
    check_or_download_model(info["name"])

    print("✅ Pipeline completed.")
    print(json.dumps(info, indent=4))

if __name__ == "__main__":
    main()
