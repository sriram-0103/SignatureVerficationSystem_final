
from flask import Flask

from database.database import create_database

from routes.overview_routes import overview_bp
from routes.dashboard_routes import dashboard_bp
from routes.history_routes import history_bp
from routes.registration_routes import registration_bp
from routes.verification_routes import verification_bp
from routes.signature_routes import signature_bp
create_database()

app = Flask(__name__)

app.register_blueprint(overview_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(history_bp)
app.register_blueprint(registration_bp)
app.register_blueprint(verification_bp)
app.register_blueprint(signature_bp)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )