from flask import render_template, Blueprint, request
from app.models.symptom import Symptom

home_bp = Blueprint('home', __name__)

@home_bp.route("/")
def getHome():
    return render_template('index.html')

@home_bp.route("/patient-symptoms")
def getForm():
    arr = Symptom.query.all()
    return render_template('patient/sympts.html', lsSympt=arr)

@home_bp.route("/patient-symptoms/submit", methods=['POST'])
def getOrdonnace():
    return render_template('/ordonnance')