from app.database import db
from datetime import datetime

class Medicine(db.Model):
    __tablename__ = 'medicines'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    medicine_effects = db.relationship('MedicineEffect', backref='medicine', lazy=True, cascade='all, delete-orphan')
    prescription_medicines = db.relationship('PrescriptionMedicine', backref='medicine', lazy=True)
    
    def __repr__(self):
        return f'<Medicine {self.name}>'