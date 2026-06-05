import os
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

# =========================================================
# CONFIGURATION GENERALE
# =========================================================
st.set_page_config(
    page_title="PV-PCM Encapsulé Maroc",
    page_icon="☀️",
    layout="wide"
)

# =========================================================
# CONSTANTES COHERENTES AVEC LE RAPPORT
# =========================================================
ELECTRICITY_PRICE_DEFAULT = 1.40       # DH/kWh
EMISSION_FACTOR = 0.679                # kgCO2/kWh
LIFETIME_YEARS = 25

# Hypothèses économiques du rapport
PCM_MASS_100 = 3.0                     # kg.m-2 pour PCM conventionnel 100%
PCM_PRICE = 18.0                       # DH/kg
ALUMINIUM_COST = 20.0                  # DH.m-2
FABRICATION_COST = 25.0                # DH.m-2
OPEX_RATE = 0.01                       # 1 % du CAPEX
ENCAPSULATED_COVERAGE = 0.60           # 60 %
ENCAPSULATION_EXTRA_GAIN = 3.00        # +3 % par rapport au PV-PCM 100 %

# =========================================================
# STYLE
# =========================================================
st.markdown(
    """
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #f8fafc 0%, #eef6f4 100%);
}
.hero {
    background: linear-gradient(135deg, #064e3b, #0f766e, #f59e0b);
    padding: 38px;
    border-radius: 28px;
    color: white;
    margin-bottom: 25px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.18);
}
.hero h1 {
    font-size: 40px;
    font-weight: 900;
    margin-bottom: 8px;
}
.hero p {
    font-size: 18px;
    margin-bottom: 0px;
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
}
.metric-value {
    color: #064e3b;
    font-size: 32px;
    font-weight: 900;
    margin-top: 8px;
}
.metric-sub {
    color: #334155;
    font-size: 13px;
    margin-top: 8px;
}
.info-box {
    background: white;
    padding: 22px;
    border-radius: 20px;
    border-left: 6px solid #0f766e;
    box-shadow: 0 5px 18px rgba(0,0,0,0.08);
}
.key-box {
    background: #ecfdf5;
    border: 1px solid #a7f3d0;
    padding: 18px;
    border-radius: 18px;
    color: #064e3b;
    font-weight: 700;
}
.footer {
    text-align: center;
    color: #64748b;
    margin-top: 45px;
    padding-bottom: 25px;
}
</style>
""",
    unsafe_allow_html=True
)

# =========================================================
# OUTILS
# =========================================================
def find_file(possible_names):
    for name in possible_names:
        if os.path.exists(name):
            return name
    for name in possible_names:
        base = os.path.basename(name)
        if os.path.exists(base):
            return base
    return None

@st.cache_data
def load_data():
    classical_file = find_file([
        "Resultats_Optimisation_PCM_Maroc.xlsx",
        "Resultats_Optimisation_PCM_Maroc (1).xlsx",
        "/mnt/data/Resultats_Optimisation_PCM_Maroc (1).xlsx",
    ])
    architecture_file = find_file([
        "Optimisation_architecture_PCM_encapsule.xlsx",
        "Optimisation_architecture_PCM_encapsule (1).xlsx",
        "/mnt/data/Optimisation_architecture_PCM_encapsule (1).xlsx",
    ])

    if classical_file is None:
        st.error("Fichier manquant : Resultats_Optimisation_PCM_Maroc.xlsx")
        st.stop()
    if architecture_file is None:
        st.error("Fichier manquant : Optimisation_architecture_PCM_encapsule.xlsx")
        st.stop()

    classical_all = pd.read_excel(classical_file, sheet_name="Tous_resultats")
    classical_opt_saison = pd.read_excel(classical_file, sheet_name="Optimal_saison")
    classical_synthese = pd.read_excel(classical_file, sheet_name="Synthese_finale")

    arch_all = pd.read_excel(architecture_file, sheet_name="Toutes_architectures")
    arch_opt_saison = pd.read_excel(architecture_file, sheet_name="Optimal_saison")
    arch_opt_ville = pd.read_excel(architecture_file, sheet_name="Optimal_ville")

    return classical_all, classical_opt_saison, classical_synthese, arch_all, arch_opt_saison, arch_opt_ville


def format_float(x, n=2):
    return f"{float(x):.{n}f}"


