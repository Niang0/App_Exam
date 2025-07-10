import os
import time
import logging
import platform
from typing import Optional, Dict, Any, List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    WebDriverException, TimeoutException, NoSuchElementException,
    ElementNotInteractableException, StaleElementReferenceException
)
from webdriver_manager.chrome import ChromeDriverManager
import requests
from bs4 import BeautifulSoup


class RobustSeleniumScraper:
    """
    Scraper Selenium robuste avec fallback et gestion d'erreurs complète
    """
    
    def __init__(self, headless: bool = True, timeout: int = 30, 
                 max_retries: int = 3, use_fallback: bool = True):
        """
        Initialise le scraper
        
        Args:
            headless: Mode sans interface graphique
            timeout: Timeout en secondes
            max_retries: Nombre de tentatives max
            use_fallback: Utiliser requests comme fallback
        """
        self.headless = headless
        self.timeout = timeout
        self.max_retries = max_retries
        self.use_fallback = use_fallback
        self.driver = None
        self.setup_logging()
        
    def setup_logging(self):
        """Configure le logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_chrome_options(self) -> Options:
        """Configure les options Chrome optimisées"""
        options = Options()
        
        # Options de base
        if self.headless:
            options.add_argument('--headless')
        
        # Options de sécurité et stabilité
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Options de performance
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--disable-features=TranslateUI')
        options.add_argument('--disable-ipc-flooding-protection')
        
        # User agent réaliste
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Options spécifiques à l'OS
        if platform.system() == "Linux":
            options.add_argument('--disable-setuid-sandbox')
            options.add_argument('--remote-debugging-port=9222')
        
        # Préférences
        prefs = {
            'profile.default_content_setting_values.notifications': 2,
            'profile.default_content_settings.popups': 0,
            'profile.managed_default_content_settings.images': 2,  # Bloquer les images
            'profile.default_content_setting_values.plugins': 1,
            'profile.content_settings.plugin_whitelist.adobe-flash-player': 1,
            'profile.content_settings.exceptions.plugins.*,*.per_resource.adobe-flash-player': 1
        }
        options.add_experimental_option('prefs', prefs)
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        return options
    
    def create_driver(self) -> Optional[webdriver.Chrome]:
        """Crée et configure le driver Chrome"""
        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"Tentative {attempt + 1}/{self.max_retries} de création du driver")
                
                # Nettoyer le cache si nécessaire
                if attempt > 0:
                    self.clean_webdriver_cache()
                
                # Configurer le service
                service = Service(ChromeDriverManager().install())
                options = self.get_chrome_options()
                
                # Créer le driver
                driver = webdriver.Chrome(service=service, options=options)
                
                # Configuration additionnelle
                driver.set_page_load_timeout(self.timeout)
                driver.implicitly_wait(10)
                
                # Masquer l'automation
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
                self.logger.info("Driver créé avec succès")
                return driver
                
            except Exception as e:
                self.logger.error(f"Erreur création driver (tentative {attempt + 1}): {e}")
                if attempt == self.max_retries - 1:
                    self.logger.error("Impossible de créer le driver après toutes les tentatives")
                    return None
                time.sleep(2 ** attempt)  # Backoff exponentiel
        
        return None
    
    def clean_webdriver_cache(self):
        """Nettoie le cache WebDriver"""
        try:
            import shutil
            cache_dir = os.path.expanduser("~/.wdm")
            if os.path.exists(cache_dir):
                shutil.rmtree(cache_dir)
                self.logger.info("Cache WebDriver nettoyé")
        except Exception as e:
            self.logger.warning(f"Impossible de nettoyer le cache: {e}")
    
    def safe_get(self, url: str, wait_element: Optional[str] = None) -> bool:
        """Navigue vers une URL de manière sécurisée"""
        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"Navigation vers {url} (tentative {attempt + 1})")
                
                self.driver.get(url)
                
                # Attendre un élément spécifique si demandé
                if wait_element:
                    WebDriverWait(self.driver, self.timeout).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, wait_element))
                    )
                
                # Vérifier que la page s'est chargée
                WebDriverWait(self.driver, 10).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                
                self.logger.info("Page chargée avec succès")
                return True
                
            except TimeoutException:
                self.logger.error(f"Timeout lors du chargement de {url}")
                if attempt < self.max_retries - 1:
                    time.sleep(2)
                    continue
                return False
                
            except WebDriverException as e:
                self.logger.error(f"Erreur WebDriver: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2)
                    continue
                return False
        
        return False
    
    def safe_find_element(self, by: By, value: str, timeout: int = 10) -> Optional[Any]:
        """Trouve un élément de manière sécurisée"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            self.logger.warning(f"Élément non trouvé: {value}")
            return None
        except Exception as e:
            self.logger.error(f"Erreur lors de la recherche d'élément: {e}")
            return None
    
    def safe_find_elements(self, by: By, value: str, timeout: int = 10) -> List[Any]:
        """Trouve plusieurs éléments de manière sécurisée"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return self.driver.find_elements(by, value)
        except TimeoutException:
            self.logger.warning(f"Éléments non trouvés: {value}")
            return []
        except Exception as e:
            self.logger.error(f"Erreur lors de la recherche d'éléments: {e}")
            return []
    
    def safe_click(self, element, timeout: int = 10) -> bool:
        """Clique sur un élément de manière sécurisée"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(element)
            )
            element.click()
            return True
        except (TimeoutException, ElementNotInteractableException) as e:
            self.logger.warning(f"Impossible de cliquer: {e}")
            try:
                # Tentative avec JavaScript
                self.driver.execute_script("arguments[0].click();", element)
                return True
            except Exception as e2:
                self.logger.error(f"Échec du clic JavaScript: {e2}")
                return False
        except Exception as e:
            self.logger.error(f"Erreur lors du clic: {e}")
            return False
    
    def safe_send_keys(self, element, text: str, clear_first: bool = True) -> bool:
        """Saisit du texte de manière sécurisée"""
        try:
            if clear_first:
                element.clear()
            element.send_keys(text)
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de la saisie: {e}")
            return False
    
    def scroll_to_element(self, element):
        """Fait défiler vers un élément"""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(1)
        except Exception as e:
            self.logger.error(f"Erreur lors du scroll: {e}")
    
    def wait_for_page_load(self, timeout: int = 30):
        """Attend que la page soit complètement chargée"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except TimeoutException:
            self.logger.warning("Timeout lors de l'attente du chargement")
    
    def fallback_scrape(self, url: str) -> Optional[BeautifulSoup]:
        """Scraping avec requests comme fallback"""
        if not self.use_fallback:
            return None
        
        try:
            self.logger.info(f"Fallback scraping pour {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none'
            }
            
            session = requests.Session()
            response = session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            self.logger.info("Fallback scraping réussi")
            return soup
            
        except Exception as e:
            self.logger.error(f"Erreur fallback scraping: {e}")
            return None
    
    def scrape_page(self, url: str, wait_element: Optional[str] = None) -> Dict[str, Any]:
        """
        Scrape une page avec gestion d'erreurs complète
        
        Args:
            url: URL à scraper
            wait_element: Sélecteur CSS d'un élément à attendre
        
        Returns:
            Dict avec les résultats ou les erreurs
        """
        result = {
            'success': False,
            'url': url,
            'data': None,
            'error': None,
            'method': None
        }
        
        # Tentative avec Selenium
        try:
            if not self.driver:
                self.driver = self.create_driver()
            
            if self.driver and self.safe_get(url, wait_element):
                result['success'] = True
                result['data'] = self.driver.page_source
                result['method'] = 'selenium'
                self.logger.info(f"Scraping réussi pour {url}")
                return result
            
        except Exception as e:
            self.logger.error(f"Erreur Selenium pour {url}: {e}")
            result['error'] = str(e)
        
        # Tentative avec fallback
        if self.use_fallback:
            soup = self.fallback_scrape(url)
            if soup:
                result['success'] = True
                result['data'] = str(soup)
                result['method'] = 'requests'
                return result
        
        result['error'] = "Toutes les méthodes de scraping ont échoué"
        return result
    
    def __enter__(self):
        """Support du context manager"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Nettoyage automatique"""
        self.quit()
    
    def quit(self):
        """Ferme le driver proprement"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("Driver fermé")
            except Exception as e:
                self.logger.error(f"Erreur lors de la fermeture: {e}")
            finally:
                self.driver = None


# Exemple d'utilisation
if __name__ == "__main__":
    # Configuration
    scraper = RobustSeleniumScraper(
        headless=True,
        timeout=30,
        max_retries=3,
        use_fallback=True
    )
    
    # Utilisation avec context manager
    with scraper:
        # Scraper une page
        result = scraper.scrape_page("https://example.com")
        
        if result['success']:
            print(f"✅ Scraping réussi avec {result['method']}")
            # Traiter result['data']
        else:
            print(f"❌ Erreur: {result['error']}")
        
        # Exemple avec attente d'élément
        result2 = scraper.scrape_page(
            "https://example.com/dynamic", 
            wait_element=".content"
        )
        
        if result2['success']:
            # Interaction avec la page
            element = scraper.safe_find_element(By.CSS_SELECTOR, ".search-input")
            if element:
                scraper.safe_send_keys(element, "test query")
                
            button = scraper.safe_find_element(By.CSS_SELECTOR, ".search-button")
            if button:
                scraper.safe_click(button)
                
            # Récupérer les résultats
            results = scraper.safe_find_elements(By.CSS_SELECTOR, ".result-item")
            print(f"Trouvé {len(results)} résultats")