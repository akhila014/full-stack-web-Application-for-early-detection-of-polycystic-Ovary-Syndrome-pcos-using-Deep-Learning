import os
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime

from models import db, PCOSRecord
from cnn_model import get_cnn_prediction, hybrid_decision_logic, is_ultrasound_image

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pcos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'pcos_admin_secret_key_bvrit'  # required for sessions

db.init_app(app)

# --- Admin credentials (change these) ---
ADMIN_USERNAME = 'doctor'
ADMIN_PASSWORD = 'bvrit@2024'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        age = request.form.get('age')
        symptoms = request.form.get('symptoms')
        image_file = request.files['ultrasound']

        if image_file:
            image_path = image_file.filename
            image_file.save(image_path)

            if not is_ultrasound_image(image_path):
                try:
                    os.remove(image_path)
                except OSError:
                    pass
                return render_template('result.html',
                                       prediction="Invalid Image Uploaded",
                                       advice="The uploaded image is not a valid ovarian ultrasound scan. Please upload a proper ultrasound image.",
                                       confidence=0,
                                       date=datetime.now().strftime("%B %d, %Y"))

            cnn_score = get_cnn_prediction(image_path)
            prediction_result, health_advice, confidence = hybrid_decision_logic(age, symptoms, cnn_score)

            try:
                new_record = PCOSRecord(
                    age=int(age),
                    symptoms=symptoms,
                    prediction=prediction_result,
                    image_path=image_path
                )
                db.session.add(new_record)
                db.session.commit()
            except Exception as e:
                print(f"Database Error: {e}")

            return render_template('result.html',
                                   prediction=prediction_result,
                                   advice=health_advice,
                                   confidence=confidence,
                                   date=datetime.now().strftime("%B %d, %Y"))

    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('records'))
        else:
            error = "Invalid username or password."
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/records')
def records():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    all_records = PCOSRecord.query.order_by(PCOSRecord.date_created.desc()).all()
    return render_template('records.html', records=all_records)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)