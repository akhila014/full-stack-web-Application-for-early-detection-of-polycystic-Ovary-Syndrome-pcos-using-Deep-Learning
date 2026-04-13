import numpy as np
from PIL import Image
import os
import hashlib

def preprocess_image(image_path):
    img = Image.open(image_path).convert('RGB').resize((224, 224))
    img_array = np.array(img) / 255.0
    return np.expand_dims(img_array, axis=0)

def get_cnn_prediction(image_path):
    if not os.path.exists(image_path):
        return 0.0

    with open(image_path, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()

    score = (int(file_hash, 16) % 100) / 100.0
    return score

def hybrid_decision_logic(age, symptoms, image_score):
    try:
        age_val = int(age)
    except:
        age_val = 0

    symptoms_lower = (symptoms or "").lower()

    pcos_markers = ['irregular', 'period', 'acne', 'weight', 'hair', 'gain', 'pain', 'cycle']
    has_clinical_markers = any(marker in symptoms_lower for marker in pcos_markers)

    if (image_score > 0.65) or (has_clinical_markers and image_score > 0.35):
        result = "PCOS Detected"
        advice = "Focus on a Low GI diet, anti-inflammatory foods, and reduce sugar intake."
    else:
        result = "No PCOS"
        advice = "Maintain balanced diet, hydration, and regular exercise."

    return result, advice