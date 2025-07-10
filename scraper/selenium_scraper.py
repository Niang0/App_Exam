import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import time

def scraper_multi_pages(nb_pages=5, categorie="Appartements à louer"):
    """
    Scrape multi-pages avec gestion d'erreurs améliorée
    """
    base_urls = {
        "Appartements à louer": "https://www.expat-dakar.com/appartements-a-louer",
        "Appartements meublés": "https://www.expat-dakar.com/appartements-meubles?page=",
        "Terrains à vendre": "https://www.expat-dakar.com/terrains-a-vendre?page="
    }

    url_base = base_urls.get(categorie)
    if not url_base:
        raise ValueError(f"Catégorie inconnue : {categorie}. Catégories disponibles : {list(base_urls.keys())}")

    # Configuration Chrome optimisée
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # Liste pour stocker les données
    data = []
    driver = None
    try:
        # Initialisation du driver avec gestion d'erreur
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except WebDriverException as e:
            raise Exception(f"Impossible d'initialiser le navigateur Chrome : {str(e)}")

        print(f"Début du scraping pour {categorie} sur {nb_pages} pages...")

        for page in range(1, nb_pages + 1):
            url = f"{url_base}{page}"
            print(f"Scraping page {page}/{nb_pages}: {url}")
            
            try:
                driver.get(url)
                time.sleep(2)  # Attente plus longue pour la stabilité

                # Attendre que les éléments se chargent
                containers = WebDriverWait(driver, 15).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[class='listings-cards__list-item ']"))
                )

                print(f"Trouvé {len(containers)} annonces sur la page {page}")

                for i, container in enumerate(containers):
                    try:
                        # Extraction des données avec gestion d'erreur individuelle
                        details = None
                        try:
                            details = container.find_element(By.CSS_SELECTOR, ".listing-card__header__title").text.strip()
                        except NoSuchElementException:
                            print(f"Titre manquant pour l'annonce {i+1}")

                        adresse = None
                        try:
                            adresse = container.find_element(By.CSS_SELECTOR, ".listing-card__header__location").text.strip()
                        except NoSuchElementException:
                            print(f"Adresse manquante pour l'annonce {i+1}")

                        # Extraction des tags (chambres, superficie)
                        chambres = None
                        superficie = None
                        try:
                            tags_container = container.find_element(By.CSS_SELECTOR, '.listing-card__header__tags')
                            span_tags = tags_container.find_elements(By.CSS_SELECTOR, 'span.listing-card__header__tags__item')
                            
                            if len(span_tags) > 0:
                                chambres = span_tags[0].text.strip()
                            if len(span_tags) > 1:
                                superficie = span_tags[1].text.strip()
                        except NoSuchElementException:
                            print(f"Tags manquants pour l'annonce {i+1}")

                        # Prix
                        prix = None
                        try:
                            prix = container.find_element(By.CSS_SELECTOR, ".listing-card__info-bar").text.strip()
                        except NoSuchElementException:
                            print(f"Prix manquant pour l'annonce {i+1}")

                        # Image
                        image_link = None
                        try:
                            image = container.find_element(By.CSS_SELECTOR, ".listing-card__image__resource")
                            image_link = image.get_attribute("src")
                        except NoSuchElementException:
                            print(f"Image manquante pour l'annonce {i+1}")

                        # N'ajouter que si au moins le titre ou l'adresse existe
                        if details or adresse:
                            data.append({
                                "categorie": categorie,
                                "details": details,
                                "adresse": adresse,
                                "chambres": chambres,
                                "superficie": superficie,
                                "prix": prix,
                                "image_lien": image_link
                            })

                    except Exception as e:
                        print(f"Erreur lors du traitement de l'annonce {i+1} sur la page {page}: {str(e)}")
                        continue

            except TimeoutException:
                print(f"Timeout sur la page {page} - passage à la suivante")
                continue
            except Exception as e:
                print(f"Erreur sur la page {page}: {str(e)}")
                continue

    except Exception as e:
        print(f"Erreur générale durant le scraping : {str(e)}")
        raise

    finally:
        if driver:
            driver.quit()

    # Création du DataFrame
    df = pd.DataFrame(data)
    
    if df.empty:
        print("Aucune donnée récupérée")
        return pd.DataFrame()
    
    # Nettoyage des données
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    
    # Assurer que toutes les colonnes existent
    colonnes_requises = ["categorie", "details", "adresse", "chambres", "superficie", "prix", "image_lien"]
    for col in colonnes_requises:
        if col not in df.columns:
            df[col] = None

    print(f"Scraping terminé : {len(df)} annonces récupérées")
    return df