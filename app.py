import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ==========================
# CONFIG PAGE
# ==========================
st.set_page_config(
    page_title="PV–PCM Encapsulé Maroc",
    page_icon="☀️",
    layout="wide"
)

# ==========================
# STYLE CSS
# ==========================
st.markdown("""
<style>
.main {
    background-color: #f8fafc;
}
.hero {
    background: linear-gradient(135deg, #0f766e, #0f172a);
    padding: 35px;
    border-radius: 22px;
    color: white;
    margin-bottom: 25px;
}
.card {
    background: white;
    padding: 22px;
    border-radius: 18px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.08);
    border-left: 6px solid #0f766e;
}
.metric-title {
    color: #64748b;
    font-size: 15px;
}
.metric-value {
    color: #0f172a;
    font-size: 30px;
    font-weight: 800;
}
.section-title {
    color: #0f172a;
    font-size: 25px;
    font-weight: 800;
    margin-top: 25px;
}
.footer {
    text-align: center;
    color: #64748b;
    margin-top: 40px;
}
</style>
""", unsafe_allow_html=True)

# ==========================
# LOAD DATA
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
# HERO
# ==========================
st.markdown("""
<div class="hero">
<h1>Plateforme d’optimisation PV–PCM encapsulé au Maroc</h1>
<h3>Dimensionnement thermo-électrique selon la ville, la saison et le matériau PCM</h3>
<p>
Application développée à partir des résultats de simulation Python du projet PFE.
Les valeurs affichées proviennent directement de la base de résultats Excel.
</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
**Développé par :** Imane Kaab  
**Encadré par :** Pr. Lahoucine Atourki  
**Formation :** Master Énergies Renouvelables et Stockage – Université Mohammed V de Rabat
""")

# ==========================
# SIDEBAR
# ==========================
st.sidebar.title("Paramètres d'entrée")

ville = st.sidebar.selectbox("Ville", sorted(all_results["Ville"].unique()))
saison = st.sidebar.selectbox("Saison", sorted(all_results["Saison"].unique()))
panel_type = st.sidebar.selectbox("Type de panneau PV", ["Monocristallin", "Polycristallin"])
power = st.sidebar.number_input("Puissance nominale du panneau (W)", 100, 800, 450)

st.sidebar.markdown("---")
st.sidebar.subheader("Hypothèses économiques")
prix_kwh = st.sidebar.number_input("Prix électricité (MAD/kWh)", 0.5, 3.0, 1.2)
surface_module = st.sidebar.number_input("Surface module (m²)", 1.0, 3.0, 2.0)

# ==========================
# FILTER
# ==========================
data = all_results[(all_results["Ville"] == ville) & (all_results["Saison"] == saison)]

best = opt_saison[
    (opt_saison["Ville"] == ville) &
    (opt_saison["Saison"] == saison)
].iloc[0]

pcm_best = best["PCM"]

# Estimation coût simple et transparente
cost_pcm = {
    "RT21": 750,
    "RT25": 850,
    "RT31": 950,
    "RT35": 1050
}

cout_estime = cost_pcm.get(pcm_best, 900) * surface_module
gain_kwh_day = (best["E_PV_PCM_kWh_m2_day"] - best["E_PV_seul_kWh_m2_day"]) * surface_module
gain_mad_year = gain_kwh_day * 365 * prix_kwh
roi = cout_estime / gain_mad_year if gain_mad_year > 0 else 0

