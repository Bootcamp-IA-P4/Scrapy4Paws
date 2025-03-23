from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from ..base_beautifulsoup_scraper import BaseBeautifulSoupScraper
from time import sleep
import requests
from datetime import datetime
import re

class NuevaVidaScraper(BaseBeautifulSoupScraper):
    """Scraper for Nuevavida website / Скрапер для сайта Nuevavida"""
    
    def __init__(self):
        """Initialize the scraper / Инициализация скрапера"""
        super().__init__("https://adoptargatosmadrid-nuevavida.org/gatos-en-adopcion/")
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def get_page(self, url: str) -> Optional[str]:
        """Get page content with proper encoding handling / Получение содержимого страницы с правильной обработкой кодировки"""
        try:
            print(f"\nAttempting to fetch page: {url}")
            print(f"Using headers: {self.headers}")
            response = requests.get(url, headers=self.headers, timeout=30)
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
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
                print(f"HTML preview: {response.text[:500]}")
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
            name_element = card.find('h2', class_='woocommerce-loop-product__title')
            if not name_element:
                print("Name element not found")
                return None
            name = name_element.text.strip()
            
            # Extract gender from URL / Извлечение пола из URL
            gender = "unknown"
            url_element = card.find('a', class_='woocommerce-LoopProduct-link')
            if url_element and 'href' in url_element.attrs:
                url = url_element['href']
                if '/macho/' in url.lower():
                    gender = "male"
                elif '/hembra/' in url.lower():
                    gender = "female"
                
            # Extract age / Извлечение возраста
            age = "unknown"
            description = card.select_one('.entry-content')
            if description:
                age_text = description.text.lower()
                if "cachorro" in age_text or "cachorrito" in age_text:
                    age = "kitten"
                elif "adulto" in age_text:
                    age = "adult"
                elif "senior" in age_text:
                    age = "senior"
                
            # Extract source URL / Извлечение исходного URL
            source_url = url_element['href'] if url_element and 'href' in url_element.attrs else None
            if not source_url:
                print("Source URL not found")
                return None
            
            # Extract image URL / Извлечение URL изображения
            image_url = None
            img_element = card.find('img', class_='attachment-woocommerce_thumbnail')
            if img_element and 'src' in img_element.attrs:
                image_url = img_element['src']
            
            print(f"\nExtracted basic info for: {name}")
            print(f"Gender: {gender}, Age: {age}")
            print(f"Image URL: {image_url}")
            print(f"Source URL: {source_url}")
            
            return {
                "name": name,
                "gender": gender,
                "age": age,
                "source_url": source_url,
                "image_url": image_url
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
            description_element = soup.select_one('.elementor-widget-theme-post-excerpt .elementor-widget-container')
            if description_element:
                description = description_element.text.strip()
            
            # Extract gender / Извлечение пола
            gender = "unknown"
            gender_element = soup.select_one('.elementor-widget-text-editor:contains("Sexo:")')
            if gender_element:
                gender_text = gender_element.text.strip().lower()
                if "macho" in gender_text:
                    gender = "male"
                elif "hembra" in gender_text:
                    gender = "female"
                    
            # Extract birth date / Извлечение даты рождения
            birth_date = None
            try:
                birth_date_element = soup.select_one('.elementor-widget-text-editor:contains("Fecha de nacimiento")')
                if birth_date_element:
                    birth_date_text = birth_date_element.text.strip()
                    if ':' in birth_date_text:
                        birth_date_str = birth_date_text.split(':')[1].strip()
                        # Remove any extra characters and clean the date string
                        birth_date_str = re.sub(r'[^\d/]', '', birth_date_str)
                        if birth_date_str:
                            try:
                                # Parse the date string
                                birth_date = datetime.strptime(birth_date_str, "%d/%m/%Y")
                            except ValueError:
                                print(f"Could not parse birth date: {birth_date_str}")
            except Exception as e:
                print(f"Error extracting birth date: {str(e)}")
                    
            print(f"Extracted detailed info:")
            print(f"Description: {description[:100]}...")
            print(f"Gender: {gender}")
            print(f"Birth date: {birth_date}")
            
            return {
                "description": description,
                "birth_date": birth_date,
                "gender": gender  # Обновляем пол из детальной информации
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
            cat_cards = soup.select('li.product')
            print(f"\nFound cat cards: {len(cat_cards)}")
            
            # Process cards / Обработка карточек
            for card in cat_cards:
                try:
                    print("\nProcessing new cat card...")
                    # Extract basic information / Извлечение базовой информации
                    basic_info = self.extract_basic_info(card)
                    if not basic_info:
                        print("Failed to extract basic info")
                        continue
                    
                    print(f"Basic info extracted: {basic_info}")
                    
                    # Extract detailed information / Извлечение детальной информации
                    detailed_info = self.extract_detailed_info(basic_info['source_url'])
                    print(f"Detailed info extracted: {detailed_info}")

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
            
        print(f"\nTotal animals extracted: {len(animals)}")
        return animals

    def run(self) -> tuple[List[Dict[str, Any]], Dict[str, str]]:
        
        animals = self.extract_animals()
        shelter_info = {
            "name": "NUEVAVIDA Adopciones",
            "address": "Apartado de correos, 58 - 28220 Majadahonda, Madrid",
            "description": "NUEVAVIDA Adopciones es una asociación sin ánimo de lucro que se dedica a la protección y adopción de gatos."
        }
        return animals, shelter_info 