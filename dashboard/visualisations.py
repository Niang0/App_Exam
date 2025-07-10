import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def afficher_dashboard(df, titre):
    """
    Affiche un dashboard avec gestion d'erreurs améliorée
    """
    st.subheader(f"📊 Dashboard - {titre}")

    if df.empty:
        st.warning("⚠️ Le tableau de données est vide.")
        return

    # Copie pour éviter de modifier l'original
    df_local = df.copy()

    # Informations générales
    st.markdown("### 📋 Informations générales")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Nombre total d'annonces", len(df_local))
    
    with col2:
        annonces_avec_prix = df_local['prix'].notna().sum() if 'prix' in df_local.columns else 0
        st.metric("Annonces avec prix", annonces_avec_prix)
    
    with col3:
        annonces_avec_superficie = df_local['superficie'].notna().sum() if 'superficie' in df_local.columns else 0
        st.metric("Annonces avec superficie", annonces_avec_superficie)

    # Fonction utilitaire pour nettoyer les données numériques
    def nettoyer_donnees_numeriques(serie):
        """Nettoie une série de données pour extraire les nombres"""
        if serie is None:
            return pd.Series(dtype=float)
        
        return (
            serie.astype(str)
            .str.replace(r'[^\d.]', '', regex=True)  # Garde seulement chiffres et points
            .replace('', pd.NA)
            .astype(float)
        )

    # Analyse des prix
    if "prix" in df_local.columns and df_local["prix"].notna().any():
        st.markdown("### 💰 Analyse des prix")
        
        try:
            prix_clean = nettoyer_donnees_numeriques(df_local["prix"])
            prix_valides = prix_clean.dropna()
            
            if len(prix_valides) > 0:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Statistiques descriptives
                    st.markdown("**📊 Statistiques des prix**")
                    st.write(f"• Prix minimum : {prix_valides.min():,.0f} FCFA")
                    st.write(f"• Prix maximum : {prix_valides.max():,.0f} FCFA")
                    st.write(f"• Prix moyen : {prix_valides.mean():,.0f} FCFA")
                    st.write(f"• Prix médian : {prix_valides.median():,.0f} FCFA")
                
                with col2:
                    # Histogramme des prix
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.hist(prix_valides, bins=20, color="#00b894", edgecolor="black", alpha=0.7)
                    ax.set_xlabel("Prix (FCFA)")
                    ax.set_ylabel("Nombre d'annonces")
                    ax.set_title("Distribution des prix")
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    st.pyplot(fig)
                    plt.close()
                
                # Graphique en boîte (box plot)
                if len(prix_valides) > 5:
                    fig, ax = plt.subplots(figsize=(10, 4))
                    ax.boxplot(prix_valides, vert=False)
                    ax.set_xlabel("Prix (FCFA)")
                    ax.set_title("Répartition des prix (Box Plot)")
                    plt.tight_layout()
                    st.pyplot(fig)
                    plt.close()
            else:
                st.info("Aucune donnée de prix valide trouvée.")
                
        except Exception as e:
            st.warning(f"⚠️ Erreur dans l'analyse des prix : {str(e)}")
    else:
        st.info("ℹ️ Colonne `prix` absente ou vide.")

    # Analyse des superficies
    if "superficie" in df_local.columns and df_local["superficie"].notna().any():
        st.markdown("### 📐 Analyse des superficies")
        
        try:
            superficie_clean = nettoyer_donnees_numeriques(df_local["superficie"])
            superficie_valides = superficie_clean.dropna()
            
            if len(superficie_valides) > 0:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Statistiques descriptives
                    st.markdown("**📊 Statistiques des superficies**")
                    st.write(f"• Superficie minimum : {superficie_valides.min():.0f} m²")
                    st.write(f"• Superficie maximum : {superficie_valides.max():.0f} m²")
                    st.write(f"• Superficie moyenne : {superficie_valides.mean():.0f} m²")
                    st.write(f"• Superficie médiane : {superficie_valides.median():.0f} m²")
                
                with col2:
                    # Histogramme des superficies
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.hist(superficie_valides, bins=20, color="#0984e3", edgecolor="black", alpha=0.7)
                    ax.set_xlabel("Superficie (m²)")
                    ax.set_ylabel("Nombre d'annonces")
                    ax.set_title("Distribution des superficies")
                    plt.tight_layout()
                    st.pyplot(fig)
                    plt.close()
            else:
                st.info("Aucune donnée de superficie valide trouvée.")
                
        except Exception as e:
            st.warning(f"⚠️ Erreur dans l'analyse des superficies : {str(e)}")
    else:
        st.info("ℹ️ Colonne `superficie` absente ou vide.")

    # Analyse des chambres
    if "chambres" in df_local.columns and df_local["chambres"].notna().any():
        st.markdown("### 🏠 Répartition par nombre de chambres")
        
        try:
            chambres_counts = df_local["chambres"].value_counts().head(10)
            
            if len(chambres_counts) > 0:
                fig, ax = plt.subplots(figsize=(10, 6))
                chambres_counts.plot(kind='bar', ax=ax, color="#e17055", edgecolor="black")
                ax.set_xlabel("Nombre de chambres")
                ax.set_ylabel("Nombre d'annonces")
                ax.set_title("Répartition par nombre de chambres")
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()
            
        except Exception as e:
            st.warning(f"⚠️ Erreur dans l'analyse des chambres : {str(e)}")

    # Analyse des adresses/localisation
    if "adresse" in df_local.columns and df_local["adresse"].notna().any():
        st.markdown("### 📍 Top 10 des zones les plus représentées")
        
        try:
            adresses_counts = df_local["adresse"].value_counts().head(10)
            
            if len(adresses_counts) > 0:
                fig, ax = plt.subplots(figsize=(12, 8))
                adresses_counts.plot(kind='barh', ax=ax, color="#a29bfe", edgecolor="black")
                ax.set_xlabel("Nombre d'annonces")
                ax.set_ylabel("Zone")
                ax.set_title("Top 10 des zones")
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()
            
        except Exception as e:
            st.warning(f"⚠️ Erreur dans l'analyse des adresses : {str(e)}")

    # Aperçu des données
    st.markdown("### 🗂️ Aperçu des données")
    
    # Filtre pour afficher les données
    col1, col2 = st.columns(2)
    with col1:
        nb_lignes = st.selectbox("Nombre de lignes à afficher", [10, 25, 50, 100], index=1)
    with col2:
        colonnes_a_afficher = st.multiselect(
            "Colonnes à afficher", 
            options=list(df_local.columns), 
            default=list(df_local.columns)
        )
    
    if colonnes_a_afficher:
        st.dataframe(df_local[colonnes_a_afficher].head(nb_lignes), use_container_width=True)
    else:
        st.dataframe(df_local.head(nb_lignes), use_container_width=True)

    # Bouton de téléchargement des données nettoyées
    st.markdown("### 📥 Télécharger les données")
    csv = df_local.to_csv(index=False, encoding='utf-8')
    st.download_button(
        label="📥 Télécharger les données complètes (CSV)",
        data=csv,
        file_name=f"{titre.lower().replace(' ', '_')}_dashboard.csv",
        mime="text/csv"
    )