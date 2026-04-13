import os
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from models import db, PCOSRecord
from cnn_model import get_cnn_prediction, hybrid_decision_logic

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin123@localhost:5433/pcos_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    age = request.form.get('age', 0)
    symptoms = request.form.get('symptoms', '')
    image_file = request.files.get('ultrasound')

    if image_file and image_file.filename != '':
        file_path = os.path.join(UPLOAD_FOLDER, image_file.filename)
        image_file.save(file_path)

        cnn_score = get_cnn_prediction(file_path)
        prediction_result, health_advice = hybrid_decision_logic(age, symptoms, cnn_score)

        try:
            new_record = PCOSRecord(
                age=int(age),
                symptoms=symptoms,
                prediction=prediction_result,
                image_path=file_path
            )
            db.session.add(new_record)
            db.session.commit()
        except Exception as e:
            print("Database Error:", e)

        return render_template(
            'results.html',
            prediction=prediction_result,
            advice=health_advice,
            date=datetime.now().strftime("%B %d, %Y")
        )

    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)