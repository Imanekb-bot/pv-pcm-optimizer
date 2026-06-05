import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="PV–PCM Encapsulé Maroc",
    page_icon="☀️",
    layout="wide"
)

# ==========================
# STYLE
# ==========================
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #f8fafc 0%, #eef6f4 100%);
}
.hero {
    background: linear-gradient(135deg, #064e3b, #0f766e, #f59e0b);
    padding: 42px;
    border-radius: 28px;
    color: white;
    margin-bottom: 25px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.18);
}
.hero h1 {
    font-size: 42px;
    font-weight: 900;
}
.hero p {
    font-size: 18px;
}
.card {
    background: white;
    padding: 24px;
    border-radius: 22px;
    box-shadow: 0 6px 25px rgba(15,23,42,0.10);
    border: 1px solid #e2e8f0;
    height: 150px;
}
.metric-title {
    color: #64748b;
    font-size: 15px;
    font-weight: 600;
}
.metric-value {
    color: #064e3b;
    font-size: 32px;
    font-weight: 900;
}
.section {
    color: #0f172a;
    font-size: 28px;
    font-weight: 900;
    margin-top: 35px;
    margin-bottom: 15px;
}
.info-box {
    background: white;
    padding: 24px;
    border-radius: 20px;
    border-left: 6px solid #0f766e;
    box-shadow: 0 5px 18px rgba(0,0,0,0.08);
}
.footer {
    text-align: center;
    color: #64748b;
    margin-top: 40px;
}
</style>
""", unsafe_allow_html=True)

# ==========================
# DATA
# ==========================
@st.cache_data
def load_data():
    file = "Resultats_Optimisation_PCM_Maroc.xlsx"
    all_results = pd.read_excel(file, sheet_name="Tous_resultats")
    opt_saison = pd.read_excel(file, sheet_name="Optimal_saison")
    opt_ville = pd.read_excel(file, sheet_name="Optimal_ville")
    synthese = pd.read_excel(file, sheet_name="Synthese_finale")
    return all_results, opt_saison, opt_ville, synthese

all_results, opt_saison, opt_ville, synthese = load_data()

# ==========================
# HEADER
# ==========================
st.markdown("""
<div class="hero">
<h1>Plateforme intelligente de dimensionnement PV–PCM encapsulé</h1>
<p>
Optimisation thermo-électrique d’un module photovoltaïque refroidi par matériau à changement de phase,
selon la ville, la saison et les conditions d’exploitation.
</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
**Développé par :** Imane Kaab  
**Encadré par :** Pr. Lahoucine Atourki  
**Master :** Énergies Renouvelables et Stockage – Université Mohammed V de Rabat
""")

# ==========================
# SIDEBAR
# ==========================
st.sidebar.title("Paramètres de dimensionnement")

ville = st.sidebar.selectbox("Ville étudiée", sorted(all_results["Ville"].unique()))
saison = st.sidebar.selectbox("Saison", sorted(all_results["Saison"].unique()))
panel_type = st.sidebar.selectbox("Type de panneau PV", ["Monocristallin", "Polycristallin"])
power = st.sidebar.slider("Puissance nominale du module PV (Wc)", 100, 800, 450, 10)
prix_kwh = st.sidebar.number_input("Prix de l’électricité (MAD/kWh)", 0.5, 3.0, 1.2)

eta_ref = 0.20 if panel_type == "Monocristallin" else 0.17
surface_module = power / (1000 * eta_ref)

# ==========================
# FILTER DATA
# ==========================
data = all_results[(all_results["Ville"] == ville) & (all_results["Saison"] == saison)]
best = opt_saison[(opt_saison["Ville"] == ville) & (opt_saison["Saison"] == saison)].iloc[0]

pcm = best["PCM"]

# Architecture rules
if best["Tmax_PV_seul_C"] >= 50:
    thickness = "40 mm"
    coverage = "90 %"
    channels = "4 canaux"
    architecture = "encapsulation dense avec canaux de ventilation"
elif best["Tmax_PV_seul_C"] >= 42:
    thickness = "34 mm"
    coverage = "80 %"
    channels = "3 à 4 canaux"
    architecture = "encapsulation intermédiaire optimisée"
else:
    thickness = "25 mm"
    coverage = "60 à 70 %"
    channels = "2 canaux"
    architecture = "encapsulation légère adaptée au climat"

# Power-dependent calculations
E_pv_day = best["E_PV_seul_kWh_m2_day"] * surface_module
E_pcm_day = best["E_PV_PCM_kWh_m2_day"] * surface_module
gain_day = E_pcm_day - E_pv_day
gain_year = gain_day * 365
gain_mad = gain_year * prix_kwh

pcm_cost = {"RT21": 20, "RT25": 25, "RT31": 25, "RT35": 20}
cout_systeme = pcm_cost.get(pcm, 320) * surface_module * 3.2


# ==========================
# MAIN METRICS
# ==========================
st.markdown(f"<div class='section'>Résultat optimal pour {ville} – {saison}</div>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="card">
    <div class="metric-title">PCM recommandé</div>
    <div class="metric-value">{pcm}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="card">
    <div class="metric-title">Réduction Tmax</div>
    <div class="metric-value">{best['Reduction_Tmax_C']:.2f} °C</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="card">
    <div class="metric-title">Gain électrique</div>
    <div class="metric-value">{best['Gain_E_percent']:.2f} %</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="card">
    <div class="metric-title">Score global</div>
    <div class="metric-value">{best['Score_global']:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

# ==========================
# ARCHITECTURE IMAGE
# ==========================
st.markdown("<div class='section'>Architecture PV–PCM encapsulé proposée</div>", unsafe_allow_html=True)

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
      <text x="420" y="238" text-anchor="middle" fill="white" font-size="16">Stockage thermique latent et réduction de la température PV</text>

      <rect x="105" y="245" width="110" height="18" rx="8" fill="#ccfbf1"/>
      <rect x="270" y="245" width="110" height="18" rx="8" fill="#ccfbf1"/>
      <rect x="435" y="245" width="110" height="18" rx="8" fill="#ccfbf1"/>
      <rect x="600" y="245" width="110" height="18" rx="8" fill="#ccfbf1"/>
      <text x="420" y="305" text-anchor="middle" fill="#0f172a" font-size="17" font-weight="bold">Canaux d’air pour évacuation thermique</text>
    </svg>
    </div>
    """, unsafe_allow_html=True)

