from app.database import db
from datetime import datetime

class Symptom(db.Model):
    __tablename__ = 'symptoms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.Text, default='')
    severity_scale = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    # medicine_effects = db.relationship('MedicineEffect', backref='symptom', lazy=True)
    # patient_symptoms = db.relationship('PatientSymptom', backref='symptom', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Symptom {self.name}>'