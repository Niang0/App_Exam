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
                df = scraper_multi_pages(nb_pages, categorie)

                nom_fichier = {
                    "Appartements à louer": "data/expatDkr_app_nettoyees.csv",
                    "Appartements meublés": "data/expatDkr_app_meubles.csv",
                    "Terrains à vendre": "data/expatDkr_terrain_nettoyees.csv"
                }[categorie]

                df.to_csv(nom_fichier, index=False)
                st.success(f"✅ Scraping terminé avec succès ! {len(df)} annonces enregistrées dans : `{nom_fichier}`")
                st.dataframe(df.head())

                # Graphique de répartition des prix si la colonne existe
                if "prix" in df.columns:
                    try:
                        import matplotlib.pyplot as plt
                        df["prix"] = df["prix"].astype(str).str.replace("[^0-9]", "", regex=True).replace("", pd.NA).astype(float)
                        st.markdown("### 📊 Répartition des prix")
                        fig, ax = plt.subplots()
                        df["prix"].dropna().plot.hist(bins=20, ax=ax, color="#00b894", edgecolor="black")
                        ax.set_xlabel("Prix (FCFA)")
                        ax.set_ylabel("Nombre d'annonces")
                        st.pyplot(fig)
                    except Exception as e:
                        st.warning(f"Erreur lors de la génération du graphique : {e}")

                st.download_button(
                    label=f"Télécharger les {len(df)} annonces",
                    data=df.to_csv(index=False).encode('utf-8'),
                    file_name=f"scraped_{categorie.replace(' ', '_').lower()}_{nb_pages}pages.csv",
                    mime="text/csv"
                )

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
                file_name=chemin.replace("Data/", "").replace(".xlsx", ".csv"),
                mime="text/csv"
            )
        except FileNotFoundError:
            st.warning(f"⚠️ Fichier manquant : {chemin}")

# --- Évaluation de l'application ---
elif menu == "Donner votre avis":
    st.header("📝 Évaluation de l'application")
    formulaire()