def compute_values(best_100, best_enc, price_kwh):
    """Calculs cohérents avec la section technico-environnementale du rapport."""

    e_pv_day = float(best_100["E_PV_seul_kWh_m2_day"])
    e_pv_year = e_pv_day * 365.0

    gain_100_pct = float(best_100["Gain_E_percent"])
    e_100_year = e_pv_year * (1.0 + gain_100_pct / 100.0)

    # Hypothèse du rapport : le PCM encapsulé apporte +3 % par rapport au PV-PCM 100 %.
    gain_enc_vs_100_pct = ENCAPSULATION_EXTRA_GAIN
    e_enc_year = e_100_year * (1.0 + gain_enc_vs_100_pct / 100.0)
    gain_enc_vs_pv_pct = (e_enc_year / e_pv_year - 1.0) * 100.0

    # Revenus annuels
    r_pv = e_pv_year * price_kwh
    r_100 = e_100_year * price_kwh
    r_enc = e_enc_year * price_kwh

    # CAPEX additionnel du système de refroidissement
    capex_100 = PCM_MASS_100 * PCM_PRICE + ALUMINIUM_COST + FABRICATION_COST
    mass_enc = PCM_MASS_100 * ENCAPSULATED_COVERAGE
    capex_enc = mass_enc * PCM_PRICE + ALUMINIUM_COST + FABRICATION_COST

    opex_100 = OPEX_RATE * capex_100
    opex_enc = OPEX_RATE * capex_enc

    delta_r_100 = r_100 - r_pv
    delta_r_enc = r_enc - r_pv

    net_100 = delta_r_100 - opex_100
    net_enc = delta_r_enc - opex_enc

    tri_100 = capex_100 / net_100 if net_100 > 0 else None
    tri_enc = capex_enc / net_enc if net_enc > 0 else None

    # Environnement : émissions évitées totales par rapport au réseau
    co2_pv = e_pv_year * EMISSION_FACTOR
    co2_100 = e_100_year * EMISSION_FACTOR
    co2_enc = e_enc_year * EMISSION_FACTOR

    return {
        "e_pv_year": e_pv_year,
        "e_100_year": e_100_year,
        "e_enc_year": e_enc_year,
        "gain_100_pct": gain_100_pct,
        "gain_enc_vs_100_pct": gain_enc_vs_100_pct,
        "gain_enc_vs_pv_pct": gain_enc_vs_pv_pct,
        "r_pv": r_pv,
        "r_100": r_100,
        "r_enc": r_enc,
        "capex_100": capex_100,
        "capex_enc": capex_enc,
        "opex_100": opex_100,
        "opex_enc": opex_enc,
        "delta_r_100": delta_r_100,
        "delta_r_enc": delta_r_enc,
        "net_100": net_100,
        "net_enc": net_enc,
        "tri_100": tri_100,
        "tri_enc": tri_enc,
        "co2_pv": co2_pv,
        "co2_100": co2_100,
        "co2_enc": co2_enc,
        "co2_25_pv": co2_pv * LIFETIME_YEARS,
        "co2_25_100": co2_100 * LIFETIME_YEARS,
        "co2_25_enc": co2_enc * LIFETIME_YEARS,
        "mass_100": PCM_MASS_100,
        "mass_enc": mass_enc,
        "capex_reduction_pct": (capex_100 - capex_enc) / capex_100 * 100.0,
        "tri_reduction_pct": ((tri_100 - tri_enc) / tri_100 * 100.0) if tri_100 and tri_enc else None,
    }


# =========================================================
# CHARGEMENT DES DONNEES
# =========================================================
classical_all, classical_opt_saison, classical_synthese, arch_all, arch_opt_saison, arch_opt_ville = load_data()

# Normalisation légère pour éviter les problèmes d'ordre
for df in [classical_all, classical_opt_saison, classical_synthese, arch_all, arch_opt_saison, arch_opt_ville]:
    if "Ville" in df.columns:
        df["Ville"] = df["Ville"].astype(str)
    if "Saison" in df.columns:
        df["Saison"] = df["Saison"].astype(str)

# =========================================================
# HEADER
# =========================================================
st.markdown(
    """
<div class="hero">
<h1>Plateforme de dimensionnement PV--PCM encapsulé</h1>
<p>Comparaison thermo-électrique, économique et environnementale des systèmes PV seul, PV--PCM 100 % et PV--PCM encapsulé sous climats marocains.</p>
</div>
""",
    unsafe_allow_html=True
)

