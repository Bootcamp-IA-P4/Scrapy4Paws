# 🐾 Scrapy4Paws 🐾

Project for collecting and analyzing animal data from various websites using Selenium and BeautifulSoup4 for web scraping.

## Project Structure

```
project/
  ├── docker/              # Docker configurations
  ├── api/                 # API application
  │   ├── models/         # Data models
  │   ├── scrapers/       # Scrapy spiders
  │   └── config/         # Configuration files
  ├── scripts/            # Helper scripts
  ├── alembic/            # Database migrations
  ├── requirements.txt    # Project dependencies
  └── .env               # Environment variables
```

## Installation and Running

1. Clone the repository
2. Create .env file based on .env.example
3. Run the project using Docker:
   ```bash
   docker-compose up -d
   ```

## Development

- Python 3.9+
- PostgreSQL
- Docker
- Selenium
- BeautifulSoup4 