import streamlit as st
import os
import csv
from datetime import datetime

def formulaire():
    """
    Formulaire d'évaluation avec gestion d'erreurs et validation
    """
    st.title("📝 Donnez votre avis")

    # Titre personnalisé en jaune
    st.markdown('<p style="color:#fdd835; font-weight:bold;">Nom et prénom</p>', unsafe_allow_html=True)
    nom = st.text_input("", placeholder="Ex. : Jean Dupont", key="nom_input")

    # Ajout d'une note (manquait dans le code original)
    st.markdown('<p style="color:#74b9ff; font-weight:bold;">Note sur 5</p>', unsafe_allow_html=True)
    note = st.slider("Évaluez l'application", 1, 5, 3, key="note_slider")

    # Titre personnalisé en rouge
    st.markdown('<p style="color:#e74c3c; font-weight:bold;">Commentaires</p>', unsafe_allow_html=True)
    commentaire = st.text_area("", placeholder="Ex. : J'adore cette application !", key="commentaire_input")

    # Ajout d'informations optionnelles
    st.markdown('<p style="color:#00b894; font-weight:bold;">Email (optionnel)</p>', unsafe_allow_html=True)
    email = st.text_input("", placeholder="Ex. : jean.dupont@example.com", key="email_input")

    st.info("🙏 Merci de partager votre avis pour améliorer l'application.")
    st.markdown("✍️ **Votre retour est précieux** pour nous aider à progresser.")

    # Affichage de la note sélectionnée
    etoiles = "⭐" * note
    st.markdown(f"**Note sélectionnée :** {etoiles} ({note}/5)")

    if st.button("📤 Envoyer mon avis", key="submit_button"):
        # Validation des données
        if nom.strip() == "":
            st.error("❗ Veuillez entrer votre nom avant de soumettre.")
            return
        
        if len(nom.strip()) < 2:
            st.error("❗ Le nom doit contenir au moins 2 caractères.")
            return
        
        if commentaire.strip() == "":
            st.warning("💭 Vous pouvez ajouter un commentaire pour nous aider davantage.")
        
        try:
            # Créer le dossier 'feedback' s'il n'existe pas
            os.makedirs("feedback", exist_ok=True)
            
            # Vérifier si le fichier existe et ajouter les en-têtes si nécessaire
            fichier_csv = "feedback/feedbacks.csv"
            fichier_existe = os.path.exists(fichier_csv)
            
            # Préparer les données
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            donnees = [timestamp, nom.strip(), note, commentaire.strip(), email.strip()]
            
            # Enregistrement dans le fichier CSV
            with open(fichier_csv, "a", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                
                # Ajouter les en-têtes si c'est un nouveau fichier
                if not fichier_existe:
                    writer.writerow(["Date", "Nom", "Note", "Commentaire", "Email"])
                
                writer.writerow(donnees)
            
            # Messages de succès
            st.success("✅ Votre avis a bien été enregistré. Merci !")
            st.balloons()
            
            # Message personnalisé
            if note >= 4:
                st.markdown(f"🎉 Merci **{nom}** ! Nous sommes ravis que l'application vous plaise !")
            elif note == 3:
                st.markdown(f"👍 Merci **{nom}** ! Vos suggestions nous aident à nous améliorer.")
            else:
                st.markdown(f"🔧 Merci **{nom}** ! Nous prendrons en compte vos remarques pour améliorer l'application.")
            
            # Afficher un résumé
            st.markdown("### 📋 Résumé de votre avis")
            st.info(f"""
            **Nom :** {nom}  
            **Note :** {etoiles} ({note}/5)  
            **Commentaire :** {commentaire if commentaire.strip() else "Aucun commentaire"}  
            **Email :** {email if email.strip() else "Non fourni"}  
            **Date :** {timestamp}
            """)
            
            # Vider les champs après soumission
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Erreur lors de l'enregistrement : {str(e)}")
            st.error("Veuillez réessayer ou contactez l'administrateur.")

    # Section informative
    st.markdown("---")
    st.markdown("### 🔍 Pourquoi votre avis est important")
    st.markdown("""
    - **Amélioration continue** : Vos retours nous aident à identifier les points à améliorer
    - **Nouvelles fonctionnalités** : Vos suggestions inspirent les futures mises à jour
    - **Expérience utilisateur** : Nous adaptons l'interface selon vos besoins
    """)
    
    # Afficher les statistiques si le fichier existe
    try:
        if os.path.exists("feedback/feedbacks.csv"):
            import pandas as pd
            df_feedback = pd.read_csv("feedback/feedbacks.csv")
            
            if len(df_feedback) > 0:
                st.markdown("### 📊 Statistiques des avis")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total des avis", len(df_feedback))
                
                with col2:
                    note_moyenne = df_feedback["Note"].mean()
                    st.metric("Note moyenne", f"{note_moyenne:.1f}/5")
                
                with col3:
                    derniere_note = df_feedback["Note"].iloc[-1]
                    st.metric("Dernière note", f"{derniere_note}/5")
                
                # Graphique simple des notes
                if len(df_feedback) > 1:
                    st.markdown("**📈 Répartition des notes**")
                    notes_count = df_feedback["Note"].value_counts().sort_index()
                    st.bar_chart(notes_count)
                
                # Afficher les derniers commentaires
                if len(df_feedback) > 0:
                    st.markdown("### 💬 Derniers commentaires")
                    derniers_avis = df_feedback.tail(3)
                    
                    for _, avis in derniers_avis.iterrows():
                        if avis["Commentaire"].strip():
                            etoiles_avis = "⭐" * int(avis["Note"])
                            st.markdown(f"""
                            **{avis['Nom']}** ({etoiles_avis})  
                            *{avis['Date']}*  
                            > {avis['Commentaire']}
                            """)
                            st.markdown("---")
                    
    except Exception as e:
        # Ignorer les erreurs de statistiques pour ne pas perturber l'utilisateur
        pass

    # Footer
    st.markdown("---")
    st.markdown("### 🤝 Contact")
    st.markdown("""
    **Questions ou suggestions ?**  
    📧 Email : support@sam-scraper.com  
    🌐 Site web : www.sam-scraper.com  
    📱 Téléphone : +221 XX XXX XX XX
    """)

def afficher_statistiques_admin():
    """
    Fonction bonus pour afficher les statistiques administrateur
    """
    st.header("📊 Statistiques Administrateur")
    
    try:
        if os.path.exists("feedback/feedbacks.csv"):
            import pandas as pd
            df = pd.read_csv("feedback/feedbacks.csv")
            
            if len(df) > 0:
                # Statistiques générales
                st.subheader("📋 Vue d'ensemble")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total avis", len(df))
                
                with col2:
                    note_moyenne = df["Note"].mean()
                    st.metric("Note moyenne", f"{note_moyenne:.2f}/5")
                
                with col3:
                    satisfaction = (df["Note"] >= 4).sum() / len(df) * 100
                    st.metric("Satisfaction", f"{satisfaction:.1f}%")
                
                with col4:
                    avec_commentaire = (df["Commentaire"] != "").sum()
                    st.metric("Avec commentaire", avec_commentaire)
                
                # Graphiques détaillés
                st.subheader("📈 Analyses détaillées")
                
                # Evolution des notes dans le temps
                df['Date'] = pd.to_datetime(df['Date'])
                df_time = df.set_index('Date').resample('D')['Note'].mean()
                
                if len(df_time.dropna()) > 1:
                    st.line_chart(df_time.dropna())
                
                # Tous les avis
                st.subheader("📝 Tous les avis")
                st.dataframe(df.sort_values('Date', ascending=False), use_container_width=True)
                
                # Export
                csv_data = df.to_csv(index=False)
                st.download_button(
                    label="📥 Télécharger tous les avis (CSV)",
                    data=csv_data,
                    file_name=f"feedbacks_export_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("Aucun avis enregistré pour le moment.")
        else:
            st.info("Aucun fichier de feedback trouvé.")
            
    except Exception as e:
        st.error(f"Erreur lors du chargement des statistiques : {str(e)}")

# Fonction utilitaire pour nettoyer les anciens avis
def nettoyer_anciens_avis(jours=30):
    """
    Supprime les avis plus anciens que X jours
    """
    try:
        if os.path.exists("feedback/feedbacks.csv"):
            import pandas as pd
            from datetime import timedelta
            
            df = pd.read_csv("feedback/feedbacks.csv")
            df['Date'] = pd.to_datetime(df['Date'])
            
            date_limite = datetime.now() - timedelta(days=jours)
            df_recent = df[df['Date'] >= date_limite]
            
            df_recent.to_csv("feedback/feedbacks.csv", index=False)
            
            return len(df) - len(df_recent)  # Nombre d'avis supprimés
    except Exception as e:
        print(f"Erreur lors du nettoyage : {str(e)}")
        return 0