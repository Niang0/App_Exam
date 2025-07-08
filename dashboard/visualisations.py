import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

def afficher_dashboard(df, titre):
    st.subheader(f"📊 Dashboard - {titre}")

    if df.empty:
        st.warning("Le tableau de données est vide.")
        return

    df_local = df.copy()

    # Histogramme des prix
    if "prix" in df_local.columns:
        try:
            df_local["prix"] = (
                df_local["prix"]
                .astype(str)
                .replace('[^0-9]', '', regex=True)
                .replace('', pd.NA)
                .astype(float)
            )

            st.markdown("### 💰 Distribution des prix")
            fig, ax = plt.subplots()
            df_local["prix"].dropna().plot.hist(bins=20, ax=ax, color="#00b894", edgecolor="black")
            ax.set_xlabel("Prix (FCFA)")
            ax.set_ylabel("Nombre d'annonces")
            st.pyplot(fig)

        except Exception as e:
            st.warning(f"Erreur dans la colonne `prix` : {e}")

    else:
        st.info("Colonne `prix` absente du jeu de données.")

    # Histogramme des superficies
    if "superficie" in df_local.columns:
        try:
            df_local["superficie"] = (
                df_local["superficie"]
                .astype(str)
                .replace('[^0-9]', '', regex=True)
                .replace('', pd.NA)
                .astype(float)
            )

            st.markdown("### 📐 Distribution des superficies")
            fig, ax = plt.subplots()
            df_local["superficie"].dropna().plot.hist(bins=20, ax=ax, color="#0984e3", edgecolor="black")
            ax.set_xlabel("Superficie (m²)")
            ax.set_ylabel("Nombre d'annonces")
            st.pyplot(fig)

        except Exception as e:
            st.warning(f"Erreur dans la colonne `superficie` : {e}")
    else:
        st.info("Colonne `superficie` absente du jeu de données.")

    # Aperçu des données
    st.markdown("### 🧾 Aperçu des 50 premières lignes")
    st.dataframe(df_local.head(50))

