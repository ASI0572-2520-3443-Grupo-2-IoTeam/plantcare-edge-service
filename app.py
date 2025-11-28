import os
from flask import Flask, request
from flask_cors import CORS
from flasgger import Swagger
from plant.interfaces.services import plant_blueprint
from shared.database import engine, ensure_database_exists
from plant.infrastructure.models import Base

# Ensure database exists and create all tables automatically on startup
try:
    print("[app.py] Ensuring database and tables exist...")
    ensure_database_exists()
    Base.metadata.create_all(bind=engine)
    print("[app.py] Database and tables ready!")
except Exception as e:
    print(f"[app.py] Warning during database setup: {e}")
    print("[app.py] Continuing anyway - some features may not work until database is ready")


app = Flask(__name__)

# Enable CORS so the Swagger UI and other origins can call the API from browsers
CORS(app)


@app.before_request
def log_request_info():
    try:
        headers = dict(request.headers)
    except Exception:
        headers = {}
    app.logger.info("Request: %s %s headers=%s", request.method, request.url, headers)

# Configure and initialize Swagger with professional English documentation
swagger_host = os.getenv("SWAGGER_HOST", "").strip()

swagger_config = {
    "swagger": "2.0",
    "info": {
        "title": "Plant Care Edge Service API Documentation",
        "description": (
            "This API allows you to manage and monitor plant data, including "
            "temperature, humidity, light, and soil moisture levels. It is "
            "designed for IoT devices like ESP32 to send sensor data."
        ),
        "version": "1.0.0",
        "contact": {"name": "Plant Care Support", "email": "support@plantcare.com"},
    },
}

# If a specific host is provided via env, include it; otherwise let Flasgger
# use the request host (avoid hardcoding `127.0.0.1:5000` which breaks Try-it-out
# when the UI is served from a remote host).
if swagger_host:
    swagger_config["host"] = swagger_host

# Default basePath and other settings (kept separate to keep diff small)
# Support both HTTP (local dev) and HTTPS (production on Render)
swagger_config.update(
    {
        "basePath": "/",
        "schemes": ["https", "http"],
        "specs": [
            {
                "endpoint": "apispec_1",
                "route": "/apispec_1.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "headers": [],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/",
    }
)

# Initialize Swagger with the updated configuration
swagger = Swagger(app, config=swagger_config)

app.register_blueprint(plant_blueprint)

@app.route("/")
def read_root():
    """
    Main endpoint of the application.
    This endpoint is used to verify that the service is running.
    ---
    responses:
      200:
        description: A welcome message.
        examples:
          text/plain: "Welcome to the Plant Care Edge Service API"
    """
    return "Welcome to the Plant Care Edge Service API"

if __name__ == '__main__':
    # Run with an ad-hoc SSL context for local HTTPS (development only)
    app.run(debug=True, ssl_context='adhoc')
