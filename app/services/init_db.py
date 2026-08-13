from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session
from app.models.calibration import MeasurementMethod
from app.models.trophy import AnimalSpecies
import logging

logger = logging.getLogger(__name__)

CARNIVORE_SPECIES = [
    ("Ursus arctos", "Бурый медведь"),
    ("Canis lupus", "Серый волк"),
    ("Vulpes vulpes", "Рыжая лиса"),
    ("Martes martes", "Обыкновенная куница"),
    ("Martes zibellina", "Соболь"),
    ("Gulo gulo", "Росомаха"),
    ("Lynx lynx", "Обыкновенная рысь"),
    ("Panthera tigris", "Амурский тигр"),
    ("Panthera leo", "Лев"),
    ("Felis silvestris", "Дикая кошка"),
]


async def initialize_database() -> None:
    """Seeds the database with default measurement method and carnivore species."""
    async with async_session() as session:
        # --- Seed MeasurementMethod ---
        existing_method = await session.execute(
            select(MeasurementMethod).where(MeasurementMethod.id == 1)
        )
        method_obj = existing_method.scalar_one_or_none()

        if method_obj is None:
            method_obj = MeasurementMethod(
                id=1,
                name="Метод 6 - Плотоядные",
                metric="CRAZIUS",
                requires_axis=True,
                requires_width=True,
                requires_length=True,
                version="1.0.0",
                is_active=True,
            )
            session.add(method_obj)
            logger.info("Seeded MeasurementMethod (id=1)")
        else:
            logger.info("MeasurementMethod (id=1) already exists, skipping")

        # --- Seed AnimalSpecies ---
        for name_la, name_ru in CARNIVORE_SPECIES:
            existing = await session.execute(
                select(AnimalSpecies).where(AnimalSpecies.name_la == name_la)
            )
            species_obj = existing.scalar_one_or_none()

            if species_obj is None:
                species_obj = AnimalSpecies(
                    name_la=name_la,
                    name_ru=name_ru,
                    is_active=True,
                )
                session.add(species_obj)
                logger.info(f"Seeded AnimalSpecies: {name_la} ({name_ru})")

        try:
            await session.commit()
            logger.info("Database initialization completed successfully")
        except Exception:
            await session.rollback()
            raise
