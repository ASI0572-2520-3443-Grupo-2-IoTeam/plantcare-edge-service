from flask import Blueprint, request, jsonify

from plant.application.services import PlantApplicationService
from plant.domain.services import PlantService
from plant.infrastructure.repositories import SQLAlchemyPlantRepository
from shared.database import get_db_session

plant_blueprint = Blueprint("plant", __name__)


def _get_plant_application_service() -> PlantApplicationService:
    """
    Creates and returns an instance of the PlantApplicationService,
    injecting its dependencies.
    """
    # Use the generator properly to ensure cleanup
    session_gen = get_db_session()
    db_session = next(session_gen)
    try:
        plant_repository = SQLAlchemyPlantRepository(db_session=db_session)
        plant_service = PlantService()
        return PlantApplicationService(
            plant_service=plant_service, plant_repository=plant_repository
        )
    except Exception:
        # Close session on error
        try:
            next(session_gen, None)
        except StopIteration:
            pass
        raise


@plant_blueprint.route("/plants", methods=["GET"])
def get_all_plants():
    """
    Retrieves all plant data records.
    Returns a list of all sensor data stored in the database,
    ordered by creation date in descending order.
    ---
    tags:
      - Plants
    responses:
      200:
        description: A list of all plant data records.
        schema:
          type: array
          items:
            $ref: '#/definitions/Plant'
    definitions:
      Plant:
        type: object
        properties:
          deviceId:
            type: string
          timestamp:
            type: string
            format: date-time
          airTemperatureC:
            type: number
          airHumidityPct:
            type: number
          lightIntensityLux:
            type: integer
          soilMoisturePct:
            type: integer
    """
    plant_application_service = _get_plant_application_service()
    all_data = plant_application_service.get_all_plant_data()
    return jsonify(all_data)


@plant_blueprint.route("/plants", methods=["POST"])
def add_plant_data():
    """
    Endpoint to add new plant data.
    ---
    tags:
      - Plants
    parameters:
      - name: body
        in: body
        required: true
        schema:
          $ref: "#/definitions/PlantData"
    responses:
      200:
        description: Data successfully saved locally.
        schema:
          $ref: '#/definitions/Plant'
      400:
        description: Invalid JSON or missing required fields.
    definitions:
      PlantData:
        type: object
        required:
          - deviceId
          - timestamp
          - airTemperatureC
          - airHumidityPct
          - lightIntensityLux
          - soilMoisturePct
        properties:
          deviceId:
            type: string
            description: The unique ID of the IoT device.
            example: "esp32-100100C40A24"
          timestamp:
            type: string
            format: date-time
            description: The timestamp of the data record.
            example: "2025-11-27T00:37:30Z"
          airTemperatureC:
            type: number
            description: The air temperature recorded in degrees Celsius.
            example: 56
          airHumidityPct:
            type: number
            description: The air humidity recorded as a percentage.
            example: 53.5
          lightIntensityLux:
            type: integer
            description: The light level recorded in lux.
            example: 1001
          soilMoisturePct:
            type: integer
            description: The soil moisture recorded as a percentage.
            example: 100
    """
    data = request.get_json()
    required_fields = [
        "deviceId",
        "timestamp",
        "airTemperatureC",
        "airHumidityPct",
        "lightIntensityLux",
        "soilMoisturePct",
    ]

    if not data or not all(k in data for k in required_fields):
        return jsonify({"message": "Invalid JSON or missing required fields."}), 400

    # Map incoming camelCase JSON to the domain's expected snake_case keys
    mapped_data = {
      "device_id": data.get("deviceId"),
      "air_temperature_celsius": data.get("airTemperatureC"),
      "air_humidity_percent": data.get("airHumidityPct"),
      "luminosity_lux": data.get("lightIntensityLux"),
      "soil_moisture_percent": data.get("soilMoisturePct"),
    }

    plant_application_service = _get_plant_application_service()
    saved_plant_data = plant_application_service.add_plant_data(mapped_data)

    return jsonify(saved_plant_data), 200