st.markdown(
    """
**Développé par :** Imane Kaab  
**Encadré par :** Pr. Lahoucine Atourki  
**Master :** Énergies Renouvelables et Stockage -- Université Mohammed V de Rabat
"""
)

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("Paramètres de dimensionnement")

villes = sorted(classical_opt_saison["Ville"].unique())
ville = st.sidebar.selectbox("Ville étudiée", villes, index=villes.index("Marrakech") if "Marrakech" in villes else 0)

saisons_dispo = sorted(classical_opt_saison[classical_opt_saison["Ville"] == ville]["Saison"].unique())
def saison_order(s):
    order = {"Mars": 1, "Juin": 2, "Septembre": 3, "Decembre": 4, "Décembre": 4}
    return order.get(s, 99)
saisons_dispo = sorted(saisons_dispo, key=saison_order)
saison = st.sidebar.selectbox("Saison", saisons_dispo)

panel_type = st.sidebar.selectbox("Type de panneau PV", ["Monocristallin", "Polycristallin"])
power = st.sidebar.slider("Puissance nominale du module PV (Wc)", 100, 800, 450, 10)
prix_kwh = st.sidebar.number_input("Prix de l'électricité (DH/kWh)", 0.5, 3.0, ELECTRICITY_PRICE_DEFAULT, step=0.1)

eta_ref = 0.20 if panel_type == "Monocristallin" else 0.17
surface_module = power / (1000.0 * eta_ref)

# =========================================================
# SELECTION DES RESULTATS
# =========================================================
row_100 = classical_opt_saison[(classical_opt_saison["Ville"] == ville) & (classical_opt_saison["Saison"] == saison)]
row_enc = arch_opt_saison[(arch_opt_saison["Ville"] == ville) & (arch_opt_saison["Saison"] == saison)]

if row_100.empty:
    st.error("Aucun résultat PV--PCM 100 % pour cette ville et cette saison.")
    st.stop()
if row_enc.empty:
    st.error("Aucun résultat PV--PCM encapsulé pour cette ville et cette saison.")
    st.stop()

best_100 = row_100.iloc[0]
best_enc = row_enc.iloc[0]
vals = compute_values(best_100, best_enc, prix_kwh)

pcm_100 = best_100["PCM"]
pcm_enc = best_enc["PCM"]

