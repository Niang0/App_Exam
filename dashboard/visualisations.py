import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

def afficher_dashboard(df: pd.DataFrame, titre: str):
    st.subheader(f"📊 Dashboard - {titre}")

    # Afficher le nombre total d'annonces
    st.markdown(f"**🔢 Nombre total d'annonces : {len(df)}**")

    # Histogramme des prix
    if "prix" in df.columns:
        try:
            df["prix"] = (
                df["prix"]
                .astype(str)
                .replace(r"[^\d]", "", regex=True)
                .replace("", pd.NA)
                .astype(float)
            )
            st.markdown("### 💰 Distribution des prix")
            fig, ax = plt.subplots()
            df["prix"].dropna().plot.hist(bins=20, ax=ax, color="#00b894", edgecolor="black")
            ax.set_xlabel("Prix (FCFA)")
            ax.set_ylabel("Nombre d'annonces")
            st.pyplot(fig)
        except Exception as e:
            st.warning(f"Erreur dans la colonne `prix` : {e}")

    # Histogramme des superficies
    if "superficie" in df.columns:
        try:
            df["superficie"] = (
                df["superficie"]
                .astype(str)
                .replace(r"[^\d]", "", regex=True)
                .replace("", pd.NA)
                .astype(float)
            )
            st.markdown("### 📐 Distribution des superficies")
            fig, ax = plt.subplots()
            df["superficie"].dropna().plot.hist(bins=20, ax=ax, color="#0984e3", edgecolor="black")
            ax.set_xlabel("Superficie (m²)")
            ax.set_ylabel("Nombre d'annonces")
            st.pyplot(fig)
        except Exception as e:
            st.warning(f"Erreur dans la colonne `superficie` : {e}")
    else:
        st.info("Colonne 'superficie' absente du jeu de données.")

    # Aperçu des données
    st.markdown("### 🧾 Aperçu des premières lignes")
    st.dataframe(df.head(30))
