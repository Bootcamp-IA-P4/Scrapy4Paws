import os
import sys

# Добавляем текущую директорию в PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config.settings import SessionLocal
from models.database import Animal, Shelter
from scrapers.web.nuevavida_scraper import NuevaVidaScraper
from sqlalchemy import text

def main():
    """Основная функция для запуска скрапера"""
    try:
        print("\nStarting scraper process...")
        # Создаем сессию базы данных
        session = SessionLocal()
        
        # Очищаем таблицу animals и сбрасываем последовательность
        print("Clearing existing data...")
        session.execute(text("TRUNCATE TABLE animals CASCADE;"))
        session.execute(text("ALTER SEQUENCE animals_id_seq RESTART WITH 1;"))
        session.commit()
        
        # Запускаем скрапер
        print("Starting scraper...")
        scraper = NuevaVidaScraper()
        animals, shelter_info = scraper.run()
        print(f"Scraper finished. Found {len(animals)} animals")
        
        # Создаем или получаем приют
        print(f"\nProcessing shelter: {shelter_info['name']}")
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
            print(f"Created new shelter with ID: {shelter.id}")
        else:
            print(f"Found existing shelter with ID: {shelter.id}")
        
        # Сохраняем животных
        print("\nSaving animals to database...")
        for animal_data in animals:
            try:
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
                print(f"Added animal: {animal_data['name']}")
            except Exception as e:
                print(f"Error saving animal {animal_data.get('name', 'unknown')}: {str(e)}")
        
        session.commit()
        print(f"\nSuccessfully processed {len(animals)} animals")
        
    except Exception as e:
        print(f"Error running scraper: {str(e)}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    main() 