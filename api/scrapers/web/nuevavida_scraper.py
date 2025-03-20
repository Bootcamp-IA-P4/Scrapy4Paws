from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from ..base_beautifulsoup_scraper import BaseBeautifulSoupScraper
from time import sleep
import requests
from datetime import datetime
import re

class NuevavidaScraper(BaseBeautifulSoupScraper):
    """Scraper for Nuevavida website / Скрапер для сайта Nuevavida"""
    
    def __init__(self):
        """Initialize the scraper / Инициализация скрапера"""
        super().__init__("https://nuevavida.org/product-category/gatos/")
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def get_page(self, url: str) -> Optional[str]:
        """Get page content with proper encoding handling / Получение содержимого страницы с правильной обработкой кодировки"""
        try:
            print(f"\nAttempting to fetch page: {url}")
            response = requests.get(url, headers=self.headers, timeout=30)
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                # Handle encoding / Обработка кодировки
                if 'content-type' in response.headers:
                    content_type = response.headers['content-type'].lower()
                    if 'charset=' in content_type:
                        charset = content_type.split('charset=')[-1]
                        print(f"Detected charset from headers: {charset}")
                        response.encoding = charset
                    else:
                        response.encoding = 'utf-8'
                        print("Using UTF-8 encoding")
                
                print("Successfully retrieved HTML")
                return response.text
            else:
                print(f"Error fetching page. Status: {response.status_code}")
                print(f"Response text: {response.text[:500]}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Request error: {str(e)}")
            return None
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return None

    def extract_basic_info(self, card: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """Extract basic information from a cat card / Извлечение базовой информации из карточки кота"""
        try:
            # Extract name / Извлечение имени
            name_element = card.select_one('h2.woocommerce-loop-product__title')
            if not name_element:
                print("Name element not found")
                return None
            name = name_element.text.strip()
            
            # Extract gender from name / Извлечение пола из имени
            gender = "unknown"
            if name.lower().startswith(("macho", "macho ")):
                gender = "male"
                name = name[6:].strip()  # Remove "MACHO " prefix / Удаление префикса "MACHO "
            elif name.lower().startswith(("hembra", "hembra ")):
                gender = "female"
                name = name[7:].strip()  # Remove "HEMBRA " prefix / Удаление префикса "HEMBRA "
                
            # Extract age / Извлечение возраста
            age = "unknown"
            age_text = name.lower()
            if "cachorro" in age_text or "cachorrito" in age_text:
                age = "kitten"
            elif "adulto" in age_text:
                age = "adult"
            elif "senior" in age_text:
                age = "senior"
                
            # Extract source URL / Извлечение исходного URL
            source_url = card.select_one('a.woocommerce-LoopProduct-link')['href']
            
            print(f"\nExtracted basic info for: {name}")
            print(f"Gender: {gender}, Age: {age}")
            
            return {
                "name": name,
                "gender": gender,
                "age": age,
                "source_url": source_url
            }
            
        except Exception as e:
            print(f"Error extracting basic info: {str(e)}")
            return None

    def parse_birth_date(self, date_str: str) -> datetime:
        """Конвертирует строковую дату в объект datetime"""
        try:
            # Предполагаем формат даты DD/MM/YYYY
            return datetime.strptime(date_str, "%d/%m/%Y")
        except ValueError:
            return None

    def extract_detailed_info(self, url: str) -> Dict[str, Any]:
        """Extract detailed information from cat's page / Извлечение детальной информации со страницы кота"""
        try:
            html = self.get_page(url)
           
            if not html:
                return {}
                
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract description / Извлечение описания
            description = ""
            main_container = soup.select_one('.elementor-element-7a01d681 .elementor-widget-container')
            
            if main_container:
                # Get all text elements / Получение всех текстовых элементов
                text_elements = []
                for element in main_container.stripped_strings:
                    text = element.strip()
                    # Skip empty strings, emails, birth dates and short texts / Пропускаем пустые строки, email, даты рождения и короткие тексты
                    if (text and 
                        not '@' in text and 
                        not 'nacimiento' in text.lower() and 
                        len(text) > 10):
                        text_elements.append(text)
                
                if text_elements:
                    description = ' '.join(text_elements)
                    
            # Remove three-letter tags at the end / Удаление трехбуквенных тегов в конце
            if description:
                words = description.split()
                if words and len(words[-1]) == 3:
                    description = ' '.join(words[:-1])
                    
            # Extract birth date / Извлечение даты рождения
            birth_date = None
            try:
                # Try to find birth date in special element / Пробуем найти дату рождения в специальном элементе
                birth_date_element = soup.select_one('.elementor-element-7a01d681 .elementor-widget-container')
                if birth_date_element:
                    birth_date_text = birth_date_element.get_text()
                    if 'nacimiento' in birth_date_text.lower():
                        birth_date = birth_date_text.split('nacimiento')[-1].strip()
            except Exception as e:
                print(f"Error extracting birth date from special element: {str(e)}")
                
            if not birth_date:
                try:
                    # Try to find birth date in general page text / Пробуем найти дату рождения в общем тексте страницы
                    page_text = soup.get_text()
                    if 'nacimiento' in page_text.lower():
                        birth_date = page_text.split('nacimiento')[-1].split('\n')[0].strip()
                except Exception as e:
                    print(f"Error extracting birth date from page text: {str(e)}")
                    
            print(f"Extracted detailed info: birth_date={birth_date}")
            
            return {
                "description": description,
                "birth_date": birth_date
            }
            
        except Exception as e:
            print(f"Error extracting detailed info: {str(e)}")
            return {}

    def extract_animals(self) -> List[Dict[str, Any]]:
        """Extract information about cats using BeautifulSoup / Извлечение информации о котах с помощью BeautifulSoup"""
        animals = []
        html = self.get_page(self.base_url)
        
        if not html:
            print("Could not get HTML page")
            return animals
            
        print(f"\nRetrieved HTML length: {len(html)}")
        
        soup = BeautifulSoup(html, 'html.parser')
        try:
            # Find all cat cards / Поиск всех карточек котов
            cat_cards = soup.select('li.product.type-product')
            print(f"\nFound cat cards: {len(cat_cards)}")
            
            # Process cards / Обработка карточек
            for card in cat_cards:
                try:
                    # Extract basic information / Извлечение базовой информации
                    basic_info = self.extract_basic_info(card)
                    if not basic_info:
                        continue
                    
                    # Extract detailed information / Извлечение детальной информации
                    detailed_info = self.extract_detailed_info(basic_info['source_url'])
                    print("detailed_info", detailed_info)

                    # Combine information / Объединение информации
                    animal_data = {
                        **basic_info,
                        **detailed_info,
                        "is_adopted": False
                    }
                    
                    animals.append(animal_data)
                    print(f"Successfully extracted all data for: {basic_info['name']}")
                    
                    # Add small delay between requests / Добавление небольшой задержки между запросами
                    sleep(1)
                    
                except Exception as e:
                    print(f"Error processing card: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"Error in extract_animals: {str(e)}")
            
        return animals

    def run(self) -> tuple[List[Dict[str, Any]], Dict[str, str]]:
        
        animals = self.extract_animals()
        shelter_info = {
            "name": "NUEVAVIDA Adopciones",
            "address": "Apartado de correos, 58 - 28220 Majadahonda, Madrid",
            "description": "NUEVAVIDA Adopciones es una asociación sin ánimo de lucro que se dedica a la protección y adopción de gatos."
        }
        return animals, shelter_info 