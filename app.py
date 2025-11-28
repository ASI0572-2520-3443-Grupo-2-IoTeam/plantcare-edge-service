from flask import Flask
from flasgger import Swagger
from plant.interfaces.services import plant_blueprint
from shared.database import engine
from plant.infrastructure.models import Base

# Crear tablas de la base de datos
Base.metadata.create_all(bind=engine)


app = Flask(__name__)

# Configure and initialize Swagger with professional English documentation
swagger_config = {
    "swagger": "2.0",
    "info": {
        "title": "Plant Care Edge Service API Documentation",
        "description": "This API allows you to manage and monitor plant data, including temperature, humidity, light, and soil moisture levels. It is designed for IoT devices like ESP32 to send sensor data.",
        "version": "1.0.0",
        "contact": {
            "name": "Plant Care Support",
            "email": "support@plantcare.com",
        },
    },
    "host": "127.0.0.1:5000",  # Ensure this matches your running host and port
    "basePath": "/",  # Base path for all endpoints
    "schemes": ["http"],  # Use "https" if your app runs on HTTPS
    "specs": [
        {
            "endpoint": "apispec_1",
            "route": "/apispec_1.json",
            "rule_filter": lambda rule: True,  # Include all endpoints
            "model_filter": lambda tag: True,  # Include all models
        }
    ],
    "headers": [],  # Ensure headers key is defined as an empty list
    "static_url_path": "/flasgger_static",  # Default static files path
    "swagger_ui": True,  # Enable Swagger UI
    "specs_route": "/apidocs/",  # Route where Swagger UI is available
}

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
