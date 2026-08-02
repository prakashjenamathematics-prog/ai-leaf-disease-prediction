import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
import os

# =============================
# PATHS
# =============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "leaf_disease_model.h5")
CLASS_PATH = os.path.join(BASE_DIR, "class_names.txt")

IMG_SIZE = 224
CONFIDENCE_THRESHOLD = 60.0

# =============================
# LOAD MODEL & CLASSES
# =============================
model = tf.keras.models.load_model(MODEL_PATH)

with open(CLASS_PATH, "r") as f:
    CLASS_NAMES = [line.strip() for line in f.readlines()]

# =============================
# AI PRECAUTION GENERATOR
# =============================
def generate_precautions(disease):
    disease = disease.lower()

    if "bacterial" in disease:
        return (
            "This disease is bacterial in nature. Avoid overhead irrigation because "
            "water splashes help bacteria spread rapidly. Remove and destroy infected "
            "leaves early. Always disinfect tools after use and apply copper-based "
            "sprays cautiously during initial stages."
        )

    elif "blight" in disease:
        return (
            "Blight develops rapidly in wet and humid conditions. Improve air circulation "
            "between plants and avoid watering in the evening. Remove infected plant parts "
            "immediately and maintain good drainage to prevent recurrence."
        )

    elif "spot" in disease:
        return (
            "Leaf spot diseases occur due to prolonged moisture on leaves. Avoid dense "
            "planting, remove infected foliage early, and keep tools clean. Apply fungicide "
            "only if infection continues to spread."
        )

    elif "mosaic" in disease:
        return (
            "Mosaic disease is viral and spreads through insect vectors. Control aphids "
            "and other pests, remove infected plants completely, and avoid touching healthy "
            "plants after handling diseased ones."
        )

    elif "healthy" in disease:
        return (
            "The plant appears healthy. Continue balanced irrigation, nutrition, and regular "
            "monitoring to maintain plant health and prevent future infections."
        )

    else:
        return (
            "The image does not clearly represent a known plant disease. Ensure good crop "
            "hygiene, avoid excessive watering, and upload a clear leaf image for accurate detection."
        )

# =============================
# MAIN AI FUNCTION
# =============================
def predict_leaf_disease(img_path):
    img = image.load_img(img_path, target_size=(IMG_SIZE, IMG_SIZE))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    preds = model.predict(img_array, verbose=0)[0]
    confidence = float(np.max(preds)) * 100
    disease = CLASS_NAMES[int(np.argmax(preds))]

    if confidence < CONFIDENCE_THRESHOLD:
        return (
            "Unknown / Invalid Image",
            round(confidence, 2),
            "The uploaded image does not appear to be a clear plant leaf. Please upload a proper leaf image."
        )

    precautions = generate_precautions(disease)
    return disease, round(confidence, 2), precautions
