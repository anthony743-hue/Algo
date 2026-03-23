from app.database import db
from datetime import datetime
from app.models.medsEffect import MedicineEffect
from app.models.meds import Medicine

class Patient(db.Model):
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    patient_symptoms = db.relationship('PatientSymptom', backref='patient', lazy=True, cascade='all, delete-orphan')
    prescriptions = db.relationship('Prescription', backref='patient', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Patient {self.full_name}>'
    
    def getAllMeds(self, sympts, budget):
        meds_effects = MedicineEffect.query.all()
        meds = Medicine.query.all()
        return self.getAllMeds(sympts=sympts, meds=meds,meds_effects=meds_effects, budget=budget)
    
    def getAllMeds(self, sympts, meds, meds_effects, budget, total_effect=[]):
        n = len(meds)
        if budget <= 0:
            return [[i] for i in range(0,n)]
        res = []
        if len(total_effect) == 0:
            total_effect = [0] * (len(sympts))

        arr = [0] * len(sympts)
        min_price = max( m.price for m in meds )
        keep_price = min_price
        for i in range(0,n):
            max_index = 0
            temp_price = meds[i].price
            
            index = -1
            
            if budget - temp_price >= 0:
                temp_meds_effects = self.getAllMeds(sympts=sympts, meds=meds, meds_effects=meds_effects, budget=budget - temp_price) 
                for j in range(0, len(temp_meds_effects)):
                    sum_price = sum( meds )



        return res