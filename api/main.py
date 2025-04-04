from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime
from pydantic import BaseModel
import logging
import sys

# Настройка логирования для Docker
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

# Создание FastAPI приложения
app = FastAPI(
    title="Scrapy4Paws API",
    description="API для доступа к данным о животных",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене нужно будет указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic модели для ответа и обновления
class AnimalResponse(BaseModel):
    id: int
    name: str
    age: str
    gender: str
    description: str
    birth_date: datetime
    image_url: str
    source_url: str
    shelter_id: int
    is_adopted: bool

class AnimalUpdate(BaseModel):
    is_adopted: bool

# Функция для подключения к базе данных
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'db'),
        database=os.getenv('POSTGRES_DB', 'scrapy4paws'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', 'postgres'),
        port=os.getenv('POSTGRES_PORT', '5432')
    )

# Модели данных
class Animal:
    def __init__(self, id: int, name: str, age: str, gender: str, 
                 description: str, birth_date: datetime, image_url: str, 
                 source_url: str, shelter_id: int, is_adopted: bool = False):
        self.id = id
        self.name = name
        self.age = age
        self.gender = gender
        self.description = description
        self.birth_date = birth_date
        self.image_url = image_url
        self.source_url = source_url
        self.shelter_id = shelter_id
        self.is_adopted = is_adopted

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "description": self.description,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "image_url": self.image_url,
            "source_url": self.source_url,
            "shelter_id": self.shelter_id,
            "is_adopted": self.is_adopted
        }

# Эндпоинты
@app.get("/")
async def root():
    """Корневой эндпоинт для проверки работоспособности API"""
    return {"message": "Scrapy4Paws API is running"}

@app.get("/api/animals", response_model=List[AnimalResponse])
async def get_animals(
    age: Optional[str] = None,
    gender: Optional[str] = None,
    shelter_id: Optional[int] = None,
    is_adopted: Optional[bool] = None
):
    """
    Получение списка животных с возможностью фильтрации
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Базовый SQL запрос
        query = """
            SELECT id, name, age, gender, description, birth_date, 
                   image_url, source_url, shelter_id, is_adopted
            FROM animals 
            WHERE 1=1
        """
        params = []
        
        # Добавляем фильтры
        if age:
            query += " AND age = %s"
            params.append(age)
            logger.info(f"Adding age filter: {age}")
        if gender:
            query += " AND gender = %s"
            params.append(gender)
            logger.info(f"Adding gender filter: {gender}")
        if shelter_id:
            query += " AND shelter_id = %s"
            params.append(shelter_id)
            logger.info(f"Adding shelter_id filter: {shelter_id}")
        if is_adopted is not None:
            query += " AND is_adopted = %s"
            params.append(is_adopted)
            logger.info(f"Adding is_adopted filter: {is_adopted}")
            
        logger.info(f"Executing query: {query}")
        logger.info(f"With parameters: {params}")
        
        # Выполняем запрос
        cur.execute(query, params)
        animals = []
        
        for row in cur.fetchall():
            logger.info(f"Raw data from DB: {row}")
            animal = Animal(*row)
            animal_dict = animal.to_dict()
            logger.info(f"Processed animal data: {animal_dict}")
            animals.append(animal_dict)
            
        logger.info(f"Total animals returned: {len(animals)}")
        return animals
        
    except Exception as e:
        logger.error(f"Error in get_animals: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/api/animals/{animal_id}", response_model=dict)
async def get_animal(animal_id: int):
    """
    Получение информации о конкретном животном по ID
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, name, age, gender, description, birth_date, 
                   image_url, source_url, shelter_id, is_adopted
            FROM animals 
            WHERE id = %s
        """, (animal_id,))
        
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Animal not found")
            
        animal = Animal(*row)
        return animal.to_dict()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.put("/api/animals/{animal_id}")
async def update_animal(animal_id: int, animal_update: AnimalUpdate):
    """
    Обновление статуса усыновления животного
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Проверяем существование животного
        cur.execute("SELECT id FROM animals WHERE id = %s", (animal_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Animal not found")
        
        # Обновляем статус
        cur.execute("""
            UPDATE animals 
            SET is_adopted = %s 
            WHERE id = %s
        """, (animal_update.is_adopted, animal_id))
        
        conn.commit()
        return {"message": "Animal status updated successfully"}
        
    except Exception as e:
        logger.error(f"Error updating animal status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/api/check-table")
async def check_table():
    """
    Проверка структуры таблицы animals
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Получаем информацию о структуре таблицы
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'animals'
        """)
        
        columns = []
        for row in cur.fetchall():
            columns.append({
                "name": row[0],
                "type": row[1]
            })
            
        return {
            "status": "ok",
            "columns": columns
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
    finally:
        cur.close()
        conn.close()

@app.get("/api/check-values")
async def check_values():
    """
    Проверка уникальных значений в базе данных
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Получаем уникальные значения для каждого поля
        cur.execute("SELECT DISTINCT gender FROM animals")
        genders = [row[0] for row in cur.fetchall()]
        
        cur.execute("SELECT DISTINCT age FROM animals")
        ages = [row[0] for row in cur.fetchall()]
        
        return {
            "status": "ok",
            "genders": genders,
            "ages": ages
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 