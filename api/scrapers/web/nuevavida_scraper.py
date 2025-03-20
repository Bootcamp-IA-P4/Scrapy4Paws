from bs4 import BeautifulSoup
from typing import List, Dict, Any
from ..base_beautifulsoup_scraper import BaseBeautifulSoupScraper
from time import sleep
import requests
from datetime import datetime

class NuevaVidaScraper(BaseBeautifulSoupScraper):
    def __init__(self):
        super().__init__("https://adoptargatosmadrid-nuevavida.org/gatos-en-adopcion/")
        # Добавляем больше заголовков для имитации браузера
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }

    def get_page(self, url: str) -> str:
        """Получает HTML страницы с дополнительной обработкой ошибок"""
        try:
            print(f"\nAttempting to fetch page: {url}")
            response = requests.get(url, headers=self.headers, timeout=30)
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                # Пробуем определить кодировку из заголовков
                if 'content-type' in response.headers:
                    content_type = response.headers['content-type'].lower()
                    if 'charset=' in content_type:
                        charset = content_type.split('charset=')[-1]
                        print(f"Detected charset from headers: {charset}")
                        response.encoding = charset
                    else:
                        # Если кодировка не указана, пробуем UTF-8
                        response.encoding = 'utf-8'
                        print("Using UTF-8 encoding")
                else:
                    response.encoding = 'utf-8'
                    print("Using UTF-8 encoding")
                
                print("Successfully retrieved HTML")
                return response.text
            else:
                print(f"Error fetching page. Status: {response.status_code}")
                print(f"Response text: {response.text[:500]}")
                return ""
                
        except requests.exceptions.RequestException as e:
            print(f"Request error: {str(e)}")
            return ""
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return ""

    def extract_basic_info(self, card: BeautifulSoup) -> Dict[str, Any]:
        """Извлекает базовую информацию из карточки животного"""
        try:
            # Извлекаем ссылку и имя
            link_elem = card.select_one('a.woocommerce-LoopProduct-link')
            if not link_elem:
                print("Could not find link on card")
                return {}
                
            link = link_elem.get('href', '')
            name = link_elem.select_one('h2.woocommerce-loop-product__title')
            name = name.text.strip() if name else "Unknown"
            
            # Извлекаем изображение
            img_elem = card.select_one('img.attachment-woocommerce_thumbnail')
            image_url = img_elem.get('src', '') if img_elem else ''
            
            # Извлекаем категории и теги
            classes = card.get('class', [])
            gender = next((c.split('-')[1] for c in classes if c.startswith('product_cat-') and c.split('-')[1] in ['macho', 'hembra']), 'unknown')
            age = next((c.split('-')[1] for c in classes if c.startswith('product_cat-') and c.split('-')[1] in ['cachorro', 'adulto']), 'unknown')
            
            print(f"\nExtracted basic info for: {name}")
            print(f"Gender: {gender}, Age: {age}")
            
            return {
                "name": name,
                "source_url": link,
                "image_url": image_url,
                "gender": gender,
                "age": age
            }
            
        except Exception as e:
            print(f"Error extracting basic info: {str(e)}")
            return {}

    def parse_birth_date(self, date_str: str) -> datetime:
        """Конвертирует строковую дату в объект datetime"""
        try:
            # Предполагаем формат даты DD/MM/YYYY
            return datetime.strptime(date_str, "%d/%m/%Y")
        except ValueError:
            return None

    def extract_detailed_info(self, url: str) -> Dict[str, Any]:
        """Извлекает детальную информацию со страницы животного"""
        try:
            html = self.get_page(url)
           
            if not html:
                return {}
                
            soup = BeautifulSoup(html, 'html.parser')
            
            # Извлекаем описание
            description = ""
            desc_elem = soup.select_one('.elementor-element-7a01d681 .elementor-widget-container div')
            if desc_elem:
                description = desc_elem.get_text().strip()
                print(f"Found description: {description}")
                    
            # Извлекаем дату рождения
            birth_date = None
            birth_elem = soup.select_one('.elementor-element-479e4d06.elementor-widget-text-editor')
            if birth_elem:
                try:
                    birth_text = birth_elem.text.strip()
                    if "Fecha de nacimiento:" in birth_text:
                        date_str = birth_text.replace("Fecha de nacimiento:", "").strip()
                        birth_date = self.parse_birth_date(date_str)
                        print(f"Found birth date: {birth_date}")
                except Exception as e:
                    print(f"Error extracting birth date: {str(e)}")
            
            print(f"Extracted detailed info: birth_date={birth_date}")
            
            return {
                "description": description,
                "birth_date": birth_date
            }
            
        except Exception as e:
            print(f"Error extracting detailed info: {str(e)}")
            return {}

    def extract_animals(self) -> List[Dict[str, Any]]:
        """Извлекает информацию о котах с помощью BeautifulSoup"""
        animals = []
        html = self.get_page(self.base_url)
        
        if not html:
            print("Could not get HTML page")
            return animals
            
        print(f"\nRetrieved HTML length: {len(html)}")
        
        soup = BeautifulSoup(html, 'html.parser')
        try:
            # Ищем все карточки котов
            cat_cards = soup.select('li.product.type-product')
            print(f"\nFound cat cards: {len(cat_cards)}")
            
            # Обрабатываем только первые 2 карточки
            for card in cat_cards[:1]:
                try:
                    # Извлекаем базовую информацию
                    basic_info = self.extract_basic_info(card)
                    if not basic_info:
                        continue
                    
                    # Извлекаем детальную информацию
                    detailed_info = self.extract_detailed_info(basic_info['source_url'])
                    print("detailed_info", detailed_info)

                    # Объединяем информацию
                    animal_data = {
                        **basic_info,
                        **detailed_info,
                        "is_adopted": False
                    }
                    
                    animals.append(animal_data)
                    print(f"Successfully extracted all data for: {basic_info['name']}")
                    
                    # Добавляем небольшую задержку между запросами
                    sleep(1)
                    
                except Exception as e:
                    print(f"Error processing card: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"Error in extract_animals: {str(e)}")
            
        return animals

    def run(self) -> tuple[List[Dict[str, Any]], Dict[str, str]]:
        """Запускает скрапер и возвращает извлеченные данные"""
        animals = self.extract_animals()
        shelter_info = {
            "name": "NUEVAVIDA Adopciones",
            "address": "Apartado de correos, 58 - 28220 Majadahonda, Madrid",
            "description": "NUEVAVIDA Adopciones es una asociación sin ánimo de lucro que se dedica a la protección y adopción de gatos."
        }
        return animals, shelter_info 