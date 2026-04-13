from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.sql import func

db = SQLAlchemy()

class PCOSRecord(db.Model):
    __tablename__ = 'pcos_records'
    
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer, nullable=False)
    symptoms = db.Column(db.Text, nullable=False)
    prediction = db.Column(db.String(20), nullable=False, index=True)
    image_path = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), server_default=func.now(), index=True)

    def __repr__(self):
        return f'<Record {self.id} - {self.prediction}>'

    def to_dict(self):
        return {
            "id": self.id,
            "age": self.age,
            "symptoms": self.symptoms,
            "prediction": self.prediction,
            "image_path": self.image_path,
            "date_created": self.date_created
        }