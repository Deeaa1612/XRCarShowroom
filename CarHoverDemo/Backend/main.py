
import fitz  # PyMuPDF
import re
import json
import os
from unidecode import unidecode
from sketchfab_fetcher import fetch_and_download_model
from flask import Flask, request, jsonify

app = Flask(__name__)

def extract_clean_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    clean_text = unidecode(text)
    clean_text = re.sub(r"\s+", " ", clean_text)
    return clean_text.lower()

def extract_car_info(text):
    info = {
        "name": "unknown_car",
        "model": "unknown_model",
        "speed": "unknown",
        "acceleration": "unknown",
        "handling": "unknown",
        "safety": "unknown"
    }

    # --- Car Name & Model Extraction ---
    known_brands = [
        "hyundai", "toyota", "honda", "kia", "tata", "mahindra", "maruti", "suzuki",
        "ford", "nissan", "porsche", "audi", "bmw", "mercedes", "skoda", "volkswagen", "jeep", "renault", "mg", "lexus", "jaguar", "land rover"
    ]
    brand_pattern = r"|".join(known_brands)

    # Try to find lines like 'Model: i20', 'Variant: Sportz', etc.
    model_match = re.search(r"model\s*[:\-]?\s*([a-z0-9\- ]{2,})", text)
    if model_match:
        model_candidate = model_match.group(1).strip().split()[0]
        if model_candidate and len(model_candidate) <= 10:
            info["model"] = model_candidate

    # Tagline/generic words/phrases to ignore
    ignore_phrases = [
        "wherever", "goes", "captures", "attention", "features", "variant", "line", "series", "model", "offers", "with", "the", "and", "new", "all-new", "car", "introducing", "presenting", "experience", "enjoy", "drive", "journey", "adventure", "style", "comfort", "performance", "safety", "technology", "innovation", "luxury", "dynamic", "bold", "future", "now", "your", "our", "its", "it's", "inspired", "crafted", "designed", "engineered", "redefined", "revolution", "unleash", "power", "passion", "spirit", "dream", "beyond", "next", "generation", "iconic", "legendary", "ultimate", "premium", "modern", "urban", "city", "road", "destination", "explore", "discover", "smart", "connect", "connected", "world", "life", "choice", "option", "select", "pick", "choose", "enjoy", "delight", "fun", "exciting", "excite", "wow", "amaze", "amazing", "impress", "impressive", "imagination", "imagine", "future", "tomorrow", "today", "every", "each", "all", "any", "best", "better", "good", "great", "super", "superior", "top", "top-notch", "first", "class", "classy", "elite", "exclusive", "special", "limited", "edition", "editions", "series", "collection", "range", "segment", "category", "type", "kind", "sort", "variety", "array", "selection", "lineup", "portfolio", "suite", "package", "bundle", "deal", "offer", "offers", "offering", "present", "presented", "showcase", "showcased", "show", "display", "displayed", "exhibit", "exhibited", "feature", "featured", "highlight", "highlighted", "spotlight", "focus", "focused", "center", "centered", "core", "main", "major", "minor", "basic", "advanced", "pro", "plus", "max", "mini", "micro", "nano", "ultra", "hyper", "mega", "giga", "tera", "pico", "femto", "at", "by", "for", "from", "to", "of", "on", "in", "out", "up", "down", "over", "under", "above", "below", "across", "through", "between", "among", "around", "near", "far", "close", "away", "along", "alongside", "beside", "next", "after", "before", "since", "until", "while", "during", "within", "without", "about", "against", "toward", "towards", "upon", "off", "onto", "into", "out", "off", "beyond", "past", "per", "via", "as", "like", "unlike", "except", "but", "save", "than", "rather", "instead", "whether", "either", "neither", "nor", "not", "no", "yes", "yet", "still", "though", "although", "even", "however", "otherwise", "besides", "anyway", "anyhow", "regardless", "nonetheless", "nevertheless", "moreover", "furthermore", "additionally", "also", "plus", "too", "either", "neither", "both", "each", "every", "all", "some", "most", "many", "much", "several", "few", "little", "less", "least", "more", "mostly", "mainly", "largely", "partly", "partially", "entirely", "completely", "totally", "wholly", "fully", "utterly", "absolutely", "definitely", "certainly", "surely", "undoubtedly", "unquestionably", "clearly", "obviously", "plainly", "evidently", "apparently", "seemingly", "presumably", "probably", "likely", "possibly", "perhaps", "maybe", "conceivably", "potentially", "theoretically", "ideally", "hopefully", "thank", "thanks", "please", "welcome", "congratulations", "congrats", "cheers", "regards", "best", "wishes", "wish", "luck", "fortune", "success", "happy", "happiness", "joy", "delight", "pleasure", "enjoyment", "satisfaction", "contentment", "gratitude", "appreciation", "admiration", "respect", "esteem", "regard", "affection", "love", "like", "fondness", "preference", "desire", "wish", "hope", "dream", "aspiration", "ambition", "goal", "aim", "objective", "purpose", "intention", "plan", "project", "scheme", "strategy", "tactic", "method", "means", "way", "manner", "approach", "style", "fashion", "mode", "form", "type", "kind", "sort", "variety", "category", "class", "group", "set", "series", "collection", "range", "array", "selection", "lineup", "portfolio", "suite", "package", "bundle", "deal", "offer", "offers", "offering", "present", "presented", "showcase", "showcased", "show", "display", "displayed", "exhibit", "exhibited", "feature", "featured", "highlight", "highlighted", "spotlight", "focus", "focused", "center", "centered", "core", "main", "major", "minor", "basic", "advanced", "pro", "plus", "max", "mini", "micro", "nano", "ultra", "hyper", "mega", "giga", "tera", "pico", "femto", "at", "by", "for", "from", "to", "of", "on", "in", "out", "up", "down", "over", "under", "above", "below", "across", "through", "between", "among", "around", "near", "far", "close", "away", "along", "alongside", "beside", "next", "after", "before", "since", "until", "while", "during", "within", "without", "about", "against", "toward", "towards", "upon", "off", "onto", "into", "out", "off", "beyond", "past", "per", "via", "as", "like", "unlike", "except", "but", "save", "than", "rather", "instead", "whether", "either", "neither", "nor", "not", "no", "yes", "yet", "still", "though", "although", "even", "however", "otherwise", "besides", "anyway", "anyhow", "regardless", "nonetheless", "nevertheless", "moreover", "furthermore", "additionally", "also", "plus", "too", "either", "neither", "both", "each", "every", "all", "some", "most", "many", "much", "several", "few", "little", "less", "least", "more", "mostly", "mainly", "largely", "partly", "partially", "entirely", "completely", "totally", "wholly", "fully", "utterly", "absolutely", "definitely", "certainly", "surely", "undoubtedly", "unquestionably", "clearly", "obviously", "plainly", "evidently", "apparently", "seemingly", "presumably", "probably", "likely", "possibly", "perhaps", "maybe", "conceivably", "potentially", "theoretically", "ideally", "hopefully", "thank", "thanks", "please", "welcome", "congratulations", "congrats", "cheers", "regards", "best", "wishes", "wish", "luck", "fortune", "success", "happy", "happiness", "joy", "delight", "pleasure", "enjoyment", "satisfaction", "contentment", "gratitude", "appreciation", "admiration", "respect", "esteem", "regard", "affection", "love", "like", "fondness", "preference", "desire", "wish", "hope", "dream", "aspiration", "ambition", "goal", "aim", "objective", "purpose", "intention", "plan", "project", "scheme", "strategy", "tactic", "method", "means", "way", "manner", "approach", "style", "fashion", "mode", "form"]

    # Try to find 'Hyundai i20', 'Hyundai i20 N Line', etc. but filter out taglines
    name_matches = re.findall(rf"({brand_pattern})[\s\-]+([a-z0-9]+)", text)
    best_name = None
    for match in name_matches:
        brand = match[0].strip()
        model = match[1].strip()
        # Remove generic/tagline words
        if model in ignore_phrases or len(model) > 15:
            continue
        # Accept only if model is a single word and not empty
        if model:
            best_name = f"{brand} {model}".strip()
            if info["model"] == "unknown_model":
                info["model"] = model
            break
    if best_name:
        info["name"] = best_name

    # If still unknown, try to find the first occurrence of a brand followed by 1-3 words, filter out taglines
    if info["name"] == "unknown_car":
        full_name_match = re.search(rf"({brand_pattern})\s+([a-z0-9]+)", text)
        if full_name_match:
            brand = full_name_match.group(1).strip()
            model = full_name_match.group(2).strip()
            if model not in ignore_phrases and len(model) <= 15:
                info["name"] = f"{brand} {model}"
                if info["model"] == "unknown_model":
                    info["model"] = model

    # --- Speed / Power ---
    speed_match = re.search(r"(\d{2,3}(\.\d+)?)(\s*(km/l|kmph|km/h|ps|bhp|kw))", text)
    if speed_match:
        info["speed"] = f"{speed_match.group(1)} {speed_match.group(4)}"

    # --- Acceleration ---
    accel_match = re.search(r"0[-–]100\s*km/h\s*[:\-]?\s*(\d+\.?\d*)\s*s", text)
    if accel_match:
        info["acceleration"] = f"{accel_match.group(1)} s"
    else:
        info["acceleration"] = "not mentioned"

    # --- Handling ---
    if any(term in text for term in ["vehicle stability control", "hill hold", "cornering", "torque vectoring", "electronic stability"]):
        info["handling"] = "excellent"
    elif "traction control" in text:
        info["handling"] = "good"

    # --- Safety score ---
    safety_keywords = ["abs", "airbags", "ebd", "isofix", "collision", "lane assist", "seatbelt", "hill-start", "speed alert", "emergency stop"]
    safety_score = sum(1 for kw in safety_keywords if kw in text)
    if safety_score >= 5:
        info["safety"] = "5/5"
    elif safety_score >= 3:
        info["safety"] = "4/5"
    elif safety_score >= 1:
        info["safety"] = "3/5"

    # --- Feature Extraction ---
    feature_keywords = [
        "alloy wheels", "diamond cut", "led tail lamps", "projector headlamps", "cruise control",
        "rear ac vent", "wireless charger", "voice recognition", "hill-start assist",
        "vehicle stability management", "touchscreen", "android auto", "apple carplay",
        "rear parking camera", "airbags", "smart key", "push button start",
        "footwell lighting", "sunroof", "cng", "ambient lighting", "head-up display",
        "reverse camera", "steering mounted controls", "glove box", "tyre pressure monitoring",
        "rear defogger", "fog lamps", "automatic climate control", "multi info display",
        "rear wiper", "front armrest", "rear armrest", "rear spoiler", "shark fin antenna", "led drl", "auto headlamps", "rain sensing wipers", "paddle shifters", "ventilated seats", "leather seats", "wireless android auto", "wireless apple carplay", "rear seat recline", "360 camera", "blind spot monitor", "sunshade", "rear sunshade", "front parking sensors", "rear parking sensors"
    ]
    # Find features as bullet points or in feature sections
    features_found = set()
    # Look for bullet points
    for line in text.split(". "):
        for kw in feature_keywords:
            if kw in line:
                features_found.add(kw)
    # Also check the whole text
    for kw in feature_keywords:
        if kw in text:
            features_found.add(kw)
    info["features"] = sorted(features_found)

    return info



def save_json(info):
    with open("car_info.json", "w") as f:
        json.dump(info, f, indent=4)
    print("Saved car_info.json")

def check_or_download_model(car_name):
    model_name = car_name.lower().replace(" ", "_") + ".glb"
    model_path = f"../frontend/models/{model_name}"
    if os.path.exists(model_path):
        print(f"Model already exists: {model_path}")
    else:
        print(f"Model not found. Attempting download for: {car_name}")
        fetch_and_download_model(car_name, model_path)


# Flask route to handle PDF upload
@app.route('/upload', methods=['POST'])
def upload_brochure():
    if 'pdf' not in request.files:
        return jsonify({'error': 'No PDF file uploaded'}), 400
    file = request.files['pdf']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Save to a temporary path or process in-memory
    temp_path = 'uploaded_brochure.pdf'
    file.save(temp_path)

    try:
        text = extract_clean_text(temp_path)
        info = extract_car_info(text)
        save_json(info)
        check_or_download_model(info["name"])
        # Optionally, remove the temp file after processing
        os.remove(temp_path)
        return jsonify({'status': 'success', 'car_name': info["name"]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