# =========================================================
# CARTES PRINCIPALES
# =========================================================
st.markdown(f"<div class='section'>Résultat optimal pour {ville} -- {saison}</div>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="card">
    <div class="metric-title">PCM encapsulé recommandé</div>
    <div class="metric-value">{pcm_enc}</div>
    <div class="metric-sub">Référence PCM 100 % : {pcm_100}</div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="card">
    <div class="metric-title">Gain vs PV seul</div>
    <div class="metric-value">{vals['gain_enc_vs_pv_pct']:.2f} %</div>
    <div class="metric-sub">PCM 100 % : {vals['gain_100_pct']:.2f} %</div>
    </div>
    """, unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="card">
    <div class="metric-title">Gain vs PCM 100 %</div>
    <div class="metric-value">{vals['gain_enc_vs_100_pct']:.2f} %</div>
    <div class="metric-sub">Hypothèse d'encapsulation du rapport</div>
    </div>
    """, unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class="card">
    <div class="metric-title">Réduction Tmax encapsulée</div>
    <div class="metric-value">{float(best_enc['Reduction_Tmax_C']):.2f} °C</div>
    <div class="metric-sub">PV--PCM encapsulé optimisé</div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# ARCHITECTURE
# =========================================================
st.markdown("<div class='section'>Architecture PV--PCM encapsulée proposée</div>", unsafe_allow_html=True)

colA, colB = st.columns([1.1, 1])
with colA:
    st.markdown("""
    <div class="info-box">
    <svg width="100%" height="315" viewBox="0 0 850 315">
      <rect x="60" y="30" width="720" height="42" rx="12" fill="#38bdf8"/>
      <text x="420" y="57" text-anchor="middle" fill="#0f172a" font-size="18" font-weight="bold">Verre frontal</text>
      <rect x="60" y="78" width="720" height="38" rx="10" fill="#fde68a"/>
      <text x="420" y="103" text-anchor="middle" fill="#0f172a" font-size="18" font-weight="bold">Cellules photovoltaïques</text>
      <rect x="60" y="123" width="720" height="34" rx="10" fill="#94a3b8"/>
      <text x="420" y="146" text-anchor="middle" fill="white" font-size="17" font-weight="bold">Face arrière du module</text>
      <rect x="60" y="175" width="720" height="90" rx="18" fill="#0f766e"/>
      <text x="420" y="205" text-anchor="middle" fill="white" font-size="20" font-weight="bold">Capsules PCM + canaux d'air</text>
      <text x="420" y="233" text-anchor="middle" fill="white" font-size="16">Stockage latent et évacuation thermique arrière</text>
      <rect x="110" y="240" width="105" height="17" rx="8" fill="#ccfbf1"/>
      <rect x="275" y="240" width="105" height="17" rx="8" fill="#ccfbf1"/>
      <rect x="440" y="240" width="105" height="17" rx="8" fill="#ccfbf1"/>
      <rect x="605" y="240" width="105" height="17" rx="8" fill="#ccfbf1"/>
      <text x="420" y="296" text-anchor="middle" fill="#0f172a" font-size="16" font-weight="bold">Objectif : mieux exploiter le PCM, pas seulement augmenter sa quantité</text>
    </svg>
    </div>
    """, unsafe_allow_html=True)

with colB:
    st.markdown(f"""
    <div class="info-box">
    <h3>Configuration optimisée</h3>
    <p><b>PCM :</b> {pcm_enc}</p>
    <p><b>Épaisseur :</b> {float(best_enc['Epaisseur_mm']):.0f} mm</p>
    <p><b>Couverture :</b> {float(best_enc['Coverage'])*100:.0f} %</p>
    <p><b>Nombre de canaux :</b> {int(best_enc['Nombre_canaux'])}</p>
    <p><b>Largeur des canaux :</b> {float(best_enc['Largeur_canal_m'])*1000:.0f} mm</p>
    <p>La comparaison économique utilise une couverture encapsulée de 60 %, conformément à la section technico-environnementale du rapport.</p>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# COMPARAISONS ENERGETIQUES, ECONOMIQUES ET ENVIRONNEMENTALES
# =========================================================
st.markdown("<div class='section'>Comparaison PV seul / PCM 100 % / PCM encapsulé</div>", unsafe_allow_html=True)

energy_table = pd.DataFrame({
    "Indicateur": [
        "Énergie annuelle produite (kWh.m⁻².an⁻¹)",
        "Gain énergétique vs PV seul",
        "Gain supplémentaire vs PCM 100 %",
        "Énergie supplémentaire vs PV seul (kWh.m⁻².an⁻¹)",
    ],
    "PV seul": [
        f"{vals['e_pv_year']:.2f}",
        "--",
        "--",
        "--",
    ],
    "PV--PCM 100 %": [
        f"{vals['e_100_year']:.2f}",
        f"{vals['gain_100_pct']:.2f} %",
        "--",
        f"{vals['e_100_year'] - vals['e_pv_year']:.2f}",
    ],
    "PV--PCM encapsulé": [
        f"{vals['e_enc_year']:.2f}",
        f"{vals['gain_enc_vs_pv_pct']:.2f} %",
        f"{vals['gain_enc_vs_100_pct']:.2f} %",
        f"{vals['e_enc_year'] - vals['e_pv_year']:.2f}",
    ],
})
st.dataframe(energy_table, use_container_width=True, hide_index=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Revenu PV seul", f"{vals['r_pv']:.2f} DH/m²/an")
with col2:
    st.metric("Revenu PV--PCM 100 %", f"{vals['r_100']:.2f} DH/m²/an")
with col3:
    st.metric("Revenu PV--PCM encapsulé", f"{vals['r_enc']:.2f} DH/m²/an")

eco_table = pd.DataFrame({
    "Indicateur": [
        "Revenu annuel (DH.m⁻².an⁻¹)",
        "Gain économique vs PV seul",
        "CAPEX additionnel (DH.m⁻²)",
        "OPEX annuel (DH.an⁻¹)",
        "Gain net annuel (DH.m⁻².an⁻¹)",
        "Temps de retour simple",
    ],
    "PV seul": [
        f"{vals['r_pv']:.2f}",
        "--",
        "0",
        "0",
        "--",
        "--",
    ],
    "PV--PCM 100 %": [
        f"{vals['r_100']:.2f}",
        f"{vals['gain_100_pct']:.2f} %",
        f"{vals['capex_100']:.1f}",
        f"{vals['opex_100']:.2f}",
        f"{vals['net_100']:.2f}",
        f"{vals['tri_100']:.2f} ans",
    ],
    "PV--PCM encapsulé": [
        f"{vals['r_enc']:.2f}",
        f"{vals['gain_enc_vs_pv_pct']:.2f} %",
        f"{vals['capex_enc']:.1f}",
        f"{vals['opex_enc']:.2f}",
        f"{vals['net_enc']:.2f}",
        f"{vals['tri_enc']:.2f} ans",
    ],
})

st.markdown("<div class='section'>Valorisation économique</div>", unsafe_allow_html=True)
st.dataframe(eco_table, use_container_width=True, hide_index=True)

k1, k2, k3 = st.columns(3)
with k1:
    st.markdown(f"""
    <div class="key-box">CAPEX réduit : {vals['capex_reduction_pct']:.1f} %</div>
    """, unsafe_allow_html=True)
with k2:
    st.markdown(f"""
    <div class="key-box">TRI réduit : {vals['tri_reduction_pct']:.1f} %</div>
    """, unsafe_allow_html=True)
with k3:
    st.markdown(f"""
    <div class="key-box">Gain vs PCM 100 % : {vals['gain_enc_vs_100_pct']:.1f} %</div>
    """, unsafe_allow_html=True)

env_table = pd.DataFrame({
    "Indicateur": [
        "CO₂ évité (kgCO₂.m⁻².an⁻¹)",
        "CO₂ évité sur 25 ans (kgCO₂.m⁻²)",
        "Gain environnemental vs PV seul",
        "Gain environnemental vs PCM 100 %",
    ],
    "PV seul": [
        f"{vals['co2_pv']:.2f}",
        f"{vals['co2_25_pv']:.1f}",
        "--",
        "--",
    ],
    "PV--PCM 100 %": [
        f"{vals['co2_100']:.2f}",
        f"{vals['co2_25_100']:.1f}",
        f"{vals['gain_100_pct']:.2f} %",
        "--",
    ],
    "PV--PCM encapsulé": [
        f"{vals['co2_enc']:.2f}",
        f"{vals['co2_25_enc']:.1f}",
        f"{vals['gain_enc_vs_pv_pct']:.2f} %",
        f"{vals['gain_enc_vs_100_pct']:.2f} %",
    ],
})

st.markdown("<div class='section'>Impact environnemental</div>", unsafe_allow_html=True)
st.dataframe(env_table, use_container_width=True, hide_index=True)

# =========================================================
# GRAPHIQUES
# =========================================================
st.markdown("<div class='section'>Visualisation comparative</div>", unsafe_allow_html=True)

plot_df = pd.DataFrame({
    "Configuration": ["PV seul", "PV--PCM 100 %", "PV--PCM encapsulé"],
    "Énergie annuelle (kWh/m²/an)": [vals["e_pv_year"], vals["e_100_year"], vals["e_enc_year"]],
    "Revenu annuel (DH/m²/an)": [vals["r_pv"], vals["r_100"], vals["r_enc"]],
    "CO₂ évité (kgCO₂/m²/an)": [vals["co2_pv"], vals["co2_100"], vals["co2_enc"]],
})

p1, p2 = st.columns(2)
with p1:
    fig1 = px.bar(
        plot_df,
        x="Configuration",
        y="Énergie annuelle (kWh/m²/an)",
        text_auto=".2f",
        title="Production annuelle par configuration"
    )
    st.plotly_chart(fig1, use_container_width=True)
with p2:
    fig2 = px.bar(
        plot_df,
        x="Configuration",
        y="CO₂ évité (kgCO₂/m²/an)",
        text_auto=".2f",
        title="Émissions évitées par configuration"
    )
    st.plotly_chart(fig2, use_container_width=True)

# =========================================================
# RESULTATS TECHNIQUES ISSUS DES EXCEL
# =========================================================
st.markdown("<div class='section'>Résultats techniques issus des simulations</div>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["PCM conventionnel 100 %", "Architecture encapsulée"])
with tab1:
    data_100 = classical_all[(classical_all["Ville"] == ville) & (classical_all["Saison"] == saison)].copy()
    st.dataframe(
        data_100[[
            "Ville", "Saison", "PCM", "Tmax_PV_seul_C", "Tmax_PV_PCM_C",
            "Reduction_Tmax_C", "E_PV_seul_kWh_m2_day", "E_PV_PCM_kWh_m2_day", "Gain_E_percent"
        ]],
        use_container_width=True,
        hide_index=True
    )
    fig3 = px.bar(data_100, x="PCM", y="Gain_E_percent", text_auto=".2f", title="Gain électrique - PCM 100 %")
    st.plotly_chart(fig3, use_container_width=True)

with tab2:
    data_enc = arch_all[(arch_all["Ville"] == ville) & (arch_all["Saison"] == saison)].copy()
    st.dataframe(
        data_enc[[
            "Ville", "Saison", "PCM", "Epaisseur_mm", "Coverage", "Nombre_canaux",
            "Reduction_Tmax_C", "E_PV_seul_kWh_m2_day", "E_architecture_kWh_m2_day", "Gain_E_percent"
        ]].head(50),
        use_container_width=True,
        hide_index=True
    )
    top_enc = data_enc.sort_values("Gain_E_percent", ascending=False).head(10)
    fig4 = px.bar(top_enc, x="PCM", y="Gain_E_percent", color="Epaisseur_mm", text_auto=".2f", title="Top configurations encapsulées - gain électrique")
    st.plotly_chart(fig4, use_container_width=True)

# =========================================================
# SYNTHESE PAR VILLE
# =========================================================
st.markdown("<div class='section'>Synthèse par ville</div>", unsafe_allow_html=True)
st.dataframe(classical_synthese, use_container_width=True, hide_index=True)

# =========================================================
# RAPPORT TELECHARGEABLE
# =========================================================
rapport = f"""
RAPPORT DE DIMENSIONNEMENT PV--PCM ENCAPSULE

Date : {datetime.now().strftime('%d/%m/%Y %H:%M')}
Développé par : Imane Kaab
Encadré par : Pr. Lahoucine Atourki

PARAMETRES
Ville : {ville}
Saison : {saison}
Type de panneau : {panel_type}
Puissance nominale : {power} Wc
Surface du module : {surface_module:.2f} m2
Prix de l'electricite : {prix_kwh:.2f} DH/kWh

RESULTATS ENERGETIQUES PAR m2
PV seul : {vals['e_pv_year']:.2f} kWh/m2/an
PV--PCM 100 % : {vals['e_100_year']:.2f} kWh/m2/an
PV--PCM encapsule : {vals['e_enc_year']:.2f} kWh/m2/an
Gain global encapsule vs PV seul : {vals['gain_enc_vs_pv_pct']:.2f} %
Gain encapsule vs PCM 100 % : {vals['gain_enc_vs_100_pct']:.2f} %

ECONOMIE PAR m2
Revenu PV seul : {vals['r_pv']:.2f} DH/m2/an
Revenu PCM 100 % : {vals['r_100']:.2f} DH/m2/an
Revenu encapsule : {vals['r_enc']:.2f} DH/m2/an
CAPEX PCM 100 % : {vals['capex_100']:.2f} DH/m2
CAPEX encapsule : {vals['capex_enc']:.2f} DH/m2
TRI PCM 100 % : {vals['tri_100']:.2f} ans
TRI encapsule : {vals['tri_enc']:.2f} ans

ENVIRONNEMENT PAR m2
CO2 evite PV seul : {vals['co2_pv']:.2f} kgCO2/m2/an
CO2 evite PCM 100 % : {vals['co2_100']:.2f} kgCO2/m2/an
CO2 evite encapsule : {vals['co2_enc']:.2f} kgCO2/m2/an
"""

st.download_button(
    "📄 Télécharger le rapport de dimensionnement",
    rapport,
    file_name=f"Rapport_PV_PCM_{ville}_{saison}.txt",
    mime="text/plain"
)

st.markdown("""
<div class="footer">
Plateforme PV--PCM Encapsulé Maroc | Projet PFE | Imane Kaab
</div>
""", unsafe_allow_html=True)
