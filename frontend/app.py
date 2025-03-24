import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Конфигурация API
API_URL = os.getenv('API_URL', 'http://api:8000')

# Функция для получения данных с API
def get_animals(filters=None):
    try:
        url = f"{API_URL}/api/animals"
        response = requests.get(url, params=filters)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"Ошибка при получении данных: {str(e)}")
        return []
    except Exception as e:
        st.error(f"Неожиданная ошибка: {str(e)}")
        return []

# Функция для обновления статуса животного
def update_animal_status(animal_id, is_adopted):
    try:
        response = requests.put(
            f"{API_URL}/api/animals/{animal_id}",
            json={"is_adopted": is_adopted}
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Ошибка при обновлении статуса: {str(e)}")
        return False

# Конфигурация страницы
st.set_page_config(
    page_title="Scrapy4Paws - Refugio de Animales",
    page_icon="🐾",
    layout="wide"
)

# Encabezado de la aplicación
st.title("🐾 Scrapy4Paws - Refugio de Animales")

# Создаем боковую панель для фильтров
with st.sidebar:
    st.header("Filtros")
    
    # Filtro por género
    gender_filter = st.selectbox(
        "Género",
        ["Todos", "Macho", "Hembra", "Desconocido"]
    )
    
    # Filtro por edad
    age_filter = st.selectbox(
        "Edad",
        ["Todos", "Cachorro", "Adulto", "Senior", "Desconocido"]
    )
    
    # Filtro por estado de adopción
    adoption_filter = st.selectbox(
        "Estado de Adopción",
        ["Todos", "Disponible", "Adoptado"]
    )

# Подготавливаем фильтры для API
filters = {}
if gender_filter != "Todos":
    gender_map = {
        "Macho": "male",
        "Hembra": "female",
        "Desconocido": "unknown"
    }
    filters["gender"] = gender_map[gender_filter]

if age_filter != "Todos":
    age_map = {
        "Cachorro": "kitten",
        "Adulto": "adult",
        "Senior": "senior",
        "Desconocido": "unknown"
    }
    filters["age"] = age_map[age_filter]

if adoption_filter != "Todos":
    filters["is_adopted"] = adoption_filter == "Adoptado"

# Получаем данные через API
animals = get_animals(filters)

# Отображаем карточки животных
for animal in animals:
    with st.container():
        col1, col2 = st.columns([1, 2])
        
        with col1:
            if animal.get('image_url'):
                st.image(animal['image_url'], use_column_width=True)
            else:
                st.image("https://via.placeholder.com/300x200?text=Sin+Imagen", use_column_width=True)
        
        with col2:
            st.subheader(animal['name'])
            
            # Информация о животном
            info_col1, info_col2 = st.columns(2)
            
            with info_col1:
                st.write(f"**Género:** {animal.get('gender', 'Desconocido')}")
            with info_col2:
                st.write(f"**Edad:** {animal.get('age', 'Desconocido')}")
            
            # Статус усыновления
            adoption_status = "Adoptado" if animal.get('is_adopted', False) else "Disponible"
            st.write(f"**Estado:** {adoption_status}")
            
            # Описание
            if animal.get('description'):
                st.write("**Descripción:**")
                st.write(animal['description'])
            
            # Кнопка усыновления
            if not animal.get('is_adopted', False):
                if st.button("Adoptar", key=f"adopt_{animal['id']}"):
                    if update_animal_status(animal['id'], True):
                        st.success(f"¡Gracias por adoptar a {animal['name']}!")
                        st.experimental_rerun()
        
        st.markdown("---") 