from app.database import db
from datetime import datetime

class MedicineEffect(db.Model):
    __tablename__ = 'medicine_effects'
    
    id = db.Column(db.Integer, primary_key=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id', ondelete='CASCADE'), nullable=False)
    symptom_id = db.Column(db.Integer, db.ForeignKey('symptoms.id', ondelete='CASCADE'), nullable=False)
    effectiveness = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # __table_args__ = (db.UniqueConstraint('medicine_id', 'symptom_id', name='uq_medicine_symptom'),)
    
    def __repr__(self):
        return f'<MedicineEffect medicine_id={self.medicine_id} symptom_id={self.symptom_id}>'