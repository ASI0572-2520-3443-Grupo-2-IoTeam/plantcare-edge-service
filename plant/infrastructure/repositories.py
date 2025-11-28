from abc import ABC, abstractmethod
from typing import List

from sqlalchemy.orm import Session

from plant.domain.entities import Plant
from plant.infrastructure.models import PlantModel


class PlantRepository(ABC):
    """
    Abstract base class for a plant repository.
    """

    @abstractmethod
    def save(self, plant: Plant) -> Plant:
        """Saves a plant entity to the repository."""
        pass

    @abstractmethod
    def get_all(self) -> List[Plant]:
        """Retrieves all plant entities from the repository."""
        pass


class SQLAlchemyPlantRepository(PlantRepository):
    """
    SQLAlchemy implementation of the plant repository.
    """

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def save(self, plant: Plant) -> Plant:
        """Saves a plant entity to the database."""
        plant_model = PlantModel(
            device_id=plant.device_id,
            temperature=plant.temperature,
            humidity=plant.humidity,
            light=plant.light,
            soil_humidity=plant.soil_humidity,
        )
        self.db_session.add(plant_model)
        self.db_session.commit()
        self.db_session.refresh(plant_model)
        return self._to_entity(plant_model)

    def get_all(self) -> List[Plant]:
        """Retrieves all plant entities from the database."""
        all_plant_models = (
            self.db_session.query(PlantModel).order_by(PlantModel.created_at.desc()).all()
        )
        return [self._to_entity(plant) for plant in all_plant_models]

    def _to_entity(self, plant_model: PlantModel) -> Plant:
        return Plant(
            id=plant_model.id,
            device_id=plant_model.device_id,
            temperature=plant_model.temperature,
            humidity=plant_model.humidity,
            light=plant_model.light,
            soil_humidity=plant_model.soil_humidity,
            created_at=plant_model.created_at,
        )