import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ============================================================
# CONFIGURATION GENERALE
# ============================================================
st.set_page_config(
    page_title="PV-PCM encapsulé - Marrakech",
    page_icon="☀️",
    layout="wide"
)

# ============================================================
# STYLE
# ============================================================
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #f8fafc 0%, #eef6f4 100%);
}
.hero {
    background: linear-gradient(135deg, #064e3b, #0f766e, #f59e0b);
    padding: 38px;
    border-radius: 28px;
    color: white;
    margin-bottom: 24px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.18);
}
.hero h1 {
    font-size: 40px;
    font-weight: 900;
    margin-bottom: 8px;
}
.hero p {
    font-size: 18px;
    line-height: 1.5;
}
.section {
    color: #0f172a;
    font-size: 28px;
    font-weight: 900;
    margin-top: 35px;
    margin-bottom: 15px;
}
.card {
    background: white;
    padding: 22px;
    border-radius: 22px;
    box-shadow: 0 6px 25px rgba(15,23,42,0.10);
    border: 1px solid #e2e8f0;
    min-height: 145px;
}
.metric-title {
    color: #64748b;
    font-size: 15px;
    font-weight: 700;
    margin-bottom: 8px;
}
.metric-value {
    color: #064e3b;
    font-size: 32px;
    font-weight: 900;
}
.metric-note {
    color: #475569;
    font-size: 13px;
    margin-top: 6px;
}
.info-box {
    background: white;
    padding: 24px;
    border-radius: 20px;
    border-left: 6px solid #0f766e;
    box-shadow: 0 5px 18px rgba(0,0,0,0.08);
}
.small-note {
    color: #475569;
    font-size: 14px;
}
.footer {
    text-align: center;
    color: #64748b;
    margin-top: 40px;
    padding-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# HYPOTHESES CONFORMES AU RAPPORT
# ============================================================
CITY = "Marrakech"
SEASON = "Septembre"
PCM_CLASSIC = "RT35"
PCM_ENCAPSULATED = "RT35"
ELECTRICITY_PRICE = 1.4      # DH/kWh
EMISSION_FACTOR = 0.679      # kgCO2/kWh
LIFETIME = 25                # years

# Données énergétiques par m2 issues de l'étude technico-environnementale
E_PV_AN = 285.80             # kWh.m-2.an-1
GAIN_PCM100 = 0.0268         # +2.68 % vs PV seul
GAIN_ENC_VS_PCM100 = 0.03    # +3.00 % vs PV-PCM 100 %

E_PCM100_AN = E_PV_AN * (1 + GAIN_PCM100)
E_ENC_AN = E_PCM100_AN * (1 + GAIN_ENC_VS_PCM100)
GAIN_ENC_VS_PV = (E_ENC_AN / E_PV_AN) - 1

# CAPEX additionnel par m2
CAPEX_PCM100 = 99.0          # DH.m-2
CAPEX_ENC = 77.4             # DH.m-2
OPEX_PCM100 = 0.01 * CAPEX_PCM100
OPEX_ENC = 0.01 * CAPEX_ENC

R_PV = E_PV_AN * ELECTRICITY_PRICE
R_PCM100 = E_PCM100_AN * ELECTRICITY_PRICE
R_ENC = E_ENC_AN * ELECTRICITY_PRICE

DELTA_R_PCM100 = R_PCM100 - R_PV
DELTA_R_ENC = R_ENC - R_PV
NET_PCM100 = DELTA_R_PCM100 - OPEX_PCM100
NET_ENC = DELTA_R_ENC - OPEX_ENC
TRI_PCM100 = CAPEX_PCM100 / NET_PCM100
TRI_ENC = CAPEX_ENC / NET_ENC
CAPEX_REDUCTION = (CAPEX_PCM100 - CAPEX_ENC) / CAPEX_PCM100
TRI_REDUCTION = (TRI_PCM100 - TRI_ENC) / TRI_PCM100

CO2_PV = E_PV_AN * EMISSION_FACTOR
CO2_PCM100 = E_PCM100_AN * EMISSION_FACTOR
CO2_ENC = E_ENC_AN * EMISSION_FACTOR

CO2_PV_25 = CO2_PV * LIFETIME
CO2_PCM100_25 = CO2_PCM100 * LIFETIME
CO2_ENC_25 = CO2_ENC * LIFETIME

# ============================================================
# SIDEBAR : PROJECTION MODULE
# ============================================================
st.sidebar.title("Projection du module")
panel_type = st.sidebar.selectbox("Type de panneau PV", ["Monocristallin", "Polycristallin"])
power = st.sidebar.slider("Puissance nominale du module PV (Wc)", 100, 800, 450, 10)
eta_ref = 0.20 if panel_type == "Monocristallin" else 0.17
surface_module = power / (1000 * eta_ref)

st.sidebar.markdown("---")
st.sidebar.markdown("**Hypothèses fixes du rapport**")
st.sidebar.write(f"Ville : {CITY}")
st.sidebar.write(f"Saison : {SEASON}")
st.sidebar.write(f"Prix électricité : {ELECTRICITY_PRICE} DH/kWh")
st.sidebar.write(f"Facteur d'émission : {EMISSION_FACTOR} kgCO₂/kWh")

# ============================================================
# HEADER
# ============================================================
st.markdown("""
<div class="hero">
<h1>Plateforme PV-PCM encapsulé</h1>
<p>
Comparaison technico-économique et environnementale entre un module photovoltaïque seul,
une configuration PV-PCM conventionnelle à 100 % et une architecture PV-PCM encapsulée optimisée.
</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
**Développé par :** Imane Kaab  
**Encadré par :** Pr. Lahoucine Atourki  
**Master :** Énergies Renouvelables et Stockage - Université Mohammed V de Rabat
""")

# ============================================================
# RESULTATS PRINCIPAUX
# ============================================================
st.markdown(f"<div class='section'>Résultat optimal - {CITY} / {SEASON}</div>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="card">
      <div class="metric-title">PCM encapsulé recommandé</div>
      <div class="metric-value">{PCM_ENCAPSULATED}</div>
      <div class="metric-note">Référence conventionnelle : {PCM_CLASSIC}</div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="card">
      <div class="metric-title">Gain vs PV seul</div>
      <div class="metric-value">{GAIN_ENC_VS_PV*100:.2f} %</div>
      <div class="metric-note">PCM 100 % : {GAIN_PCM100*100:.2f} %</div>
    </div>
    """, unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="card">
      <div class="metric-title">Gain vs PCM 100 %</div>
      <div class="metric-value">{GAIN_ENC_VS_PCM100*100:.2f} %</div>
      <div class="metric-note">Amélioration additionnelle</div>
    </div>
    """, unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class="card">
      <div class="metric-title">TRI encapsulé</div>
      <div class="metric-value">{TRI_ENC:.2f} ans</div>
      <div class="metric-note">PCM 100 % : {TRI_PCM100:.2f} ans</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# ARCHITECTURE
# ============================================================
st.markdown("<div class='section'>Architecture PV-PCM encapsulée proposée</div>", unsafe_allow_html=True)

colA, colB = st.columns([1.2, 1])
with colA:
    st.markdown("""
    <div class="info-box">
    <svg width="100%" height="330" viewBox="0 0 850 330">
      <rect x="60" y="30" width="720" height="45" rx="12" fill="#38bdf8"/>
      <text x="420" y="58" text-anchor="middle" fill="#0f172a" font-size="18" font-weight="bold">Verre frontal</text>
      <rect x="60" y="82" width="720" height="40" rx="10" fill="#fde68a"/>
      <text x="420" y="108" text-anchor="middle" fill="#0f172a" font-size="18" font-weight="bold">Cellules photovoltaïques</text>
      <rect x="60" y="130" width="720" height="35" rx="10" fill="#94a3b8"/>
      <text x="420" y="153" text-anchor="middle" fill="white" font-size="17" font-weight="bold">Face arrière du module</text>
      <rect x="60" y="180" width="720" height="95" rx="18" fill="#0f766e"/>
      <text x="420" y="210" text-anchor="middle" fill="white" font-size="20" font-weight="bold">Capsules PCM encapsulées</text>
      <text x="420" y="238" text-anchor="middle" fill="white" font-size="16">Couverture optimisée de 60 % avec canaux d'air</text>
      <rect x="105" y="245" width="110" height="18" rx="8" fill="#ccfbf1"/>
      <rect x="270" y="245" width="110" height="18" rx="8" fill="#ccfbf1"/>
      <rect x="435" y="245" width="110" height="18" rx="8" fill="#ccfbf1"/>
      <rect x="600" y="245" width="110" height="18" rx="8" fill="#ccfbf1"/>
      <text x="420" y="305" text-anchor="middle" fill="#0f172a" font-size="17" font-weight="bold">Canaux d'air pour améliorer les échanges thermiques</text>
    </svg>
    </div>
    """, unsafe_allow_html=True)
with colB:
    st.markdown(f"""
    <div class="info-box">
    <h3>Configuration étudiée</h3>
    <p><b>Site :</b> {CITY}</p>
    <p><b>Saison :</b> {SEASON}</p>
    <p><b>PCM conventionnel :</b> {PCM_CLASSIC}, couverture 100 %</p>
    <p><b>PCM encapsulé :</b> {PCM_ENCAPSULATED}, couverture 60 %</p>
    <p><b>Logique :</b> conserver une performance énergétique élevée tout en réduisant le CAPEX additionnel.</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# TABLEAU ENERGETIQUE ET ECONOMIQUE
# ============================================================
st.markdown("<div class='section'>Performance énergétique et valorisation économique</div>", unsafe_allow_html=True)

eco_df = pd.DataFrame({
    "Indicateur": [
        "Energie annuelle produite (kWh/m2/an)",
        "Revenu annuel (DH/m2/an)",
        "Gain économique vs PV seul",
        "CAPEX additionnel (DH/m2)",
        "OPEX annuel (DH/an)",
        "Gain net annuel (DH/m2/an)",
        "Temps de retour simple"
    ],
    "PV seul": [
        f"{E_PV_AN:.2f}",
        f"{R_PV:.2f}",
        "--",
        "0",
        "0",
        "--",
        "--"
    ],
    "PV-PCM 100 %": [
        f"{E_PCM100_AN:.2f}",
        f"{R_PCM100:.2f}",
        f"{GAIN_PCM100*100:.2f} %",
        f"{CAPEX_PCM100:.1f}",
        f"{OPEX_PCM100:.2f}",
        f"{NET_PCM100:.2f}",
        f"{TRI_PCM100:.2f} ans"
    ],
    "PV-PCM encapsulé": [
        f"{E_ENC_AN:.2f}",
        f"{R_ENC:.2f}",
        f"{GAIN_ENC_VS_PV*100:.2f} %",
        f"{CAPEX_ENC:.1f}",
        f"{OPEX_ENC:.2f}",
        f"{NET_ENC:.2f}",
        f"{TRI_ENC:.2f} ans"
    ]
})

st.dataframe(eco_df, use_container_width=True, hide_index=True)

r1, r2, r3 = st.columns(3)
r1.metric("CAPEX réduit", f"{CAPEX_REDUCTION*100:.1f} %")
r2.metric("TRI réduit", f"{TRI_REDUCTION*100:.1f} %")
r3.metric("Gain additionnel vs PCM 100 %", f"{GAIN_ENC_VS_PCM100*100:.2f} %")

# ============================================================
# ENVIRONNEMENT
# ============================================================
st.markdown("<div class='section'>Impact environnemental</div>", unsafe_allow_html=True)

env_df = pd.DataFrame({
    "Indicateur": [
        "CO2 évité (kgCO2/m2/an)",
        "CO2 évité sur 25 ans (kgCO2/m2)",
        "Gain environnemental vs PV seul",
        "Gain supplémentaire vs PCM 100 %"
    ],
    "PV seul": [
        f"{CO2_PV:.2f}",
        f"{CO2_PV_25:.1f}",
        "--",
        "--"
    ],
    "PV-PCM 100 %": [
        f"{CO2_PCM100:.2f}",
        f"{CO2_PCM100_25:.1f}",
        f"{GAIN_PCM100*100:.2f} %",
        "--"
    ],
    "PV-PCM encapsulé": [
        f"{CO2_ENC:.2f}",
        f"{CO2_ENC_25:.1f}",
        f"{GAIN_ENC_VS_PV*100:.2f} %",
        f"{GAIN_ENC_VS_PCM100*100:.2f} %"
    ]
})

st.dataframe(env_df, use_container_width=True, hide_index=True)

# ============================================================
# GRAPHIQUES
# ============================================================
st.markdown("<div class='section'>Comparaison visuelle des configurations</div>", unsafe_allow_html=True)

plot_df = pd.DataFrame({
    "Configuration": ["PV seul", "PV-PCM 100 %", "PV-PCM encapsulé"],
    "Energie annuelle": [E_PV_AN, E_PCM100_AN, E_ENC_AN],
    "Revenu annuel": [R_PV, R_PCM100, R_ENC],
    "CO2 évité": [CO2_PV, CO2_PCM100, CO2_ENC]
})

g1, g2 = st.columns(2)
with g1:
    fig1 = px.bar(
        plot_df,
        x="Configuration",
        y="Energie annuelle",
        text_auto=".2f",
        title="Energie annuelle produite (kWh/m2/an)"
    )
    st.plotly_chart(fig1, use_container_width=True)
with g2:
    fig2 = px.bar(
        plot_df,
        x="Configuration",
        y="CO2 évité",
        text_auto=".2f",
        title="CO2 évité (kgCO2/m2/an)"
    )
    st.plotly_chart(fig2, use_container_width=True)

# ============================================================
# PROJECTION MODULE
# ============================================================
st.markdown("<div class='section'>Projection pour le module sélectionné</div>", unsafe_allow_html=True)

module_df = pd.DataFrame({
    "Indicateur": [
        "Surface du module (m2)",
        "Revenu PV seul (DH/an)",
        "Revenu PV-PCM encapsulé (DH/an)",
        "Gain net encapsulé (DH/an)",
        "CO2 évité PV seul (kgCO2/an)",
        "CO2 évité PV-PCM encapsulé (kgCO2/an)"
    ],
    "Valeur": [
        f"{surface_module:.2f}",
        f"{R_PV*surface_module:.2f}",
        f"{R_ENC*surface_module:.2f}",
        f"{NET_ENC*surface_module:.2f}",
        f"{CO2_PV*surface_module:.2f}",
        f"{CO2_ENC*surface_module:.2f}"
    ]
})
st.dataframe(module_df, use_container_width=True, hide_index=True)

# ============================================================
# FONDEMENT SCIENTIFIQUE
# ============================================================
st.markdown("<div class='section'>Lecture scientifique des résultats</div>", unsafe_allow_html=True)
st.markdown(f"""
<div class="info-box">
L'architecture encapsulée ne se limite pas à ajouter du PCM au module photovoltaïque. Elle améliore l'exploitation du stockage latent en combinant une couverture optimisée de 60 % et des canaux d'air favorisant les échanges thermiques.
<br><br>
Dans le cas de Marrakech - Septembre, le système PV-PCM 100 % apporte un gain énergétique de {GAIN_PCM100*100:.2f} % par rapport au PV seul. L'architecture encapsulée ajoute ensuite un gain supplémentaire de {GAIN_ENC_VS_PCM100*100:.2f} %, ce qui porte le gain global à {GAIN_ENC_VS_PV*100:.2f} %.
<br><br>
Cette amélioration s'accompagne d'une réduction du CAPEX additionnel de {CAPEX_REDUCTION*100:.1f} % et d'une diminution du temps de retour de {TRI_PCM100:.2f} ans à {TRI_ENC:.2f} ans.
</div>
""", unsafe_allow_html=True)

# ============================================================
# RAPPORT TELECHARGEABLE
# ============================================================
rapport = f"""
RAPPORT DE COMPARAISON PV-PCM ENCAPSULE

Date : {datetime.now().strftime('%d/%m/%Y %H:%M')}

Développé par : Imane Kaab
Encadré par : Pr. Lahoucine Atourki
Master : Energies Renouvelables et Stockage
Université Mohammed V de Rabat

CAS D'ETUDE
Ville : {CITY}
Saison : {SEASON}
PCM conventionnel : {PCM_CLASSIC}
PCM encapsulé : {PCM_ENCAPSULATED}

HYPOTHESES
Prix de l'électricité : {ELECTRICITY_PRICE} DH/kWh
Facteur d'émission : {EMISSION_FACTOR} kgCO2/kWh
Durée de vie : {LIFETIME} ans

RESULTATS ENERGETIQUES PAR m2
PV seul : {E_PV_AN:.2f} kWh/m2/an
PV-PCM 100 % : {E_PCM100_AN:.2f} kWh/m2/an
PV-PCM encapsulé : {E_ENC_AN:.2f} kWh/m2/an
Gain PV-PCM 100 % vs PV seul : {GAIN_PCM100*100:.2f} %
Gain PV-PCM encapsulé vs PV seul : {GAIN_ENC_VS_PV*100:.2f} %
Gain PV-PCM encapsulé vs PV-PCM 100 % : {GAIN_ENC_VS_PCM100*100:.2f} %

RESULTATS ECONOMIQUES PAR m2
Revenu PV seul : {R_PV:.2f} DH/m2/an
Revenu PV-PCM 100 % : {R_PCM100:.2f} DH/m2/an
Revenu PV-PCM encapsulé : {R_ENC:.2f} DH/m2/an
CAPEX PV-PCM 100 % : {CAPEX_PCM100:.2f} DH/m2
CAPEX PV-PCM encapsulé : {CAPEX_ENC:.2f} DH/m2
TRI PV-PCM 100 % : {TRI_PCM100:.2f} ans
TRI PV-PCM encapsulé : {TRI_ENC:.2f} ans

RESULTATS ENVIRONNEMENTAUX PAR m2
CO2 évité PV seul : {CO2_PV:.2f} kgCO2/m2/an
CO2 évité PV-PCM 100 % : {CO2_PCM100:.2f} kgCO2/m2/an
CO2 évité PV-PCM encapsulé : {CO2_ENC:.2f} kgCO2/m2/an

CONCLUSION
L'architecture PV-PCM encapsulée améliore le gain énergétique global tout en réduisant le CAPEX additionnel et le temps de retour par rapport au PV-PCM conventionnel à 100 %.
"""

st.download_button(
    "📄 Télécharger le rapport de comparaison",
    rapport,
    file_name="Rapport_comparaison_PV_PCM_encapsule.txt",
    mime="text/plain"
)

st.markdown("""
<div class="footer">
Plateforme PV-PCM Encapsulé Maroc | Projet PFE | Imane Kaab
</div>
""", unsafe_allow_html=True)
