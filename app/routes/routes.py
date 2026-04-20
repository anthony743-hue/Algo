from __future__ import annotations

from decimal import Decimal, InvalidOperation

from flask import Blueprint, render_template, request, current_app

from app.models.patient import Patient
from app.models.symptom import Symptom
from app.utils import to_decimal, _extract_selected_symptoms

home_bp = Blueprint('home', __name__)


@home_bp.route("/")
def getHome():
    return render_template('index.html')


@home_bp.route("/patient-symptoms")
def getForm():
    arr = Symptom.query.order_by(Symptom.name.asc()).all()
    return render_template('patient/sympts.html', lsSympt=arr)


@home_bp.post("/patient-symptoms/submit")
def getOrdonnance():
    sympts = _extract_selected_symptoms(request.form)
    budget = int(request.form.get('budget', '0'))

    if not sympts:
        return render_template(
            'meds/lazy.html',
            budget=budget,
            selected_symptoms=[],
            partial_remedy={'items': [], 'total_price': Decimal('0')},
            cheapest_remedy=None,
            missing_amount=None,
            error_message="Aucun symptôme valide n'a été sélectionné.",
        )

    patient = Patient(full_name='Simulation')
    best_remedies = patient.getAllMeds(sympts=sympts, budget=budget)

    if best_remedies:
        best_remedy = best_remedies[0]
        return render_template(
            'meds/success.html',
            budget=budget,
            best_remedy=best_remedy,
            alternatives=best_remedies[1:4],
            selected_symptoms=sympts,
        )

    cheapest_remedy = patient.getCheapestRemedy(sympts=sympts)
    partial_remedy = patient.getAffordableRemedy(sympts=sympts, budget=budget)
    missing_amount = None

    if cheapest_remedy is not None:
        missing_amount = max(Decimal('0'), cheapest_remedy['total_price'] - to_decimal(budget))

    return render_template(
        'meds/lazy.html',
        budget=budget,
        selected_symptoms=sympts,
        partial_remedy=partial_remedy,
        cheapest_remedy=cheapest_remedy,
        missing_amount=missing_amount,
    )