with colB:
    st.markdown(f"""
    <div class="info-box">
    <h3>Configuration recommandée</h3>
    <p><b>Type PCM :</b> {pcm}</p>
    <p><b>Épaisseur proposée :</b> {thickness}</p>
    <p><b>Taux de couverture :</b> {coverage}</p>
    <p><b>Ventilation arrière :</b> {channels}</p>
    <p><b>Architecture :</b> {architecture}</p>
    <p>
    Cette architecture vise à limiter l’échauffement du module tout en conservant
    une évacuation thermique suffisante à l’arrière du système.
    </p>
    </div>
    """, unsafe_allow_html=True)

# ==========================
# ENERGY AND ECONOMY
# ==========================
st.markdown("<div class='section'>Performance énergétique et valorisation économique</div>", unsafe_allow_html=True)

e1, e2, e3, e4 = st.columns(4)

e1.metric("Surface calculée du module", f"{surface_module:.2f} m²")
e2.metric("Énergie PV seul", f"{E_pv_day:.3f} kWh/j")
e3.metric("Énergie PV–PCM", f"{E_pcm_day:.3f} kWh/j")
e4.metric("Gain annuel valorisé", f"{gain_mad:.1f} MAD/an")

e5, e6, e7 = st.columns(3)
e5.metric("Gain énergétique annuel", f"{gain_year:.2f} kWh/an")
e6.metric("Coût système PCM", f"{cout_systeme:.0f} MAD")


# ==========================
# GRAPHS
# ==========================
st.markdown("<div class='section'>Analyse comparative des PCM</div>", unsafe_allow_html=True)

g1, g2 = st.columns(2)

with g1:
    fig1 = px.bar(
        data,
        x="PCM",
        y="Reduction_Tmax_C",
        text_auto=".2f",
        title="Réduction de la température maximale"
    )
    st.plotly_chart(fig1, use_container_width=True)

