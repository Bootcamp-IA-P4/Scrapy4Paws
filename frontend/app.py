import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env raíz
load_dotenv('../.env')

# Configuración de conexión a la base de datos
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        database=os.getenv('POSTGRES_DB', 'scrapy4paws'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', 'postgres'),
        port=os.getenv('POSTGRES_PORT', '5432')
    )

# Configuración de la página
st.set_page_config(
    page_title="Scrapy4Paws - Refugio de Animales",
    page_icon="🐾",
    layout="wide"
)

# Encabezado de la aplicación
st.title("🐾 Scrapy4Paws - Refugio de Animales")

# Crear barra lateral para filtros
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

# Contenido principal
try:
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Formar consulta SQL con filtros
    query = "SELECT * FROM animals WHERE 1=1"
    params = []
    
    if gender_filter != "Todos":
        gender_map = {
            "Macho": "male",
            "Hembra": "female",
            "Desconocido": "unknown"
        }
        query += " AND gender = %s"
        params.append(gender_map[gender_filter])
    
    if age_filter != "Todos":
        age_map = {
            "Cachorro": "kitten",
            "Adulto": "adult",
            "Senior": "senior",
            "Desconocido": "unknown"
        }
        query += " AND age = %s"
        params.append(age_map[age_filter])
    
    if adoption_filter != "Todos":
        is_adopted = adoption_filter == "Adoptado"
        query += " AND is_adopted = %s"
        params.append(is_adopted)
    
    # Ejecutar consulta
    cur.execute(query, params)
    animals = cur.fetchall()
    
    # Mostrar tarjetas de animales
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
                
                # Información del animal
                info_col1, info_col2, info_col3 = st.columns(3)
                
                with info_col1:
                    st.write(f"**Género:** {animal['gender']}")
                with info_col2:
                    st.write(f"**Edad:** {animal['age']}")
                with info_col3:
                    status = "✅ Adoptado" if animal['is_adopted'] else "🆕 Disponible"
                    st.write(f"**Estado:** {status}")
                
                # Descripción
                if animal.get('description'):
                    st.write("**Descripción:**")
                    st.write(animal['description'])
                
                # Botón de adopción
                if not animal['is_adopted']:
                    if st.button("Adoptar", key=f"adopt_{animal['id']}"):
                        # Aquí irá la lógica de adopción
                        st.success(f"¡Gracias por adoptar a {animal['name']}!")
            
            st.markdown("---")

except Exception as e:
    st.error(f"Error de conexión a la base de datos: {str(e)}")
finally:
    if 'cur' in locals():
        cur.close()
    if 'conn' in locals():
        conn.close() 