# ==========================
# RESULTATS PRINCIPAUX
# ==========================
st.markdown(f"<div class='section-title'>Résultat optimal : {ville} – {saison}</div>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="card">
    <div class="metric-title">PCM optimal</div>
    <div class="metric-value">{pcm_best}</div>
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
# ARCHITECTURE
# ==========================
st.markdown("<div class='section-title'>Architecture recommandée</div>", unsafe_allow_html=True)

a1, a2, a3 = st.columns(3)

with a1:
    st.info(f"**Matériau PCM recommandé :** {pcm_best}")

with a2:
    st.info("**Architecture :** PCM encapsulé en face arrière du module PV")

with a3:
    st.info("**Objectif :** réduction thermique + amélioration du rendement électrique")

# ==========================
# GRAPHES
# ==========================
st.markdown("<div class='section-title'>Analyse graphique</div>", unsafe_allow_html=True)

g1, g2 = st.columns(2)

with g1:
    fig1 = px.bar(
        data,
        x="PCM",
        y="Reduction_Tmax_C",
        title="Réduction de la température maximale selon le PCM",
        text_auto=".2f"
    )
    st.plotly_chart(fig1, use_container_width=True)

with g2:
    fig2 = px.bar(
        data,
        x="PCM",
        y="Gain_E_percent",
        title="Gain électrique selon le PCM",
        text_auto=".2f"
    )
    st.plotly_chart(fig2, use_container_width=True)

fig3 = px.line(
    data,
    x="PCM",
    y=["Tmax_PV_seul_C", "Tmax_PV_PCM_C"],
    markers=True,
    title="Comparaison thermique : PV seul vs PV–PCM"
)
st.plotly_chart(fig3, use_container_width=True)

# ==========================
# ETUDE ECONOMIQUE
# ==========================
st.markdown("<div class='section-title'>Étude économique estimative</div>", unsafe_allow_html=True)

e1, e2, e3, e4 = st.columns(4)

e1.metric("Coût estimé", f"{cout_estime:.0f} MAD")
e2.metric("Gain énergétique/jour", f"{gain_kwh_day:.3f} kWh/j")
e3.metric("Gain économique/an", f"{gain_mad_year:.1f} MAD/an")
e4.metric("Retour simple", f"{roi:.1f} ans")

st.warning("""
L’étude économique est une estimation préliminaire.  
Elle dépend du prix réel du PCM, de la surface du module, du prix de l’électricité et des conditions climatiques annuelles.
Elle est présentée comme indicateur d’aide à la décision, pas comme étude financière définitive.
""")

# ==========================
# TABLEAU
# ==========================
st.markdown("<div class='section-title'>Base de comparaison pour la configuration choisie</div>", unsafe_allow_html=True)

st.dataframe(
    data[
        [
            "Ville", "Saison", "PCM",
            "Tmax_PV_seul_C", "Tmax_PV_PCM_C",
            "Reduction_Tmax_C",
            "E_PV_seul_kWh_m2_day", "E_PV_PCM_kWh_m2_day",
            "Gain_E_percent", "Score_global"
        ]
    ],
    use_container_width=True
)

# ==========================
# SYNTHESE PAR VILLE
# ==========================
st.markdown("<div class='section-title'>Synthèse finale par ville</div>", unsafe_allow_html=True)

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
# RAPPORT TELECHARGEABLE
# ==========================
rapport = f"""
RAPPORT DE RESULTATS - PV-PCM ENCAPSULE

Date : {datetime.now().strftime("%d/%m/%Y %H:%M")}

Projet : Optimisation d’un système photovoltaïque refroidi par PCM encapsulé
Développé par : Imane Kaab
Encadré par : Pr. Lahoucine Atourki
Formation : Master Énergies Renouvelables et Stockage - Université Mohammed V de Rabat

PARAMETRES D'ENTREE
Ville : {ville}
Saison : {saison}
Type de panneau : {panel_type}
Puissance nominale : {power} W

RESULTAT OPTIMAL
PCM recommandé : {pcm_best}
Température maximale PV seul : {best['Tmax_PV_seul_C']:.2f} °C
Température maximale PV-PCM : {best['Tmax_PV_PCM_C']:.2f} °C
Réduction de température maximale : {best['Reduction_Tmax_C']:.2f} °C
Gain électrique : {best['Gain_E_percent']:.2f} %
Score global : {best['Score_global']:.2f}

ETUDE ECONOMIQUE ESTIMATIVE
Coût estimé : {cout_estime:.0f} MAD
Gain énergétique journalier : {gain_kwh_day:.3f} kWh/jour
Gain économique annuel : {gain_mad_year:.1f} MAD/an
Retour simple estimé : {roi:.1f} ans

METHODOLOGIE
Les résultats sont issus d’une simulation paramétrique réalisée sous Python.
La plateforme ne génère pas les résultats par intelligence artificielle.
Elle lit directement la base Excel exportée après simulation.
La sélection optimale est basée sur un score combinant la réduction thermique,
le gain électrique et la performance globale du système PV-PCM encapsulé.
"""

st.download_button(
    label="📄 Télécharger le rapport de résultat",
    data=rapport,
    file_name=f"rapport_pv_pcm_{ville}_{saison}.txt",
    mime="text/plain"
)

# ==========================
# METHODOLOGIE
# ==========================
st.markdown("<div class='section-title'>Méthodologie scientifique</div>", unsafe_allow_html=True)

st.markdown("""
La plateforme est basée sur une démarche en quatre étapes :

1. **Collecte des données climatiques** représentatives des villes marocaines étudiées.  
2. **Simulation thermique et électrique sous Python** du système PV seul et du système PV–PCM encapsulé.  
3. **Optimisation paramétrique** selon la ville, la saison et le type de PCM.  
4. **Visualisation interactive** des résultats via Streamlit.

Le site ne remplace pas le modèle numérique.  
Il sert d’interface de consultation et d’aide à la décision à partir des résultats validés.
""")

st.markdown("""
<div class="footer">
Plateforme PV–PCM Encapsulé Maroc | Projet PFE | Imane Kaab
</div>
""", unsafe_allow_html=True)
