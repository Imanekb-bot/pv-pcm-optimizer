import streamlit as st
import pandas as pd

# ==========================
# BASE DE DONNEES RESULTATS
# ==========================
database = {
    "Rabat": {
        "pcm": "RT31",
        "thickness": "34 mm",
        "coverage": "90%",
        "channels": 4,
        "layout": "Center-dense",
        "gain_temp": "12 °C",
        "gain_power": "4.8 %",
        "cost": "1800 DH"
    },
    "Marrakech": {
        "pcm": "RT31",
        "thickness": "34 mm",
        "coverage": "90%",
        "channels": 4,
        "layout": "Center-dense",
        "gain_temp": "13 °C",
        "gain_power": "5.0 %",
        "cost": "1900 DH"
    },
    "Ouarzazate": {
        "pcm": "RT31",
        "thickness": "34 mm",
        "coverage": "90%",
        "channels": 4,
        "layout": "Center-dense",
        "gain_temp": "14 °C",
        "gain_power": "5.2 %",
        "cost": "2000 DH"
    },
    "Merzouga": {
        "pcm": "RT31",
        "thickness": "34 mm",
        "coverage": "90%",
        "channels": 4,
        "layout": "Center-dense",
        "gain_temp": "15 °C",
        "gain_power": "5.4 %",
        "cost": "2100 DH"
    },
    "Ifrane": {
        "pcm": "RT31",
        "thickness": "20 mm",
        "coverage": "50%",
        "channels": 2,
        "layout": "Center-dense",
        "gain_temp": "6 °C",
        "gain_power": "3.0 %",
        "cost": "1500 DH"
    }
}

# ==========================
# INTERFACE
# ==========================
st.set_page_config(
    page_title="PV-PCM Optimizer",
    page_icon="☀",
    layout="wide"
)

st.title("Plateforme de dimensionnement PV–PCM encapsulé")

st.markdown("### Optimisation thermo-électrique du système photovoltaïque")

# INPUTS
city = st.selectbox(
    "Choisir la ville",
    list(database.keys())
)

panel_type = st.selectbox(
    "Type de panneau PV",
    ["Monocristallin", "Polycristallin"]
)

power = st.number_input(
    "Puissance nominale du panneau (W)",
    min_value=100,
    max_value=800,
    value=450
)

# CALCUL
if st.button("Générer configuration optimale"):

    result = database[city]

    st.success("Configuration optimale générée")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Architecture optimale")
        st.write("PCM recommandé :", result["pcm"])
        st.write("Épaisseur optimale :", result["thickness"])
        st.write("Taux de couverture :", result["coverage"])
        st.write("Nombre de canaux :", result["channels"])
        st.write("Distribution :", result["layout"])

    with col2:
        st.subheader("Performances estimées")
        st.write("Gain thermique :", result["gain_temp"])
        st.write("Gain électrique :", result["gain_power"])
        st.write("Coût estimé :", result["cost"])

    st.subheader("Résumé")
    data = {
        "Paramètre": [
            "Ville",
            "Type panneau",
            "Puissance"
        ],
        "Valeur": [
            city,
            panel_type,
            str(power) + " W"
        ]
    }

    df = pd.DataFrame(data)
    st.table(df)