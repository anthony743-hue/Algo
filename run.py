from flask import Flask
from app.database import db
from app.routes.routes import home_bp
import os

app = Flask(__name__, template_folder="app/templates"
                    , static_folder="app/assets")
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/tp_meds'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.register_blueprint(home_bp)

# Initialiser la base de données
db.init_app(app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)