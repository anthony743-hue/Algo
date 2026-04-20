from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from app.database import db
from app.models.meds import Medicine
from app.models.medsEffect import MedicineEffect
from app.utils import (
    MedicineEffectsMap,
    RemedyItem,
    RemedyResult,
    SymptomState,
    apply_medicine_effect,
    build_meds_effects_map,
    build_symptom_state,
    calculate_integer_scalar,
    calculate_remaining_severities,
    calculate_total_effect,
    calculate_useful_coverage,
    is_symptom_state_resolved,
    to_decimal,
)

if TYPE_CHECKING:
    from app.models.patientSympt import PatientSymptom


class Patient(db.Model):
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient_symptoms = db.relationship('PatientSymptom', backref='patient', lazy=True, cascade='all, delete-orphan')
    # prescriptions = db.relationship('Prescription', backref='patient', lazy=True, cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f'<Patient {self.full_name}>'

    def getAllMeds(
        self,
        sympts: list['PatientSymptom'],
        budget: int,
    ) -> list[RemedyResult]:
        meds_effects = self._loadMedsEffectsMap()
        meds = Medicine.query.all()
        results: list[RemedyResult] = []
        seen: dict[tuple[int, tuple[int, ...]], Decimal] = {}

        self.getAllMedsRecursive(
            sympts=sympts,
            meds=meds,
            meds_effects=meds_effects,
            budget=budget,
            lst=[],
            res=results,
            arr=build_symptom_state(sympts),
            seen=seen,
            start_index=0,
        )

        results.sort(key=lambda remedy: (remedy['total_price'], len(remedy['items'])))
        return results

    def getCheapestRemedy(self, sympts: list['PatientSymptom']) -> RemedyResult | None:
        meds_effects = self._loadMedsEffectsMap()
        meds = Medicine.query.all()
        max_budget = self._estimateMaxBudget(sympts=sympts, meds=meds, meds_effects=meds_effects)

        if max_budget == 0:
            return None

        remedies = self.getAllMeds(sympts=sympts, budget=max_budget)
        return remedies[0] if remedies else None

    def getAffordableRemedy(
        self,
        sympts: list['PatientSymptom'],
        budget: Decimal | int | float,
    ) -> RemedyResult:
        meds_effects = self._loadMedsEffectsMap()
        meds = Medicine.query.all()
        items = self.generer_remede_incremental(
            liste_medicaments=meds,
            symptomes_initiaux=build_symptom_state(sympts),
            meds_effects=meds_effects,
            budget=budget,
        )
        return {
            'items': items,
            'total_price': self.getTotalPrice(items),
        }

    def getTotalPrice(self, arr: list[RemedyItem]) -> Decimal:
        return sum((item['total_price'] for item in arr), start=Decimal('0'))

    def isMedsEffective(
        self,
        sympts: list['PatientSymptom'],
        lst: SymptomState | None = None,
    ) -> bool:
        if lst is None:
            return False
        return is_symptom_state_resolved(
            build_symptom_state_from_remaining(
                sympts=sympts, 
                remaining=calculate_remaining_severities(symptoms=sympts, total_effects=lst)))

    def getTotalEffect(
        self,
        meds: list[RemedyItem],
        meds_effects: MedicineEffectsMap,
        symptoms: list['PatientSymptom'],
    ) -> SymptomState:
        return calculate_total_effect(remedy_items=meds, meds_effects=meds_effects, symptoms=symptoms)

    def selectionner_meilleur(
        self,
        liste_medicaments: list[Medicine],
        symptomes_patient: SymptomState,
        meds_effects: MedicineEffectsMap,
    ) -> Medicine | None:
        best_med: Medicine | None = None
        best_score = Decimal('-1')
        best_coverage = -1
        coverage = 0
        price = 0
        score = 0
        for med in liste_medicaments:
            coverage = calculate_useful_coverage(
                medicine_id=med.id,
                symptomes_patient=symptomes_patient,
                meds_effects=meds_effects,
            )
            if coverage <= 0:
                continue

            price = med.price
            score = Decimal(coverage) if price == 0 else Decimal(coverage) / price

            if score > best_score or (score == best_score and coverage > best_coverage):
                best_med = med
                best_score = score
                best_coverage = coverage

        return best_med

    def generer_remede_incremental(
        self,
        liste_medicaments: list[Medicine],
        symptomes_initiaux: SymptomState,
        meds_effects: MedicineEffectsMap,
        budget: Decimal | int | float,
    ) -> list[RemedyItem]:
        remede: list[RemedyItem] = []
        symptomes_courants = dict(symptomes_initiaux)
        medicaments_disponibles = list(liste_medicaments)

        while not is_symptom_state_resolved(symptomes_courants):
            meilleur_med = self.selectionner_meilleur(medicaments_disponibles, symptomes_courants, meds_effects)
            if meilleur_med is None:
                break

            k_needed = calculate_integer_scalar(medicine_id=meilleur_med.id, symptomes_patient=symptomes_courants, meds_effects=meds_effects)
            if k_needed == 0:
                break

            unit_price = meilleur_med.price
            max_affordable = k_needed if unit_price == 0 else int(budget // unit_price)
            quantite = min(k_needed, max_affordable)

            if quantite <= 0:
                break

            remede_item = self._buildRemedyItem(meilleur_med, quantite)
            remede.append(remede_item)
            budget -= remede_item['total_price']
            symptomes_courants = apply_medicine_effect(
                symptomes_restants=symptomes_courants,
                medicine_id=meilleur_med.id,
                quantite=quantite,
                meds_effects=meds_effects,
            )
            medicaments_disponibles = [med for med in medicaments_disponibles if med.id != meilleur_med.id]

        return remede

    def getAllMedsRecursive(
        self,
        sympts: list['PatientSymptom'],
        meds: list[Medicine],
        meds_effects: MedicineEffectsMap,
        budget: Decimal | int | float = 0,
        lst: list[RemedyItem] | None = None,
        res: list[RemedyResult] | None = None,
        arr: SymptomState | None = None,
        seen: dict[tuple[int, tuple[int, ...]], Decimal] | None = None,
        start_index: int = 0,
    ) -> None:
        remedy = lst if lst is not None else []
        results = res if res is not None else []
        remaining_symptoms = arr if arr is not None else build_symptom_state(sympts)
        visited = seen if seen is not None else {}

        if is_symptom_state_resolved(remaining_symptoms):
            results.append({
                'items': remedy,
                'total_price': self.getTotalPrice(remedy),
            })
            return

        if budget <= 0 or start_index >= len(meds):
            return

        state_key = (
            start_index,
            tuple(remaining_symptoms.get(symptom.symptom_id, 0) for symptom in sympts),
        )
        best_budget_seen = visited.get(state_key)
        if best_budget_seen is not None and best_budget_seen >= budget:
            return
        visited[state_key] = budget

        for med_index in self._orderCandidateIndexes(
            meds=meds,
            start_index=start_index,
            symptomes_restants=remaining_symptoms,
            meds_effects=meds_effects,
        ):
            med = meds[med_index]
            max_needed = calculate_integer_scalar(
                medicine_id=med.id,
                symptomes_patient=remaining_symptoms,
                meds_effects=meds_effects,
            )
            if max_needed == 0:
                continue

            max_affordable = max_needed if med.price == 0 else int(budget // med.price)
            max_quantity = min(max_needed, max_affordable)
            for quantity in range(1, max_quantity + 1):
                remedy_item = self._buildRemedyItem(med, quantity)
                next_remaining = apply_medicine_effect(
                    symptomes_restants=remaining_symptoms,
                    medicine_id=med.id,
                    quantite=quantity,
                    meds_effects=meds_effects,
                )
                self.getAllMedsRecursive(
                    sympts=sympts,
                    meds=meds,
                    meds_effects=meds_effects,
                    budget=budget - remedy_item['total_price'],
                    lst=remedy + [remedy_item],
                    res=results,
                    arr=next_remaining,
                    seen=visited,
                    start_index=med_index + 1,
                )
            
                

    def _loadMedsEffectsMap(self) -> MedicineEffectsMap:
        return build_meds_effects_map(MedicineEffect.query.all())

    def _buildRemedyItem(self, medicament: Medicine, quantite: int) -> RemedyItem:
        unit_price = to_decimal(medicament.price)
        return {
            'medicine_id': medicament.id,
            'medicine_name': medicament.name,
            'quantity': quantite,
            'unit_price': unit_price,
            'total_price': unit_price * quantite,
        }

    def _estimateMaxBudget(
        self,
        sympts: list['PatientSymptom'],
        meds: list[Medicine],
        meds_effects: MedicineEffectsMap,
    ) -> Decimal:
        symptomes_restants = build_symptom_state(sympts)
        total = Decimal('0')

        for med in meds:
            scalar = calculate_integer_scalar(
                medicine_id=med.id,
                symptomes_patient=symptomes_restants,
                meds_effects=meds_effects,
            )
            if scalar <= 0:
                continue
            total += to_decimal(med.price) * scalar

        return total

    def _orderCandidateIndexes(
        self,
        meds: list[Medicine],
        start_index: int,
        symptomes_restants: SymptomState,
        meds_effects: MedicineEffectsMap,
    ) -> list[int]:
        candidate_indexes = list(range(start_index, len(meds)))
        candidate_meds = [meds[index] for index in candidate_indexes]
        best_med = self.selectionner_meilleur(candidate_meds, symptomes_restants, meds_effects)

        def sort_key(index: int) -> tuple[Decimal, int]:
            med = meds[index]
            coverage = calculate_useful_coverage(
                medicine_id=med.id,
                symptomes_patient=symptomes_restants,
                meds_effects=meds_effects,
            )
            price = to_decimal(med.price)
            score = Decimal(coverage) if price == 0 else Decimal(coverage) / price
            return score, coverage

        ordered_indexes = sorted(candidate_indexes, key=sort_key, reverse=True)

        if best_med is None:
            return ordered_indexes

        best_index = next(index for index in candidate_indexes if meds[index].id == best_med.id)
        return [best_index] + [index for index in ordered_indexes if index != best_index]


def build_symptom_state_from_remaining(
    sympts: list['PatientSymptom'],
    remaining: list[int],
) -> SymptomState:
    return {
        symptom.symptom_id: remaining[index]
        for index, symptom in enumerate(sympts)
    }
