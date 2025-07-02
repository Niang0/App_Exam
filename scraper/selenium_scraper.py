import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

def scraper_multi_pages(nb_pages=3, categorie="Appartements meublés"):
    base_urls = {
        "Appartements à louer": "https://www.expat-dakar.com/appartements-a-louer?page=",
        "Appartements meublés": "https://www.expat-dakar.com/appartements-meubles?page=",
        "Terrains à vendre": "https://www.expat-dakar.com/terrains-a-vendre?page="
    }

    url_base = base_urls.get(categorie)
    if not url_base:
        raise ValueError(f"Catégorie inconnue : {categorie}")

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    # ✅ Télécharger et utiliser automatiquement le bon ChromeDriver
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    data = []

    try:
        for page in range(1, nb_pages + 1):
            url = f"{url_base}{page}"
            driver.get(url)
            time.sleep(2)

            containers = driver.find_elements(By.CSS_SELECTOR, "[class='listings-cards__list-item ']")

            for container in containers:
                try:
                    details = container.find_element(By.CSS_SELECTOR, ".listing-card__header__title").text
                    adresse = container.find_element(By.CSS_SELECTOR, ".listing-card__header__location").text

                    tags_container = container.find_element(By.CSS_SELECTOR, ".listing-card__header__tags")
                    span_tags = tags_container.find_elements(By.CSS_SELECTOR, "span.listing-card__header__tags__item")

                    chambres = span_tags[0].text if len(span_tags) >= 1 else None
                    superficie = span_tags[1].text if len(span_tags) >= 2 else None

                    prix = container.find_element(By.CSS_SELECTOR, ".listing-card__info-bar").text
                    image = container.find_element(By.CSS_SELECTOR, ".listing-card__image__resource.vh-img").get_attribute("src")

                    data.append({
                        "categorie": categorie,
                        "details": details,
                        "adresse": adresse,
                        "chambres": chambres,
                        "superficie": superficie,
                        "prix": prix,
                        "image_lien": image
                    })

                except Exception:
                    continue

    finally:
        driver.quit()

    return pd.DataFrame(data)
