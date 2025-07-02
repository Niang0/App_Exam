import streamlit as st
import os
import csv

def formulaire():
    st.title("📝 Donnez votre avis")

# Titre personnalisé en jaune
    st.markdown('<p style="color:#fdd835; font-weight:bold;">Nom et prénom</p>', unsafe_allow_html=True)
    nom = st.text_input("", placeholder="Ex. : Jean Dupont")

    # Titre personnalisé en rouge
    st.markdown('<p style="color:#e74c3c; font-weight:bold;">Commentaires</p>', unsafe_allow_html=True)
    commentaire = st.text_area("", placeholder="Ex. : J'adore cette application !")


    st.info("Merci de partager votre avis pour améliorer l'application.")
    st.markdown("✍️ Votre retour est précieux pour nous aider à progresser.")

    if st.button("Envoyer mon avis"):
        if nom.strip() == "":
            st.warning("❗ Veuillez entrer votre nom avant de soumettre.")
        else:
            # Créer le dossier 'feedback' s'il n'existe pas
            os.makedirs("feedback", exist_ok=True)

            # Enregistrement dans un vrai fichier CSV
            with open("feedback/feedbacks.csv", "a", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([nom, note, commentaire])

            st.success("✅ Votre avis a bien été enregistré. Merci !")
            st.balloons()
            st.markdown(f"👋 Bonjour **{nom}**, encore merci pour votre retour.")
