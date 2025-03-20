# 🐾 Scrapy4Paws 🐾

## 🎯 Description
Scrapy4Paws is a web application for finding and adopting animals(cats) from shelters. The application collects data about cats from various shelter websites and provides a convenient interface for viewing and adopting them.

## 🛠 Technologies
- Python 
- SQLAlchemy
- Alembic
- PostgreSQL
- Docker
- BeautifulSoup4
- Pydantic
- Python-dotenv

## 📋 Requirements
- Docker
- Docker Compose

## 🚀 Installation and Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/scrapy4paws.git
cd scrapy4paws
```

2. Create a `.env` file in the project root:
```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=scrapy4paws
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/scrapy4paws
```

3. Run the application using Docker Compose:
```bash
docker-compose -f docker/docker-compose.yml up --build
```

## 📁 Project Structure
```
scrapy4paws/
├── api/
│   ├── models/
│   │   ├── base.py
│   │   └── database.py
│   ├── scrapers/
│   │   └── web/
│   │       └── nuevavida_scraper.py
│   └── config/
│       └── database.py
├── alembic/
│   ├── versions/
│   │   └── initial_migration.py
│   └── env.py
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── scripts/
│   └── run_scraper.py
├── .env
├── .gitignore
├── alembic.ini
├── requirements.txt
└── README.md
```

## 🗄 Database
The project uses PostgreSQL with the following main tables:

### Users
- id (PK)
- username (unique, indexed)
- email (unique, indexed)
- city (indexed)
- password
- is_admin
- created_at
- updated_at

### Animals
- id (PK)
- name
- gender
- age
- birth_date
- description
- image_url
- source_url
- is_adopted
- shelter_id (FK)
- created_at

### Shelters
- id (PK)
- name
- address
- website
- description
- created_at

### Adoption Requests
- id (PK)
- animal_id (FK)
- user_id (FK)
- status
- request_date

## 🔄 Scraping
The application collects data about animals from [Nueva Vida](https://adoptargatosmadrid-nuevavida.org/). The scraper extracts:
- Basic information (name, gender, age)
- Detailed description
- Birth date
- Image URL
- Animal page URL

## 🔒 Security
Currently implemented:
- Environment variables for database configuration
- Basic database schema with proper relationships and constraints


