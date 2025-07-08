import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

def afficher_dashboard(df, titre):
    st.subheader(f"📊 Dashboard - {titre}")

    if "prix" in df.columns:
        try:
            df["prix"] = df["prix"].replace('[^0-9]', '', regex=True).astype(float)
        except:
            pass
        st.write("Distribution des prix :")
        fig, ax = plt.subplots()
        df["prix"].dropna().plot.hist(bins=20, ax=ax)
        st.pyplot(fig)

    if "superficie" in df.columns:
        try:
            df["superficie"] = df["superficie"].replace('[^0-9]', '', regex=True).astype(float)
            st.write("Distribution des superficies :")
            fig, ax = plt.subplots()
            df["superficie"].dropna().plot.hist(bins=20, ax=ax)
            st.pyplot(fig)
        except:
            st.info("Colonne superficie non exploitable.")

    st.dataframe(df.head(50))

