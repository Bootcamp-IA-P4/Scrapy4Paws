import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Tuple
from abc import ABC, abstractmethod
from time import time, sleep
import logging

class BaseBeautifulSoupScraper(ABC):
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        self.session = requests.Session()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def get_page(self, url: str) -> str:
        """Получает HTML-страницу / Gets HTML page"""
        max_retries = 3
        retry_delay = 2  # секунды / seconds

        for attempt in range(max_retries):
            try:
                self.logger.info(f"Fetching {url} (attempt {attempt + 1}/{max_retries})")
                response = self.session.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                
                # Добавляем небольшую задержку между запросами / Add a small delay between requests
                sleep(retry_delay)
                return response.text
                
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Error fetching {url} (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    sleep(retry_delay * (attempt + 1))  # Увеличиваем задержку с каждой попыткой / Increase delay with each attempt
                else:
                    self.logger.error(f"Failed to fetch {url} after {max_retries} attempts")
                    return ""

    @abstractmethod
    def extract_animals(self) -> List[Dict[str, Any]]:
        """Извлекает информацию о животных / Extracts information about animals"""
        pass

    def extract_shelter_info(self) -> Dict[str, str]:
        """Извлекает информацию о приюте / Extracts shelter information"""
        return {
            "name": "Unknown Shelter",
            "address": "Unknown",
            "description": "No description available",
            "website": self.base_url
        }

    def run(self) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
        """Запускает скрапер и возвращает извлеченные данные / Runs scraper and returns extracted data"""
        animals = self.extract_animals()
        shelter_info = self.extract_shelter_info()
        return animals, shelter_info 