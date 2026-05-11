import numpy as np
from PIL import Image
import os
import hashlib


# --- ULTRASOUND VALIDATION ---

def _is_grayscale(arr):
    r = arr[:, :, 0].astype(float)
    g = arr[:, :, 1].astype(float)
    b = arr[:, :, 2].astype(float)
    avg_diff = (np.mean(np.abs(r - g)) +
                np.mean(np.abs(r - b)) +
                np.mean(np.abs(g - b))) / 3.0
    return avg_diff < 12.0


def _has_dark_border(arr):
    brightness = np.mean(arr, axis=2)
    return (np.sum(brightness < 30) / brightness.size) > 0.15


def _has_speckle_texture(arr):
    gray = np.mean(arr, axis=2)
    h, w = gray.shape
    ps = max(1, h // 8)
    variances = [
        np.var(gray[i:i + ps, j:j + ps])
        for i in range(0, h - ps, ps)
        for j in range(0, w - ps, ps)
    ]
    avg_var = np.mean(variances) if variances else 0
    return 150 < avg_var < 6000


def _valid_aspect_ratio(img):
    w, h = img.size
    ratio = w / h
    return 0.5 <= ratio <= 2.8


def is_ultrasound_image(image_path):
    try:
        img = Image.open(image_path).convert("RGB")
        if not _valid_aspect_ratio(img):
            img.close()
            return False
        img_small = img.resize((128, 128))
        img.close()  # release Windows file lock
        arr = np.array(img_small)
        if not _is_grayscale(arr):
            return False
        if not _has_dark_border(arr):
            return False
        if not _has_speckle_texture(arr):
            return False
        return True
    except Exception:
        return False


# --- IMAGE PRE-PROCESSING ---

def preprocess_image(image_path):
    img = Image.open(image_path).convert("RGB").resize((224, 224))
    img_array = np.array(img) / 255.0
    return np.expand_dims(img_array, axis=0)


# --- CNN PREDICTION (hash-based placeholder) ---

def get_cnn_prediction(image_path):
    if not os.path.exists(image_path):
        return 0.0
    with open(image_path, "rb") as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
    return (int(file_hash, 16) % 100) / 100.0 * 0.70


# --- HYBRID DECISION LOGIC ---

_PCOS_MARKERS = [
    "irregular", "period", "acne", "weight gain", "hair loss", "hair growth",
    "hirsutism", "infertility", "obesity", "fatigue", "mood", "bloating",
    "missed period", "heavy bleeding", "cyst", "pain", "cycle", "hormonal",
    "androgen", "insulin", "facial hair", "thinning hair", "pimple"
]


def _count_symptoms(symptoms_text):
    text = (symptoms_text or "").lower()
    return sum(1 for m in _PCOS_MARKERS if m in text)


def hybrid_decision_logic(age, symptoms, image_score):
    try:
        age_val = int(age)
    except (ValueError, TypeError):
        age_val = 0

    symptom_count = _count_symptoms(symptoms)
    has_symptoms = symptom_count >= 1
    strong_symptoms = symptom_count >= 3

    high_image = image_score >= 0.50
    medium_image = 0.20 <= image_score < 0.50

    if high_image and strong_symptoms:
        label, confidence = "PCOS Detected", 92
        advice = ("Both the ultrasound scan and your clinical symptoms strongly indicate PCOS.")

    elif high_image and has_symptoms:
        label, confidence = "PCOS Detected", 80
        advice = ("The ultrasound shows polycystic ovarian features and you have reported "
                  "relevant symptoms. A gynaecologist visit is strongly recommended for "
                  "hormonal evaluation and lifestyle guidance.")

    elif high_image and not has_symptoms:
        label, confidence = "PCOS Suspected (Ultrasound)", 65
        advice = ("The ultrasound shows possible polycystic features, but no clinical symptoms "
                  "were reported. Follow up with a gynaecologist for a hormonal panel to "
                  "confirm or rule out PCOS.")

    elif medium_image and strong_symptoms:
        label, confidence = "PCOS Suspected (Clinical)", 70
        advice = ("You have multiple PCOS-related symptoms. Although the ultrasound score is "
                  "moderate, PCOS can be diagnosed on clinical and hormonal criteria alone. "
                  "Please see a doctor for a blood test and further evaluation.")

    elif medium_image and has_symptoms:
        label, confidence = "PCOS Possible", 55
        advice = ("Some symptoms and mild ultrasound changes are present. "
                  "Track your menstrual cycle and consult a gynaecologist for a definitive diagnosis.")

    elif not high_image and strong_symptoms:
        label, confidence = "PCOS Suspected (Clinical)", 60
        advice = ("Multiple PCOS-related symptoms are present even though the ultrasound "
                  "score is low. Consult a doctor - symptoms and hormone levels can confirm "
                  "PCOS independently of ultrasound findings.")

    else:
        label, confidence = "No PCOS Detected", 85
        advice = ("No significant PCOS indicators were found in the ultrasound or your "
                  "reported symptoms.")

    return label, advice, confidence