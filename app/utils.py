from __future__ import annotations

from decimal import Decimal
from math import ceil
from typing import TYPE_CHECKING, TypedDict

from app.models.medsEffect import MedicineEffect

if TYPE_CHECKING:
    from app.models.patientSympt import PatientSymptom

MedicineEffectsMap = dict[int, dict[int, MedicineEffect]]
SymptomState = dict[int, int]


class RemedyItem(TypedDict):
    medicine_id: int
    medicine_name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal

class RemedyResult(TypedDict):
    items: list[RemedyItem]
    total_price: Decimal

def to_decimal(value: Decimal | int | float | str) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def build_meds_effects_map(effects: list[MedicineEffect]) -> MedicineEffectsMap:
    effects_map: MedicineEffectsMap = {}

    for effect in effects:
        if effect.medicine_id not in effects_map:
            effects_map[effect.medicine_id] = {}
        effects_map[effect.medicine_id][effect.symptom_id] = effect

    return effects_map


def build_symptom_state(symptoms: list['PatientSymptom']) -> SymptomState:
    return {symptom.symptom_id: symptom.current_severity for symptom in symptoms}

def calculate_remaining_severities(
    symptoms: list['PatientSymptom'],
    total_effects: SymptomState | None = None,
) -> list[int]:
    applied_effects = total_effects or {}
    return [
        max(0, symptom.current_severity - applied_effects.get(symptom.symptom_id, 0))
        for symptom in symptoms
    ]


def is_symptom_state_resolved(symptom_state: SymptomState) -> bool:
    return all(value == 0 for value in symptom_state.values())


def calculate_total_effect(
    remedy_items: list[RemedyItem],
    meds_effects: MedicineEffectsMap,
    symptoms: list['PatientSymptom'],
) -> SymptomState:
    total_effects: SymptomState = {symptom.symptom_id: 0 for symptom in symptoms}

    for item in remedy_items:
        effects_by_symptom = meds_effects.get(item['medicine_id'], {})
        for symptom in symptoms:
            effect = effects_by_symptom.get(symptom.symptom_id)
            if effect is None:
                continue
            total_effects[symptom.symptom_id] += effect.effectiveness * item['quantity']

    return total_effects


def calculate_integer_scalar(
    medicine_id: int,
    symptomes_patient: SymptomState,
    meds_effects: MedicineEffectsMap,
) -> int:
    max_k = 0
    effects_by_symptom = meds_effects.get(medicine_id, {})

    for symptom_id, besoin in symptomes_patient.items():
        effect = effects_by_symptom.get(symptom_id)
        if besoin > 0 and effect is not None and effect.effectiveness > 0:
            max_k = max(max_k, ceil(besoin / effect.effectiveness))

    return max_k


def apply_medicine_effect(
    symptomes_restants: SymptomState,
    medicine_id: int,
    quantite: int,
    meds_effects: MedicineEffectsMap,
) -> SymptomState:
    next_state = dict(symptomes_restants)
    effects_by_symptom = meds_effects.get(medicine_id, {})
    effect = None
    for symptom_id, besoin in symptomes_restants.items():
        effect = effects_by_symptom.get(symptom_id)
        reduction = 0 if effect is None else effect.effectiveness * quantite
        if besoin <= 0 :
            continue
        next_state[symptom_id] = max(0, besoin - reduction)

    return next_state


def calculate_useful_coverage(
    medicine_id: int,
    symptomes_patient: SymptomState,
    meds_effects: MedicineEffectsMap,
) -> int:
    coverage = 0
    effects_by_symptom = meds_effects.get(medicine_id, {})
    effect = None
    for symptom_id, besoin in symptomes_patient.items():
        effect = effects_by_symptom.get(symptom_id)
        if besoin <= 0 or effect is None or effect.effectiveness <= 0:
            continue
        coverage += min(besoin, effect.effectiveness)

    return coverage
