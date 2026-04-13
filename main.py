def getAllMeds(self, sympts, budget):
    temp =  MedicineEffect.query.all()
    meds_effects = {  }
    for m in temp:
        key = m.medicine_id
        if key not in meds_effects:
            meds_effects[key] = {}
        meds_effects[key][m.symptom_id] = m
    meds = Medicine.query.all()
    res = []
    self.getAllMedsRecursive(sympts=sympts, meds=meds, meds_effects=meds_effects, budget=budget, lst=[], res=res)
    return res

def getTotalPrice(self, arr):
    if len(arr) == 0:
        return 0
    return sum( m.price for m in arr )
def getImportanceEffect(self, sympts, lst={}):
    if len(lst) == 0:
        return False
    
    diff = 0
    for m in sympts:
        diff = lst.get(m.symptom_id,0) - m.current_severity
        if diff > 0:
            return False
    return True

def getTotalEffect(self, meds, meds_effects, symptoms, arr = {}, level=0):
    n = len(meds_effects)
    if level == 0:
        arr = { s.symptom_id : 0 for s in symptoms }
    for m in meds:
        temp = meds_effects.get(m.id, {})
        for s in symptoms:
            idx = s.symptom_id
            arr[idx] = arr[idx] + temp.get(idx, type('obj', (object,), {'effectiveness': 0})).effectiveness
def getAllMedsRecursive(self, sympts, meds, meds_effects, budget=0, level=0,lst=[],res=[], arr={}):
    if budget <= 0 or level > len(meds):
        return
    if self.getImportanceEffect(sympts, lst=arr):
        res.append(lst)
        return
    for med in meds:
        temp = lst + [med]
        prix_total = self.getTotalPrice(temp) 
        if prix_total > budget:
            continue
        
        self.getTotalEffect(meds=temp,meds_effects=meds_effects, symptoms=sympts,arr=arr, level=level)
        self.getAllMedsRecursive(sympts=sympts, meds=meds, meds_effects=meds_effects, budget=budget - prix_total, res=res, lst=temp, arr=arr, level=-1)
        return