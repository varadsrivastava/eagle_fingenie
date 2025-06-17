import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from PIL import Image
from io import BytesIO
import pytesseract
import logging
from typing import Dict, List
import chromadb
from chromadb.utils import embedding_functions

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class BarclayScraper:
    """Scrapes Barclays website to extract content and structure"""
    
    def __init__(self):
        self.base_url = "https://www.barclays.co.uk"
        self.visited = set()
        self.docs_paths = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path="F:/xx/xx/fingenie/data/chromadb")
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-mpnet-base-v2"
        )
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="barclays_uk_products",
            embedding_function=self.embedding_function
        )

    def extract_text_from_image(self, img_url: str) -> str:
        """Extract text from images using OCR"""
        try:
            response = requests.get(img_url, headers=self.headers)
            img = Image.open(BytesIO(response.content))
            return pytesseract.image_to_string(img)
        except Exception as e:
            logging.warning(f"Failed to extract text from image {img_url}: {e}")
            return ""

    def scrape_page(self, url: str, depth: int = 0) -> Dict[str, str]:
        """Scrape content from a page and its images"""
        if depth > 2 or url in self.visited:  # Limit depth to avoid infinite recursion
            return {}
        
        self.visited.add(url)
        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove navigation, footer and other unwanted elements
            for element in soup.find_all(['footer', 'nav', 'header']):
                element.decompose()
            
            # Remove elements with specific classes/IDs that contain footer/nav content
            unwanted_selectors = [
                'footer', '.footer', '#footer', 
                'nav', '.navigation', '#navigation',
                '.site-info', '.legal-info', '.copyright',
                '.menu', '.site-header'
            ]
            for selector in unwanted_selectors:
                for element in soup.select(selector):
                    element.decompose()
            
            # Extract text content from remaining elements
            text_content = ' '.join([p.get_text() for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'li'])])
            
            # Remove common footer text patterns
            footer_patterns = [
                "Barclays Bank UK PLC and Barclays Bank PLC are each authorised",
                "Protecting Your Money",
                "Important information",
                "Privacy policy",
                "Cookies policy",
                "Security",
                "Find us",
                "Help & FAQs"
            ]
            for pattern in footer_patterns:
                text_content = text_content.replace(pattern, '')
            
            # Extract and process images
            image_content = []
            for img in soup.find_all('img'):
                img_url = urljoin(url, img.get('src', ''))
                if img_url.endswith(('.jpg', '.png', '.jpeg')):
                    img_text = self.extract_text_from_image(img_url)
                    if img_text:
                        image_content.append(img_text)
            
            content = {
                'url': url,
                'text_content': text_content.strip(),
                'image_content': ' '.join(image_content)
            }
            
            # Add to ChromaDB
            if text_content or image_content:
                full_content = text_content + " " + ' '.join(image_content)
                self.collection.upsert(
                    documents=[full_content],
                    metadatas=[{"url": url}],
                    ids=[url]
                )
            
            # Extract links for further scraping
            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href']
                if href.startswith('/'):
                    full_url = urljoin(self.base_url, href)
                    if full_url not in self.visited: #and self.is_relevant_path(href):
                        self.docs_paths.append(href.lstrip('/'))
                        self.scrape_page(full_url, depth + 1)
            
            return content
            
        except Exception as e:
            logging.error(f"Failed to scrape {url}: {e}")
            return {}

    def is_relevant_path(self, path: str) -> bool:
        """Check if the path is relevant for financial products"""
        relevant_keywords = [
            'account', 'banking', 'savings', 'mortgage', 'loan', 'invest',
            'insurance', 'credit', 'debit', 'premium', 'wealth', 'business', 'card', 'eligibility',
            'travel', 'tech', 'investment', 'retirement'
        ]
        return any(keyword in path.lower() for keyword in relevant_keywords)

    def get_site_structure(self) -> List[str]:
        """Get the structure of relevant pages"""
        self.scrape_page(self.base_url)
        return list(set(self.docs_paths))  # Remove duplicates

def initialize_database():
    """Initialize and populate the ChromaDB database"""
    scraper = BarclayScraper()
    docs_paths = scraper.get_site_structure()
    return scraper.client, docs_paths

if __name__ == "__main__":
    # Initialize database and get paths UNCOMMENT THIS TO RUN AND UPDATE THE DATABASE
    client, paths = initialize_database()
    print(f"Scraped and indexed {len(paths)} pages")
    print("Sample paths:", paths[:5])

    # print sample content of the database
    client = chromadb.PersistentClient(path="F:/xx/xx/fingenie/data/chromadb")
    collection = client.get_or_create_collection(name="barclays_uk_products", 
            embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-mpnet-base-v2")
    )
    results = collection.query(
    query_texts=["tell me about retirement and travel products"], # Chroma will embed this for you
    n_results=2 # how many results to return
    )

    # print(results)
