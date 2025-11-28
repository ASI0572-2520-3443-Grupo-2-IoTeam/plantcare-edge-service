import os
from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from plant.interfaces.services import plant_blueprint
from shared.database import engine
from plant.infrastructure.models import Base

# Create tables only when explicitly requested via environment variable.
# In production (Gunicorn) this avoids opening a DB connection at import time
# which can fail during deployment. To run migrations/manually create tables,
# set env `RUN_CREATE_ALL=true` temporarily, or use a proper migration tool.
if os.getenv("RUN_CREATE_ALL", "false").lower() == "true":
    Base.metadata.create_all(bind=engine)


app = Flask(__name__)

# Enable CORS so the Swagger UI and other origins can call the API from browsers
CORS(app)

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
    app.run(debug=True)
