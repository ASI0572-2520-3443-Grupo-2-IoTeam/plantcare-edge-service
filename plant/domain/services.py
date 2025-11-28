from plant.domain.entities import Plant

# Constants for dictionary keys to avoid magic strings
KEY_DEVICE_ID = "device_id"
KEY_TEMPERATURE = "air_temperature_celsius"
KEY_HUMIDITY = "air_humidity_percent"
KEY_LIGHT = "luminosity_lux"
KEY_SOIL_HUMIDITY = "soil_moisture_percent"


class PlantService:
    """
    Domain service for handling plant-related operations.
    """

    def process_plant_data(self, data: dict) -> Plant:
        """
        Processes raw plant data and returns a Plant entity.

        Args:
            data: A dictionary containing the plant data.

        Returns:
            A Plant entity.
        """
        return Plant(
            id=None,  # The ID will be assigned by the database
            device_id=data[KEY_DEVICE_ID],
            temperature=data[KEY_TEMPERATURE],
            humidity=data[KEY_HUMIDITY],
            light=data[KEY_LIGHT],
            soil_humidity=data[KEY_SOIL_HUMIDITY],
            created_at=None  # The creation date will be assigned by the database
        )
