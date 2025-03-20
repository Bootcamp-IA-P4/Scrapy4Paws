import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.config.settings import SessionLocal
from api.models.base import Base
from api.models.database import User, Animal, Shelter
from api.scrapers.web.nuevavida_scraper import NuevaVidaScraper

def main():
    # Создаем сессию базы данных
    db = SessionLocal()
    try:
        # Создаем экземпляр скрапера
        scraper = NuevaVidaScraper()
        
        # Запускаем скрапинг
        animals, shelter_info = scraper.run()
        
        if not animals:
            print("No animals found!")
            return
            
        print(f"Found {len(animals)} animals")
        
        # Создаем или получаем приют
        shelter = db.query(Shelter).filter(Shelter.name == shelter_info["name"]).first()
        if not shelter:
            shelter = Shelter(
                name=shelter_info["name"],
                address=shelter_info["address"],
                description=shelter_info["description"],
                website=shelter_info.get("website", "")
            )
            db.add(shelter)
            db.commit()
            db.refresh(shelter)
        
        # Сохраняем животных
        for animal_data in animals:
            # Проверяем, существует ли уже животное
            existing_animal = db.query(Animal).filter(
                Animal.source_url == animal_data["source_url"]
            ).first()
            
            if existing_animal:
                print(f"Animal {animal_data['name']} already exists, skipping...")
                continue
                
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
            db.add(animal)
            print(f"Added new animal: {animal_data['name']}")
        
        # Сохраняем изменения
        db.commit()
        print("Data successfully saved to database")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main() 