with g2:
    fig2 = px.bar(
        data,
        x="PCM",
        y="Gain_E_percent",
        text_auto=".2f",
        title="Gain électrique journalier"
    )
    st.plotly_chart(fig2, use_container_width=True)

fig3 = px.line(
    data,
    x="PCM",
    y=["Tmax_PV_seul_C", "Tmax_PV_PCM_C"],
    markers=True,
    title="Température maximale : PV seul vs PV–PCM"
)
st.plotly_chart(fig3, use_container_width=True)

# ==========================
# TABLES
# ==========================
st.markdown("<div class='section'>Résultats numériques détaillés</div>", unsafe_allow_html=True)

st.dataframe(
    data[
        [
            "Ville", "Saison", "PCM",
            "Tmax_PV_seul_C", "Tmax_PV_PCM_C",
            "Reduction_Tmax_C",
            "Reduction_moyenne_C",
            "E_PV_seul_kWh_m2_day",
            "E_PV_PCM_kWh_m2_day",
            "Gain_E_percent",
            "Score_global"
        ]
    ],
    use_container_width=True
)

st.markdown("<div class='section'>Synthèse par ville</div>", unsafe_allow_html=True)
st.dataframe(synthese, use_container_width=True)

fig4 = px.bar(
    synthese,
    x="Ville",
    y="Gain électrique moyen (%)",
    color="PCM optimal",
    title="Gain électrique moyen par ville"
)
st.plotly_chart(fig4, use_container_width=True)

# ==========================
# METHODOLOGY
# ==========================
st.markdown("<div class='section'>Fondement scientifique</div>", unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
Cette plateforme est issue d’un travail de modélisation thermo-électrique et d’optimisation paramétrique
d’un système photovoltaïque couplé à un matériau à changement de phase encapsulé.

L’étude considère plusieurs villes marocaines, différentes saisons et plusieurs matériaux PCM.
Les performances sont évaluées à partir d’indicateurs thermiques, électriques et économiques :
température maximale du module, réduction thermique, énergie journalière produite, gain électrique
et score global de performance.

La plateforme recommande l’architecture PV–PCM la plus adaptée au contexte climatique choisi,
tout en permettant une comparaison directe entre les différents matériaux étudiés.
</div>
""", unsafe_allow_html=True)

# ==========================
# REPORT
# ==========================
rapport = f"""
RAPPORT DE DIMENSIONNEMENT PV–PCM ENCAPSULE

Date : {datetime.now().strftime("%d/%m/%Y %H:%M")}

Développé par : Imane Kaab
Encadré par : Pr. Lahoucine Atourki
Master : Énergies Renouvelables et Stockage
Université Mohammed V de Rabat

PARAMETRES
Ville : {ville}
Saison : {saison}
Type de panneau : {panel_type}
Puissance nominale : {power} Wc
Surface calculée du module : {surface_module:.2f} m²

CONFIGURATION RECOMMANDEE
PCM : {pcm}
Epaisseur : {thickness}
Couverture : {coverage}
Ventilation : {channels}
Architecture : {architecture}

RESULTATS THERMO-ELECTRIQUES
Tmax PV seul : {best['Tmax_PV_seul_C']:.2f} °C
Tmax PV-PCM : {best['Tmax_PV_PCM_C']:.2f} °C
Réduction Tmax : {best['Reduction_Tmax_C']:.2f} °C
Gain électrique : {best['Gain_E_percent']:.2f} %
Score global : {best['Score_global']:.2f}

ENERGIE ET ECONOMIE
Energie PV seul : {E_pv_day:.3f} kWh/jour
Energie PV-PCM : {E_pcm_day:.3f} kWh/jour
Gain annuel : {gain_year:.2f} kWh/an
Valorisation annuelle : {gain_mad:.2f} MAD/an
Coût système PCM : {cout_systeme:.0f} MAD

"""

st.download_button(
    "📄 Télécharger le rapport de dimensionnement",
    rapport,
    file_name=f"Rapport_PV_PCM_{ville}_{saison}.txt",
    mime="text/plain"
)

st.markdown("""
<div class="footer">
Plateforme PV–PCM Encapsulé Maroc | Projet PFE | Imane Kaab
</div>
""", unsafe_allow_html=True)
