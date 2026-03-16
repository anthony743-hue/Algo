from app.database import db
from datetime import datetime

class PatientSymptom(db.Model):
    __tablename__ = 'patient_symptoms'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    symptom_id = db.Column(db.Integer, db.ForeignKey('symptoms.id', ondelete='CASCADE'), nullable=False)
    current_severity = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('patient_id', 'symptom_id', name='uq_patient_symptom'),)
    
    def __repr__(self):
        return f'<PatientSymptom patient_id={self.patient_id} symptom_id={self.symptom_id}>'