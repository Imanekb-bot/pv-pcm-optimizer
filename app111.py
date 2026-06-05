import os
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="PV–PCM Encapsulé Maroc",
    page_icon="☀️",
    layout="wide"
)

# ============================================================
# STYLE
# ============================================================
st.markdown(
    """
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
    margin-bottom: 10px;
}
.hero p {
    font-size: 18px;
    margin-bottom: 0;
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
    font-weight: 600;
}
.metric-value {
    color: #064e3b;
    font-size: 30px;
    font-weight: 900;
    margin-top: 8px;
}
.metric-note {
    color: #475569;
    font-size: 13px;
    margin-top: 6px;
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
.small-note {
    color: #64748b;
    font-size: 13px;
}
.footer {
    text-align: center;
    color: #64748b;
    margin-top: 40px;
}
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# HELPERS
# ============================================================
def find_file(candidates):
    for file in candidates:
        if os.path.exists(file):
            return file
    return None


def safe_percent(new_value, ref_value):
    if ref_value is None or ref_value == 0:
        return 0.0
    return (new_value - ref_value) / ref_value * 100


def simple_payback(capex, annual_net_gain):
    if annual_net_gain <= 0:
        return None
    return capex / annual_net_gain


def fmt_payback(value):
    if value is None:
        return "Non rentable"
    return f"{value:.2f} ans"

# ============================================================
# DATA LOADING
# ============================================================
@st.cache_data
def load_data():
    classic_file = find_file([
        "Resultats_Optimisation_PCM_Maroc.xlsx",
        "Resultats_Optimisation_PCM_Maroc (1).xlsx",
    ])
    arch_file = find_file([
        "Optimisation_architecture_PCM_encapsule.xlsx",
        "Optimisation_architecture_PCM_encapsule (1).xlsx",
    ])

    if classic_file is None or arch_file is None:
        missing = []
        if classic_file is None:
            missing.append("Resultats_Optimisation_PCM_Maroc.xlsx")
        if arch_file is None:
            missing.append("Optimisation_architecture_PCM_encapsule.xlsx")
        raise FileNotFoundError(
            "Fichier(s) Excel manquant(s) : " + ", ".join(missing)
        )

    classic_all = pd.read_excel(classic_file, sheet_name="Tous_resultats")
    classic_opt_saison = pd.read_excel(classic_file, sheet_name="Optimal_saison")
    classic_synthese = pd.read_excel(classic_file, sheet_name="Synthese_finale")

    arch_all = pd.read_excel(arch_file, sheet_name="Toutes_architectures")
    arch_opt_saison = pd.read_excel(arch_file, sheet_name="Optimal_saison")
    arch_opt_ville = pd.read_excel(arch_file, sheet_name="Optimal_ville")

    return classic_all, classic_opt_saison, classic_synthese, arch_all, arch_opt_saison, arch_opt_ville

try:
    classic_all, classic_opt_saison, classic_synthese, arch_all, arch_opt_saison, arch_opt_ville = load_data()
except Exception as exc:
    st.error(str(exc))
    st.stop()

# ============================================================
# HEADER
# ============================================================
st.markdown(
    """
<div class="hero">
<h1>Plateforme intelligente de dimensionnement PV–PCM encapsulé</h1>
<p>
Comparaison thermo-électrique, économique et environnementale entre PV seul, PV–PCM conventionnel et PV–PCM encapsulé.
</p>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
**Développé par :** Imane Kaab  
**Encadré par :** Pr. Lahoucine Atourki  
**Master :** Énergies Renouvelables et Stockage – Université Mohammed V de Rabat
"""
)

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.title("Paramètres de dimensionnement")

ville = st.sidebar.selectbox("Ville étudiée", sorted(arch_opt_saison["Ville"].unique()))
saison = st.sidebar.selectbox("Saison", sorted(arch_opt_saison["Saison"].unique()))
panel_type = st.sidebar.selectbox("Type de panneau PV", ["Monocristallin", "Polycristallin"])
power = st.sidebar.slider("Puissance nominale du module PV (Wc)", 100, 800, 450, 10)
prix_kwh = st.sidebar.number_input("Prix de l'électricité (MAD/kWh)", 0.5, 3.0, 1.4, 0.1)

st.sidebar.markdown("---")
st.sidebar.subheader("Hypothèses économiques")
pcm_price = st.sidebar.number_input("Prix du PCM (MAD/kg)", 1.0, 300.0, 18.0, 1.0)
al_price = st.sidebar.number_input("Coût aluminium (MAD/m²)", 0.0, 200.0, 20.0, 1.0)
fab_price = st.sidebar.number_input("Coût fabrication (MAD/m²)", 0.0, 200.0, 25.0, 1.0)
pcm_mass_100 = st.sidebar.number_input("Masse PCM pour couverture 100 % (kg/m²)", 0.5, 10.0, 3.0, 0.1)
opex_rate = st.sidebar.number_input("OPEX annuel (% du CAPEX)", 0.0, 10.0, 1.0, 0.1) / 100
emission_factor = st.sidebar.number_input("Facteur d'émission (kgCO₂/kWh)", 0.0, 2.0, 0.679, 0.001)

eta_ref = 0.20 if panel_type == "Monocristallin" else 0.17
surface_module = power / (1000 * eta_ref)

# ============================================================
# FILTER DATA
# ============================================================
classic_data = classic_all[(classic_all["Ville"] == ville) & (classic_all["Saison"] == saison)].copy()
arch_data = arch_all[(arch_all["Ville"] == ville) & (arch_all["Saison"] == saison)].copy()

classic_best = classic_opt_saison[
    (classic_opt_saison["Ville"] == ville) & (classic_opt_saison["Saison"] == saison)
].iloc[0]

arch_best = arch_opt_saison[
    (arch_opt_saison["Ville"] == ville) & (arch_opt_saison["Saison"] == saison)
].iloc[0]

# ============================================================
# CALCULATIONS
# ============================================================
pcm_classic = classic_best["PCM"]
pcm_enc = arch_best["PCM"]
coverage_enc = float(arch_best["Coverage"])
coverage_enc_percent = coverage_enc * 100
thickness_enc = float(arch_best["Epaisseur_mm"])
channels_enc = int(arch_best["Nombre_canaux"])
channel_width_cm = float(arch_best["Largeur_canal_m"]) * 100

# Energy per m² per day
E_pv_m2_day = float(arch_best["E_PV_seul_kWh_m2_day"])
E_pcm100_m2_day = float(classic_best["E_PV_PCM_kWh_m2_day"])
E_enc_m2_day = float(arch_best["E_architecture_kWh_m2_day"])

# Total energy for selected module area
E_pv_day = E_pv_m2_day * surface_module
E_pcm100_day = E_pcm100_m2_day * surface_module
E_enc_day = E_enc_m2_day * surface_module

E_pv_year = E_pv_day * 365
E_pcm100_year = E_pcm100_day * 365
E_enc_year = E_enc_day * 365

revenue_pv = E_pv_year * prix_kwh
revenue_pcm100 = E_pcm100_year * prix_kwh
revenue_enc = E_enc_year * prix_kwh

# Gains
gain_pcm100_vs_pv = safe_percent(E_pcm100_year, E_pv_year)
gain_enc_vs_pv = safe_percent(E_enc_year, E_pv_year)
gain_enc_vs_pcm100 = safe_percent(E_enc_year, E_pcm100_year)

# Thermal performance
reduction_pcm100 = float(classic_best["Reduction_Tmax_C"])
reduction_enc = float(arch_best["Reduction_Tmax_C"])

# Costs for selected module area
mass_pcm100 = pcm_mass_100 * surface_module
mass_enc = pcm_mass_100 * coverage_enc * surface_module
capex_pcm100 = mass_pcm100 * pcm_price + surface_module * al_price + surface_module * fab_price
capex_enc = mass_enc * pcm_price + surface_module * al_price + surface_module * fab_price

# Additional economic indicators
opex_pcm100 = capex_pcm100 * opex_rate
opex_enc = capex_enc * opex_rate

annual_gain_pcm100 = revenue_pcm100 - revenue_pv
annual_gain_enc = revenue_enc - revenue_pv
net_gain_pcm100 = annual_gain_pcm100 - opex_pcm100
net_gain_enc = annual_gain_enc - opex_enc

tri_pcm100 = simple_payback(capex_pcm100, net_gain_pcm100)
tri_enc = simple_payback(capex_enc, net_gain_enc)
capex_reduction = safe_percent(capex_pcm100, capex_enc) * -1
tri_reduction = safe_percent(tri_enc, tri_pcm100) * -1 if tri_pcm100 and tri_enc else 0

# Environmental indicators
co2_pv = E_pv_year * emission_factor
co2_pcm100 = E_pcm100_year * emission_factor
co2_enc = E_enc_year * emission_factor
co2_extra_enc_vs_pcm100 = co2_enc - co2_pcm100
co2_extra_enc_vs_pv = co2_enc - co2_pv

# Dataframes for tables
comparison_df = pd.DataFrame({
    "Indicateur": [
        "Énergie annuelle (kWh/an)",
        "Revenu annuel (MAD/an)",
        "Gain énergétique vs PV seul (%)",
        "Gain supplémentaire vs PCM 100 % (%)",
        "Réduction Tmax (°C)",
        "Masse PCM (kg)",
        "CAPEX refroidissement (MAD)",
        "OPEX annuel (MAD/an)",
        "Gain net annuel (MAD/an)",
        "Temps de retour simple",
    ],
    "PV seul": [
        E_pv_year,
        revenue_pv,
        0,
        0,
        0,
        0,
        0,
        0,
        None,
        "--",
    ],
    "PV–PCM 100 %": [
        E_pcm100_year,
        revenue_pcm100,
        gain_pcm100_vs_pv,
        0,
        reduction_pcm100,
        mass_pcm100,
        capex_pcm100,
        opex_pcm100,
        net_gain_pcm100,
        fmt_payback(tri_pcm100),
    ],
    "PV–PCM encapsulé": [
        E_enc_year,
        revenue_enc,
        gain_enc_vs_pv,
        gain_enc_vs_pcm100,
        reduction_enc,
        mass_enc,
        capex_enc,
        opex_enc,
        net_gain_enc,
        fmt_payback(tri_enc),
    ],
})

env_df = pd.DataFrame({
    "Indicateur": [
        "Énergie annuelle (kWh/an)",
        "CO₂ évité total (kgCO₂/an)",
        "CO₂ évité sur 25 ans (kgCO₂)",
        "Gain environnemental vs PV seul (%)",
        "Gain environnemental vs PCM 100 % (%)",
    ],
    "PV seul": [E_pv_year, co2_pv, co2_pv * 25, 0, 0],
    "PV–PCM 100 %": [E_pcm100_year, co2_pcm100, co2_pcm100 * 25, gain_pcm100_vs_pv, 0],
    "PV–PCM encapsulé": [E_enc_year, co2_enc, co2_enc * 25, gain_enc_vs_pv, gain_enc_vs_pcm100],
})

# ============================================================
# MAIN METRICS
# ============================================================
st.markdown(f"<div class='section'>Résultat optimal pour {ville} – {saison}</div>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="card">
    <div class="metric-title">PCM encapsulé recommandé</div>
    <div class="metric-value">{pcm_enc}</div>
    <div class="metric-note">Référence classique : {pcm_classic}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="card">
    <div class="metric-title">Gain vs PV seul</div>
    <div class="metric-value">{gain_enc_vs_pv:.2f} %</div>
    <div class="metric-note">PCM 100 % : {gain_pcm100_vs_pv:.2f} %</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="card">
    <div class="metric-title">Gain vs PCM 100 %</div>
    <div class="metric-value">{gain_enc_vs_pcm100:.2f} %</div>
    <div class="metric-note">Comparaison directe encapsulation</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="card">
    <div class="metric-title">Réduction Tmax</div>
    <div class="metric-value">{reduction_enc:.2f} °C</div>
    <div class="metric-note">PV–PCM encapsulé</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# ARCHITECTURE
# ============================================================
st.markdown("<div class='section'>Architecture PV–PCM encapsulée proposée</div>", unsafe_allow_html=True)

colA, colB = st.columns([1.2, 1])

with colA:
    st.markdown(
        """
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
      <text x="420" y="238" text-anchor="middle" fill="white" font-size="16">Stockage latent + diffusion thermique améliorée</text>

      <rect x="105" y="245" width="110" height="18" rx="8" fill="#ccfbf1"/>
      <rect x="270" y="245" width="110" height="18" rx="8" fill="#ccfbf1"/>
      <rect x="435" y="245" width="110" height="18" rx="8" fill="#ccfbf1"/>
      <rect x="600" y="245" width="110" height="18" rx="8" fill="#ccfbf1"/>
      <text x="420" y="305" text-anchor="middle" fill="#0f172a" font-size="17" font-weight="bold">Canaux d'air et couverture optimisée</text>
    </svg>
    </div>
    """,
        unsafe_allow_html=True,
    )

with colB:
    st.markdown(f"""
    <div class="info-box">
    <h3>Configuration optimisée</h3>
    <p><b>PCM :</b> {pcm_enc}</p>
    <p><b>Épaisseur :</b> {thickness_enc:.0f} mm</p>
    <p><b>Couverture :</b> {coverage_enc_percent:.0f} %</p>
    <p><b>Nombre de canaux :</b> {channels_enc}</p>
    <p><b>Largeur des canaux :</b> {channel_width_cm:.1f} cm</p>
    <p>
    L'objectif est d'utiliser le PCM plus efficacement : moins de matière, meilleure répartition thermique,
    et comparaison directe avec une couche PCM conventionnelle à 100 %.
    </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# ENERGY AND ECONOMY
# ============================================================
st.markdown("<div class='section'>Performance énergétique et valorisation économique</div>", unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Surface du module", f"{surface_module:.2f} m²")
m2.metric("Revenu PV seul", f"{revenue_pv:.1f} MAD/an")
m3.metric("Revenu PV–PCM encapsulé", f"{revenue_enc:.1f} MAD/an")
m4.metric("TRI encapsulé", fmt_payback(tri_enc))

m5, m6, m7, m8 = st.columns(4)
m5.metric("CAPEX réduit", f"{capex_reduction:.1f} %")
m6.metric("Gain net annuel", f"{net_gain_enc:.1f} MAD/an")
m7.metric("CO₂ évité additionnel vs PV", f"{co2_extra_enc_vs_pv:.1f} kg/an")
m8.metric("CO₂ gagné vs PCM 100 %", f"{co2_extra_enc_vs_pcm100:.1f} kg/an")

st.markdown("<div class='section'>Comparaison PV seul / PCM 100 % / PCM encapsulé</div>", unsafe_allow_html=True)

st.dataframe(
    comparison_df.style.format({
        "PV seul": "{}",
        "PV–PCM 100 %": "{}",
        "PV–PCM encapsulé": "{}",
    }),
    use_container_width=True,
    hide_index=True,
)

st.markdown(f"""
<div class="info-box">
<b>Résultat clé :</b> l'architecture encapsulée réduit le CAPEX de <b>{capex_reduction:.1f} %</b>
par rapport au PCM 100 %, tout en améliorant le gain énergétique de <b>{gain_enc_vs_pcm100:.2f} %</b>.
Le temps de retour passe de <b>{fmt_payback(tri_pcm100)}</b> à <b>{fmt_payback(tri_enc)}</b>.
</div>
""", unsafe_allow_html=True)

# ============================================================
# ENVIRONMENT
# ============================================================
st.markdown("<div class='section'>Impact environnemental</div>", unsafe_allow_html=True)

st.dataframe(env_df, use_container_width=True, hide_index=True)

# ============================================================
# GRAPHS
# ============================================================
st.markdown("<div class='section'>Analyse graphique</div>", unsafe_allow_html=True)

chart_df = pd.DataFrame({
    "Configuration": ["PV seul", "PV–PCM 100 %", "PV–PCM encapsulé"],
    "Énergie annuelle (kWh/an)": [E_pv_year, E_pcm100_year, E_enc_year],
    "Revenu annuel (MAD/an)": [revenue_pv, revenue_pcm100, revenue_enc],
    "CO₂ évité (kg/an)": [co2_pv, co2_pcm100, co2_enc],
})

g1, g2 = st.columns(2)
with g1:
    fig_energy = px.bar(
        chart_df,
        x="Configuration",
        y="Énergie annuelle (kWh/an)",
        text_auto=".1f",
        title="Énergie annuelle produite"
    )
    st.plotly_chart(fig_energy, use_container_width=True)

with g2:
    fig_revenue = px.bar(
        chart_df,
        x="Configuration",
        y="Revenu annuel (MAD/an)",
        text_auto=".1f",
        title="Revenu annuel estimé"
    )
    st.plotly_chart(fig_revenue, use_container_width=True)

# Classical PCM charts
st.markdown("<div class='section'>Comparaison des PCM conventionnels</div>", unsafe_allow_html=True)

g3, g4 = st.columns(2)
with g3:
    fig1 = px.bar(
        classic_data,
        x="PCM",
        y="Reduction_Tmax_C",
        text_auto=".2f",
        title="Réduction de la température maximale"
    )
    st.plotly_chart(fig1, use_container_width=True)

with g4:
    fig2 = px.bar(
        classic_data,
        x="PCM",
        y="Gain_E_percent",
        text_auto=".2f",
        title="Gain électrique journalier"
    )
    st.plotly_chart(fig2, use_container_width=True)

# Architecture design exploration
st.markdown("<div class='section'>Exploration des architectures encapsulées</div>", unsafe_allow_html=True)
fig_arch = px.scatter(
    arch_data,
    x="Reduction_Tmax_C",
    y="Gain_E_percent",
    color="PCM",
    size="Coverage",
    hover_data=["Epaisseur_mm", "Nombre_canaux", "Largeur_canal_m"],
    title="Compromis réduction thermique / gain énergétique"
)
st.plotly_chart(fig_arch, use_container_width=True)

# ============================================================
# NUMERICAL RESULTS
# ============================================================
st.markdown("<div class='section'>Résultats numériques détaillés</div>", unsafe_allow_html=True)

classic_display = classic_data[[
    "Ville", "Saison", "PCM", "Tmax_PV_seul_C", "Tmax_PV_PCM_C",
    "Reduction_Tmax_C", "Reduction_moyenne_C", "E_PV_seul_kWh_m2_day",
    "E_PV_PCM_kWh_m2_day", "Gain_E_percent"
]].copy()
classic_display = classic_display.rename(columns={
    "Tmax_PV_seul_C": "Tmax PV seul (°C)",
    "Tmax_PV_PCM_C": "Tmax PV–PCM 100 % (°C)",
    "Reduction_Tmax_C": "Réduction Tmax (°C)",
    "Reduction_moyenne_C": "Réduction moyenne (°C)",
    "E_PV_seul_kWh_m2_day": "Énergie PV seul (kWh/m²/j)",
    "E_PV_PCM_kWh_m2_day": "Énergie PV–PCM (kWh/m²/j)",
    "Gain_E_percent": "Gain énergétique (%)",
})
st.dataframe(classic_display, use_container_width=True, hide_index=True)

st.markdown("<div class='section'>Synthèse par ville</div>", unsafe_allow_html=True)
st.dataframe(classic_synthese, use_container_width=True, hide_index=True)

# ============================================================
# SCIENTIFIC NOTE
# ============================================================
st.markdown("<div class='section'>Fondement scientifique</div>", unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
Cette plateforme compare trois niveaux de performance : le module PV seul, le module avec PCM conventionnel
à couverture totale, et l'architecture PV–PCM encapsulée optimisée. Les résultats sont issus des simulations
thermo-électriques et de l'optimisation paramétrique réalisée sous Python.
<br><br>
Le <b>score global</b> présent dans les fichiers Excel est un indicateur interne de classement utilisé durant
l'optimisation. Ce n'est pas une grandeur physique mesurable comme la température, l'énergie ou le rendement.
C'est pourquoi l'application met plutôt en avant les indicateurs directement interprétables : réduction de Tmax,
gain énergétique, revenu annuel, CAPEX, temps de retour et CO₂ évité.
</div>
""", unsafe_allow_html=True)

# ============================================================
# REPORT
# ============================================================
rapport = f"""
RAPPORT DE DIMENSIONNEMENT PV-PCM ENCAPSULE

Date : {datetime.now().strftime('%d/%m/%Y %H:%M')}

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
Prix de l'électricité : {prix_kwh:.2f} MAD/kWh

CONFIGURATION PCM CONVENTIONNELLE 100 %
PCM : {pcm_classic}
Réduction Tmax : {reduction_pcm100:.2f} °C
Gain énergétique vs PV seul : {gain_pcm100_vs_pv:.2f} %
CAPEX refroidissement : {capex_pcm100:.2f} MAD
TRI : {fmt_payback(tri_pcm100)}

CONFIGURATION PCM ENCAPSULEE
PCM : {pcm_enc}
Epaisseur : {thickness_enc:.0f} mm
Couverture : {coverage_enc_percent:.0f} %
Nombre de canaux : {channels_enc}
Largeur des canaux : {channel_width_cm:.1f} cm
Réduction Tmax : {reduction_enc:.2f} °C
Gain énergétique vs PV seul : {gain_enc_vs_pv:.2f} %
Gain énergétique vs PCM 100 % : {gain_enc_vs_pcm100:.2f} %
CAPEX refroidissement : {capex_enc:.2f} MAD
TRI : {fmt_payback(tri_enc)}

COMPARAISON ECONOMIQUE
Revenu PV seul : {revenue_pv:.2f} MAD/an
Revenu PV-PCM 100 % : {revenue_pcm100:.2f} MAD/an
Revenu PV-PCM encapsulé : {revenue_enc:.2f} MAD/an
Gain net annuel PCM 100 % : {net_gain_pcm100:.2f} MAD/an
Gain net annuel PCM encapsulé : {net_gain_enc:.2f} MAD/an
Réduction du CAPEX : {capex_reduction:.2f} %

IMPACT ENVIRONNEMENTAL
CO2 évité PV seul : {co2_pv:.2f} kgCO2/an
CO2 évité PV-PCM 100 % : {co2_pcm100:.2f} kgCO2/an
CO2 évité PV-PCM encapsulé : {co2_enc:.2f} kgCO2/an
Gain CO2 vs PV seul : {co2_extra_enc_vs_pv:.2f} kgCO2/an
Gain CO2 vs PCM 100 % : {co2_extra_enc_vs_pcm100:.2f} kgCO2/an
"""

st.download_button(
    "📄 Télécharger le rapport de dimensionnement",
    rapport,
    file_name=f"Rapport_PV_PCM_{ville}_{saison}.txt",
    mime="text/plain"
)

st.markdown(
    """
<div class="footer">
Plateforme PV–PCM Encapsulé Maroc | Projet PFE | Imane Kaab
</div>
""",
    unsafe_allow_html=True,
)
