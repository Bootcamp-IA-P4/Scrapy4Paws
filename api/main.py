from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from models.database import Animal
from schemas import AnimalBase
from config.settings import Base, engine, get_db

# Создаем FastAPI приложение
app = FastAPI(
    title="Scrapy4Paws API",
    description="API для получения информации о животных",
    version="1.0.0"
)

# Создаем таблицы
print("\nCreating database tables...")
Base.metadata.create_all(bind=engine)
print("Database tables created successfully")

@app.get("/animals/", response_model=List[AnimalBase])
async def get_animals(db: Session = Depends(get_db)):
    """
    Получить список всех животных из базы данных
    """
    print("\nFetching animals from database...")
    animals = db.query(Animal).all()
    print(f"Found {len(animals)} animals in database")
    for animal in animals:
        print(f"Animal: {animal.name}, ID: {animal.id}, Shelter ID: {animal.shelter_id}")
    return animals 