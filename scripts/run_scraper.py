import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.config.settings import SessionLocal
from api.models.base import Base
from api.models.database import User, Animal, Shelter
from api.scrapers.web.nuevavida_scraper import NuevaVidaScraper
from sqlalchemy import text

def main():
    """Основная функция для запуска скрапера"""
    try:
        # Создаем сессию базы данных
        session = SessionLocal()
        
        # Очищаем таблицу animals и сбрасываем последовательность
        session.execute(text("TRUNCATE TABLE animals CASCADE;"))
        session.execute(text("ALTER SEQUENCE animals_id_seq RESTART WITH 1;"))
        session.commit()
        
        # Запускаем скрапер
        scraper = NuevaVidaScraper()
        animals, shelter_info = scraper.run()
        
        # Проверяем существующих животных
        existing_animals = session.query(Animal).all()
        existing_names = {animal.name for animal in existing_animals}
        
        # Создаем или получаем приют
        shelter = session.query(Shelter).filter(Shelter.name == shelter_info["name"]).first()
        if not shelter:
            shelter = Shelter(
                name=shelter_info["name"],
                address=shelter_info["address"],
                description=shelter_info["description"],
                website=shelter_info.get("website", "")
            )
            session.add(shelter)
            session.commit()
            session.refresh(shelter)
        
        # Сохраняем только новых животных
        for animal_data in animals:
            if animal_data['name'] not in existing_names:
                animal = Animal(
                    name=animal_data["name"],
                    gender=animal_data["gender"],
                    age=animal_data["age"],
                    birth_date=animal_data.get("birth_date"),
                    description=animal_data.get("description", ""),
                    image_url=animal_data.get("image_url", ""),
                    source_url=animal_data["source_url"],
                    is_adopted=animal_data.get("is_adopted", False),
                    shelter_id=shelter.id
                )
                session.add(animal)
                print(f"Added new animal: {animal_data['name']}")
            else:
                print(f"Animal already exists: {animal_data['name']}")
        
        session.commit()
        print(f"Successfully processed {len(animals)} animals")
        
    except Exception as e:
        print(f"Error running scraper: {str(e)}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    main() 