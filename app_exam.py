import streamlit as st
import pandas as pd
import os
from scraper.selenium_scraper import scraper_multi_pages
from dashboard.visualisations import afficher_dashboard
from feedback.evaluation import formulaire

# --- Configuration de la page ---
st.set_page_config(page_title="SAM SCRAPER", layout="wide")
st.title("🕷️SAM SCRAPER")
st.markdown("Bienvenue sur la plateforme de scraping et d'analyse de données immobilières.")

# --- Chargement du style CSS (avec gestion d'erreur) ---
try:
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("⚠️ Fichier style.css non trouvé. Styles par défaut appliqués.")

# --- Menu latéral ---
menu = st.sidebar.radio("Navigation", [
    "Scraper les données (nettoyées)",
    "Visualiser le dashboard",
    "Télécharger les données brutes",
    "Donner votre avis"
])

# --- Création des dossiers nécessaires ---
os.makedirs("Data", exist_ok=True)
os.makedirs("feedback", exist_ok=True)

# --- Fichiers de données ---
fichiers_brutes = {
    "Appartements à louer": "Data/Appartements_____a___louer.xlsx",
    "Appartements meublés": "Data/Appartements_______meubles.xlsx",
    "Terrains à vendre": "Data/terrains____a__vendre.xlsx"
}

fichiers_nettoyes = {
    "Appartements à louer": "Data/expat_dakar_apps_nettoyees.csv",
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
                # Lancement du scraping
                df = scraper_multi_pages(nb_pages, categorie)

                if df.empty:
                    st.warning("⚠️ Aucune donnée récupérée. Vérifiez la connexion ou le site web.")
                else:
                    # Sauvegarde dans le bon fichier CSV
                    nom_fichier = fichiers_nettoyes[categorie]
                    df.to_csv(nom_fichier, index=False, encoding='utf-8')

                    st.success(f"✅ {len(df)} annonces récupérées et enregistrées dans {nom_fichier}")

                    # Affichage du DataFrame
                    st.subheader("Aperçu des données scrapées")
                    st.dataframe(df, use_container_width=True)

                    # Bouton de téléchargement
                    st.download_button(
                        label=f"📥 Télécharger les données ({len(df)} lignes)",
                        data=df.to_csv(index=False, encoding='utf-8'),
                        file_name=nom_fichier.split("/")[-1],
                        mime="text/csv"
                    )
            except Exception as e:
                st.error(f"❌ Une erreur est survenue pendant le scraping : {str(e)}")
                st.error("Vérifiez votre connexion internet et que les dépendances sont installées.")

# --- Visualisation Dashboard ---
elif menu == "Visualiser le dashboard":
    st.header("📈 Dashboard d'analyse")
    choix = st.selectbox("Choisissez une catégorie :", list(fichiers_nettoyes.keys()))

    try:
        df = pd.read_csv(fichiers_nettoyes[choix], encoding='utf-8')
        if df.empty:
            st.warning("⚠️ Le fichier de données est vide. Lancez d'abord le scraping.")
        else:
            afficher_dashboard(df, choix)
    except FileNotFoundError:
        st.error("❌ Fichier non trouvé. Veuillez lancer le scraping d'abord.")
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des données : {str(e)}")

# --- Téléchargement des données brutes ---
elif menu == "Télécharger les données brutes":
    st.header("📥 Téléchargement des fichiers brutes (.xlsx → .csv)")

    for titre, chemin in fichiers_brutes.items():
        try:
            if os.path.exists(chemin):
                df = pd.read_excel(chemin)
                st.download_button(
                    label=f"📥 Télécharger : {titre} ({len(df)} lignes)",
                    data=df.to_csv(index=False, encoding='utf-8'),
                    file_name=chemin.replace("Data/", "").replace(".xlsx", ".csv"),
                    mime="text/csv",
                    key=f"download_{titre}"  # Clé unique pour éviter les conflits
                )
            else:
                st.warning(f"⚠️ Fichier manquant : {chemin}")
        except Exception as e:
            st.error(f"❌ Erreur avec {titre} : {str(e)}")

# --- Évaluation de l'application ---
elif menu == "Donner votre avis":
    st.header("📝 Évaluation de l'application")
    formulaire()