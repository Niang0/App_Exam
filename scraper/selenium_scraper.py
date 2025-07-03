import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def scraper_multi_pages(nb_pages=5, categorie="Appartements à louer"):
    # Mots de base selon la catégorie choisie
    base_urls = {
        "Appartements à louer": "https://www.expat-dakar.com/appartements-a-louer?page=",
        "Appartements meublés": "https://www.expat-dakar.com/appartements-meubles?page=",
        "Terrains à vendre": "https://www.expat-dakar.com/terrains-a-vendre?page="
    }

    url_base = base_urls.get(categorie)
    if not url_base:
        raise ValueError(f"Catégorie inconnue : {categorie}")

    # Configuration du navigateur en mode headless
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-dev-shm-usage")
    # Instantiation du driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    data = []

    try:
        for page in range(1, nb_pages + 1):
            url = f"{url_base}{page}"
            driver.get(url)

            # Attendre que les éléments soient chargeés
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[class='listings-cards__list-item ']"))
            )

            containers = driver.find_elements(By.CSS_SELECTOR, "[class='listings-cards__list-item ']")

            for container in containers:
                try:
                    details = container.find_element(By.CSS_SELECTOR, ".listing-card__header__title").text
                    adresse = container.find_element(By.CSS_SELECTOR, ".listing-card__header__location").text

                    tags_container = container.find_element(By.CSS_SELECTOR, '.listing-card__header__tags')
                    span_tags = tags_container.find_elements(By.CSS_SELECTOR, 'span.listing-card__header__tags__item')

                    chambres = span_tags[0].text if len(span_tags) > 0 else None
                    superficie = span_tags[1].text if len(span_tags) > 1 else None

                    prix = container.find_element(By.CSS_SELECTOR, ".listing-card__info-bar").text

                    image = container.find_element(By.CSS_SELECTOR, ".listing-card__image__resource")
                    image_link = image.get_attribute("src")

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
                    print(f"Erreur lors du traitement d'un élément: {e}")
                    continue  # Ignore les erreurs d'une annonce

    finally:
        driver.quit()

    # Convertir en DataFrame
    df = pd.DataFrame(data)
    return df
