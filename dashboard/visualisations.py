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
        annonces_avec_chambres = df_local['chambres'].notna().sum() if 'chambres' in df_local.columns else 0
        st.metric("Annonces avec chambres", annonces_avec_chambres)

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

    # ANALYSE DES TYPES DE BIENS
    if "type_bien" in df_local.columns and df_local["type_bien"].notna().any():
        st.markdown("### 🏡 Répartition par type de bien")
        
        try:
            type_counts = df_local["type_bien"].value_counts()
            
            if len(type_counts) > 0:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Graphique en secteurs (pie chart)
                    fig, ax = plt.subplots(figsize=(8, 8))
                    colors = ['#00b894', '#0984e3', '#e17055', '#a29bfe', '#fd79a8']
                    ax.pie(type_counts.values, labels=type_counts.index, autopct='%1.1f%%', 
                           colors=colors[:len(type_counts)])
                    ax.set_title("Répartition par type de bien")
                    st.pyplot(fig)
                    plt.close()
                
                with col2:
                    # Tableau des statistiques
                    st.markdown("**📊 Statistiques par type**")
                    for idx, (type_bien, count) in enumerate(type_counts.items()):
                        pourcentage = (count / len(df_local)) * 100
                        st.write(f"• {type_bien}: {count} ({pourcentage:.1f}%)")
                        
        except Exception as e:
            st.warning(f"⚠️ Erreur dans l'analyse des types de biens : {str(e)}")
    else:
        st.info("ℹ️ Colonne `type_bien` absente ou vide.")

    # ANALYSE DE L'ÉTAT DES BIENS
    if "etat" in df_local.columns and df_local["etat"].notna().any():
        st.markdown("### 🔧 État des biens")
        
        try:
            etat_counts = df_local["etat"].value_counts()
            
            if len(etat_counts) > 0:
                fig, ax = plt.subplots(figsize=(10, 6))
                bars = ax.bar(etat_counts.index, etat_counts.values, 
                             color=['#00b894', '#fdcb6e', '#e17055', '#74b9ff'])
                ax.set_xlabel("État du bien")
                ax.set_ylabel("Nombre d'annonces")
                ax.set_title("Répartition par état des biens")
                
                # Ajouter les valeurs sur les barres
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{int(height)}', ha='center', va='bottom')
                
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()
                
        except Exception as e:
            st.warning(f"⚠️ Erreur dans l'analyse de l'état : {str(e)}")
    else:
        st.info("ℹ️ Colonne `etat` absente ou vide.")

    # ANALYSE TEMPORELLE (si date disponible)
    if "date_publication" in df_local.columns and df_local["date_publication"].notna().any():
        st.markdown("### 📅 Évolution temporelle des annonces")
        
        try:
            # Conversion en datetime si nécessaire
            df_local['date_publication'] = pd.to_datetime(df_local['date_publication'], errors='coerce')
            dates_valides = df_local['date_publication'].dropna()
            
            if len(dates_valides) > 0:
                # Grouper par mois
                monthly_counts = dates_valides.dt.to_period('M').value_counts().sort_index()
                
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.plot(monthly_counts.index.astype(str), monthly_counts.values, 
                       marker='o', linewidth=2, color='#0984e3')
                ax.set_xlabel("Mois")
                ax.set_ylabel("Nombre d'annonces")
                ax.set_title("Évolution du nombre d'annonces par mois")
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()
                
        except Exception as e:
            st.warning(f"⚠️ Erreur dans l'analyse temporelle : {str(e)}")
    else:
        st.info("ℹ️ Colonne `date_publication` absente ou vide.")

    # ANALYSE DES VENDEURS/AGENTS
    if "vendeur" in df_local.columns and df_local["vendeur"].notna().any():
        st.markdown("### 👤 Top 10 des vendeurs/agents")
        
        try:
            vendeur_counts = df_local["vendeur"].value_counts().head(10)
            
            if len(vendeur_counts) > 0:
                fig, ax = plt.subplots(figsize=(12, 8))
                bars = ax.barh(vendeur_counts.index, vendeur_counts.values, color='#a29bfe')
                ax.set_xlabel("Nombre d'annonces")
                ax.set_ylabel("Vendeur/Agent")
                ax.set_title("Top 10 des vendeurs les plus actifs")
                
                # Ajouter les valeurs sur les barres
                for bar in bars:
                    width = bar.get_width()
                    ax.text(width + 0.1, bar.get_y() + bar.get_height()/2.,
                           f'{int(width)}', ha='left', va='center')
                
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()
                
        except Exception as e:
            st.warning(f"⚠️ Erreur dans l'analyse des vendeurs : {str(e)}")
    else:
        st.info("ℹ️ Colonne `vendeur` absente ou vide.")

    # Analyse des chambres
    if "chambres" in df_local.columns and df_local["chambres"].notna().any():
        st.markdown("### 🏠 Répartition par nombre de chambres")
        
        try:
            chambres_counts = df_local["chambres"].value_counts().head(10)
            
            if len(chambres_counts) > 0:
                fig, ax = plt.subplots(figsize=(10, 6))
                bars = ax.bar(chambres_counts.index, chambres_counts.values, color="#e17055", edgecolor="black")
                ax.set_xlabel("Nombre de chambres")
                ax.set_ylabel("Nombre d'annonces")
                ax.set_title("Répartition par nombre de chambres")
                
                # Ajouter les valeurs sur les barres
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{int(height)}', ha='center', va='bottom')
                
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()
            
        except Exception as e:
            st.warning(f"⚠️ Erreur dans l'analyse des chambres : {str(e)}")
    else:
        st.info("ℹ️ Colonne `chambres` absente ou vide.")

    # Analyse des adresses/localisation
    if "adresse" in df_local.columns and df_local["adresse"].notna().any():
        st.markdown("### 📍 Top 10 des zones les plus représentées")
        
        try:
            adresses_counts = df_local["adresse"].value_counts().head(10)
            
            if len(adresses_counts) > 0:
                fig, ax = plt.subplots(figsize=(12, 8))
                bars = ax.barh(adresses_counts.index, adresses_counts.values, color="#a29bfe", edgecolor="black")
                ax.set_xlabel("Nombre d'annonces")
                ax.set_ylabel("Zone")
                ax.set_title("Top 10 des zones")
                
                # Ajouter les valeurs sur les barres
                for bar in bars:
                    width = bar.get_width()
                    ax.text(width + 0.1, bar.get_y() + bar.get_height()/2.,
                           f'{int(width)}', ha='left', va='center')
                
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()
            
        except Exception as e:
            st.warning(f"⚠️ Erreur dans l'analyse des adresses : {str(e)}")
    else:
        st.info("ℹ️ Colonne `adresse` absente ou vide.")

    # ANALYSE DES ÉQUIPEMENTS/CARACTÉRISTIQUES
    if "equipements" in df_local.columns and df_local["equipements"].notna().any():
        st.markdown("### 🛠️ Équipements les plus fréquents")
        
        try:
            # Supposons que les équipements sont séparés par des virgules
            equipements_list = []
            for eq in df_local["equipements"].dropna():
                if isinstance(eq, str):
                    equipements_list.extend([e.strip() for e in eq.split(',')])
            
            if equipements_list:
                equipements_counts = pd.Series(equipements_list).value_counts().head(10)
                
                fig, ax = plt.subplots(figsize=(12, 8))
                bars = ax.barh(equipements_counts.index, equipements_counts.values, color='#fd79a8')
                ax.set_xlabel("Nombre d'occurrences")
                ax.set_ylabel("Équipement")
                ax.set_title("Top 10 des équipements les plus mentionnés")
                
                # Ajouter les valeurs sur les barres
                for bar in bars:
                    width = bar.get_width()
                    ax.text(width + 0.1, bar.get_y() + bar.get_height()/2.,
                           f'{int(width)}', ha='left', va='center')
                
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()
                
        except Exception as e:
            st.warning(f"⚠️ Erreur dans l'analyse des équipements : {str(e)}")
    else:
        st.info("ℹ️ Colonne `equipements` absente ou vide.")

    # HEATMAP DE CORRÉLATION (pour variables numériques)
    st.markdown("### 🔥 Corrélations entre variables numériques")

    try:
        # Sélectionner seulement les colonnes numériques
        numeric_columns = df_local.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_columns) > 1:
            correlation_matrix = df_local[numeric_columns].corr()
            
            fig, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                       square=True, ax=ax, fmt='.2f')
            ax.set_title("Matrice de corrélation")
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
        else:
            st.info("Pas assez de variables numériques pour calculer les corrélations.")
            
    except Exception as e:
        st.warning(f"⚠️ Erreur dans l'analyse des corrélations : {str(e)}")

    # ANALYSE DES DESCRIPTIONS (longueur, mots-clés)
    if "description" in df_local.columns and df_local["description"].notna().any():
        st.markdown("### 📝 Analyse des descriptions")
        
        try:
            # Longueur des descriptions
            df_local['longueur_description'] = df_local['description'].astype(str).str.len()
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Statistiques
                st.write(f"• Longueur moyenne : {df_local['longueur_description'].mean():.0f} caractères")
                st.write(f"• Longueur médiane : {df_local['longueur_description'].median():.0f} caractères")
                st.write(f"• Description la plus courte : {df_local['longueur_description'].min()} caractères")
                st.write(f"• Description la plus longue : {df_local['longueur_description'].max()} caractères")
            
            with col2:
                # Histogramme des longueurs
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.hist(df_local['longueur_description'], bins=20, color='#00cec9', alpha=0.7)
                ax.set_xlabel("Longueur de la description (caractères)")
                ax.set_ylabel("Nombre d'annonces")
                ax.set_title("Distribution des longueurs de description")
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()
                
        except Exception as e:
            st.warning(f"⚠️ Erreur dans l'analyse des descriptions : {str(e)}")
    else:
        st.info("ℹ️ Colonne `description` absente ou vide.")

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