
import streamlit as st
import pandas as pd
from scraper.selenium_scraper import scraper_multi_pages
from dashboard.visualisations import afficher_dashboard
from feedback.evaluation import formulaire 

# --- Configuration de la page ---
st.set_page_config(page_title="SAM SCRAPER", layout="wide")
st.title("🕷️SAM SCRAPER")
st.markdown("Bienvenue sur la plateforme de scraping et d'analyse de données immobilières.")

# --- Chargement du style CSS ---
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Menu latéral ---
menu = st.sidebar.radio("Navigation", [
    "Scraper les données (nettoyées)",
    "Visualiser le dashboard",
    "Télécharger les données brutes",
    "Donner votre avis"
])

# --- Fichiers de données ---
fichiers_brutes = {
    "Appartements à louer": "Data/Appartements_____a___louer.xlsx",
    "Appartements meublés": "Data/Appartements_______meubles.xlsx",
    "Terrains à vendre": "Data/terrains____a__vendre.xlsx"
}

fichiers_nettoyes = {
    "Appartements à louer": "Data/expat_dkr_app_nettoyees.csv",
    "Appartements meublés": "Data/expatDkr_app_meubles.csv",
    "Terrains à vendre": "Data/expat_terrains_nettoyees.csv"
}

# --- Scraping ---
if menu == "Scraper les données (nettoyées)":
    st.header("🕷️ Scraper les données")
    categorie = st.selectbox("Choisissez une catégorie :", list(fichiers_nettoyes.keys()))
    nb_pages = st.slider("Nombre de pages à scraper :", 1, 100, 5)
if st.button("Lancer le scraping"):
    with st.spinner(f"Scraping de {categorie} sur {nb_pages} page(s)..."):
        try:
            df = scraper_multi_pages(nb_pages=nb_pages, categorie=categorie)

            if df.empty:
                st.warning("Le scraping a réussi mais aucun résultat n’a été trouvé.")
            else:
                fichier_csv = fichiers_nettoyes[categorie]
                df.to_csv(fichier_csv, index=False)

                st.success(f"{len(df)} annonces récupérées et enregistrées dans : `{fichier_csv}`")
                st.dataframe(df.head())

        except Exception as e:
            st.error(f"❌ Une erreur est survenue pendant le scraping : {e}")

# --- Visualisation Dashboard ---
elif menu == "Visualiser le dashboard":
    st.header("📈 Dashboard d'analyse")
    choix = st.selectbox("Choisissez une catégorie :", list(fichiers_nettoyes.keys()))

    try:
        df = pd.read_csv(fichiers_nettoyes[choix])
        afficher_dashboard(df, choix)
    except FileNotFoundError:
        st.error("Fichier non trouvé. Veuillez lancer le scraping d'abord.")

# --- Téléchargement des données brutes ---
elif menu == "Télécharger les données brutes":
    st.header("📥 Téléchargement des fichiers brutes (.xlsx → .csv)")

    for titre, chemin in fichiers_brutes.items():
        try:
            df = pd.read_excel(chemin)
            st.download_button(
                label=f"Télécharger : {titre}",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name=chemin.replace("data/", "").replace(".xlsx", ".csv"),
                mime="text/csv"
            )
        except FileNotFoundError:
            st.warning(f"⚠️ Fichier manquant : {chemin}")

# --- Évaluation de l'application ---
elif menu == "Donner votre avis":
    st.header("📝 Évaluation de l'application")
    formulaire()
