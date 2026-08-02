from flask import Flask, request, send_from_directory, jsonify, redirect, session
import os, random, smtplib, base64, time
from email.message import EmailMessage
from predict_model import predict_leaf_disease


# DISEASE PRECAUTIONS (BASE)

DISEASE_PRECAUTIONS = {
    "Tomato___Septoria_leaf_spot": [
        "Remove infected leaves immediately",
        "Avoid overhead irrigation",
        "Apply copper-based fungicide",
        "Ensure good air circulation",
        "Practice crop rotation"
    ],
    "Tomato___Late_blight": [
        "Destroy infected plants",
        "Avoid wet foliage",
        "Use certified disease-free seeds",
        "Apply fungicide early",
        "Ensure proper drainage"
    ],
    "Peach___Bacterial_spot": [
        "Prune infected branches",
        "Avoid water splash on leaves",
        "Apply copper sprays",
        "Use resistant varieties",
        "Sanitize garden tools"
    ],
    "Apple___Black_rot": [
        "Remove infected fruits",
        "Prune dead wood",
        "Maintain orchard hygiene",
        "Apply fungicides",
        "Improve sunlight exposure"
    ],
    "Healthy": [
        "Maintain balanced fertilization",
        "Monitor plant health regularly",
        "Ensure adequate watering",
        "Avoid overcrowding",
        "Keep soil healthy"
    ]
}


# APP CONFIG

app = Flask(__name__)
app.secret_key = "secure_ai_leaf_key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# EMAIL CONFIG

SENDER_EMAIL = "swathyasathi.ai@gmail.com"
SENDER_PASSWORD = "wcwuczytryshxtpn"

otp_store = {}
prediction_result = {}
OTP_EXPIRY = 300

# ROUTES


@app.route("/")
def home():
    return send_from_directory("templates", "index.html")

@app.route("/about")
def about():
    return send_from_directory("templates", "about.html")

@app.route("/login")
def login():
    return send_from_directory("templates", "login.html")

@app.route("/verify-otp")
def verify_otp():
    return send_from_directory("templates", "otp.html")

@app.route("/detect")
def detect():
    if not session.get("logged_in"):
        return redirect("/login")
    return send_from_directory("templates", "detect.html")

@app.route("/result")
def result():
    return send_from_directory("templates", "result.html")


# SEND OTP

@app.route("/send-otp", methods=["POST"])
def send_otp():
    email = request.form.get("email")
    otp = random.randint(100000, 999999)
    otp_store[email] = (otp, time.time())

    msg = EmailMessage()
    msg.set_content(f"Your OTP for AI Plant Disease Login is: {otp}")
    msg["Subject"] = "AI Plant Disease OTP"
    msg["From"] = SENDER_EMAIL
    msg["To"] = email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)

    session["email"] = email
    return redirect("/verify-otp")


# VERIFY OTP

@app.route("/check-otp", methods=["POST"])
def check_otp():
    email = request.form.get("email")
    user_otp = int(request.form.get("otp"))

    if email not in otp_store:
        return "OTP expired"

    saved_otp, ts = otp_store[email]

    if time.time() - ts > OTP_EXPIRY:
        return "OTP expired"

    if user_otp == saved_otp:
        session["logged_in"] = True
        otp_store.pop(email)
        return redirect("/detect")

    return "Invalid OTP"


# PREDICT IMAGE

@app.route("/predict", methods=["POST"])
def predict():
    global prediction_result

    if not session.get("logged_in"):
        return redirect("/login")

    img_path = None

    if "image" in request.files and request.files["image"].filename != "":
        file = request.files["image"]
        img_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(img_path)

    elif "image" in request.form:
        image_data = request.form["image"].split(",")[1]
        img_bytes = base64.b64decode(image_data)
        img_path = os.path.join(UPLOAD_FOLDER, "camera.jpg")
        with open(img_path, "wb") as f:
            f.write(img_bytes)

    if not img_path:
        return "No image uploaded", 400

    # ✅ EXACTLY 3 VALUES
    disease, confidence, precautions = predict_leaf_disease(img_path)

    prediction_result = {
        "disease": disease,
        "confidence": confidence,
        "precautions": precautions
    }

    return redirect("/result")


    # FILE UPLOAD
    if "image" in request.files and request.files["image"].filename != "":
        file = request.files["image"]
        img_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(img_path)

    # CAMERA IMAGE
    elif "image" in request.form:
        image_data = request.form["image"].split(",")[1]
        img_bytes = base64.b64decode(image_data)
        img_path = os.path.join(UPLOAD_FOLDER, "camera.jpg")
        with open(img_path, "wb") as f:
            f.write(img_bytes)

    if not img_path:
        return "No image uploaded", 400

    # AI PREDICTION 
    disease, confidence, precautions = predict_leaf_disease(img_path)


    precautions_list = DISEASE_PRECAUTIONS.get(disease, [
        "Maintain proper plant hygiene",
        "Avoid excessive moisture",
        "Monitor crop health regularly"
    ])

    # Convert precautions into AI-style paragraph
    precautions_text = (
        "Based on the detected disease, it is advised to "
        + ", ".join(precautions_list[:-1])
        + ", and "
        + precautions_list[-1]
        + "."
    )

    prediction_result = {
        "disease": disease.replace("___", " "),
        "confidence": round(float(confidence), 2),
        "precautions": precautions_text
    }

    return redirect("/result")


# RESULT DATA 

@app.route("/result-data")
def result_data():
    return jsonify(prediction_result)


# LOGOUT

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# RUN

if __name__ == "__main__":
    app.run(debug=True)
