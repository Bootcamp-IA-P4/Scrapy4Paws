# 🐾 Scrapy4Paws 🐾

A web scraping application that collects information about animals available for adoption from shelters. Built with FastAPI, PostgreSQL, and Streamlit. The project is designed with extensibility in mind, allowing for easy addition of more shelters in the future.

## 🌟 Features

- Automated scraping of cat adoption information 
- RESTful API for accessing the collected data
- Interactive web interface built with Streamlit
- PostgreSQL database for data storage
- Docker containerization for easy deployment
- Alembic migrations for database management
- Modular scraper architecture for easy integration of new shelters

## 🛠️ Tech Stack

- **Backend**: FastAPI, SQLAlchemy
- **Frontend**: Streamlit
- **Database**: PostgreSQL
- **Scraping**: BeautifulSoup4
- **Containerization**: Docker, Docker Compose
- **Database Migrations**: Alembic

## 🚀 Getting Started

### Prerequisites

- Docker
- Docker Compose

### Installation

1. Clone the repository:
```bash
git clone https://github.com/MarynaDRST/Scrapy4Paws.git
cd scrapy4paws
```

2. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

3. Update the `.env` file with your database credentials and other settings.

4. Build and start the containers:
```bash
docker-compose up -d
```

The application will be available at:
- Frontend: http://localhost:8501
- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 📁 Project Structure

```
scrapy4paws/
├── api/
│   ├── config/         # Configuration files
│   ├── models/         # Database models
│   ├── schemas/        # Pydantic schemas
│   ├── scripts/        # Utility scripts
│   └── scrapers/       # Web scrapers
│   └── alembic/        # Database migrations
├── frontend/           # Streamlit frontend
├── docker-compose.yml
└── README.md
```

## 🔄 Database Migrations

To apply database migrations:
```bash
docker-compose exec api alembic upgrade head
```

To create a new migration:
```bash
docker-compose exec api alembic revision --autogenerate -m "description"
```

## 🐱 Available Endpoints

- `GET /api/animals` - Get all animals
- `GET /api/animals/{id}` - Get animal by ID
- `PUT /api/animals/{id}` - Update animal information

## 🔍 Scraping

The application automatically scrapes data from Nuevavida shelter website. The scraper runs when the application starts and collects:
- Animal names
- Ages
- Genders
- Descriptions
- Images
- Shelter information

> ⚠️ **Important Note**: The website's domain was changed on March 23rd, 2024, requiring project adaptation. If scraping fails, please check:
> - Website URL accessibility
> - Website structure and selectors (they may have changed)
> - Website's robots.txt and scraping policies




