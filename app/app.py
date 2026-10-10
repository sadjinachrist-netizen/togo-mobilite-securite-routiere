"""
Mobilité et sécurité routière au Togo — tableau de bord interactif
Data Challenge · Administration territoriale et mobilité · Défi 1 · Togo AI Lab / MESPTN
Auteur : SADJINA Christ

Lancer : streamlit run app.py
"""
import streamlit as st

st.set_page_config(page_title="Mobilité et sécurité routière · Togo", page_icon="🛣️",
                   layout="wide", initial_sidebar_state="expanded")

from lib.ui import inject_css  # noqa: E402

inject_css()

pages = {
    "Diagnostic": [
        st.Page("views/overview.py", title="Vue d'ensemble", icon=":material/dashboard:", default=True),
        st.Page("views/parc.py", title="Parc et permis", icon=":material/two_wheeler:"),
        st.Page("views/securite.py", title="Sécurité routière", icon=":material/health_and_safety:"),
    ],
    "Territoire": [
        st.Page("views/reseau.py", title="Réseau routier", icon=":material/route:"),
        st.Page("views/formation.py", title="Formation des conducteurs", icon=":material/school:"),
    ],
    "Pilotage": [
        st.Page("views/recommandations.py", title="Recommandations", icon=":material/lightbulb:"),
        st.Page("views/methodologie.py", title="Méthodologie et données", icon=":material/menu_book:"),
    ],
}

with st.sidebar:
    st.markdown(
        """
<div style="display:flex;gap:.65rem;align-items:center;padding:.3rem 0 1rem 0">
  <div style="font-size:1.9rem;line-height:1">🛣️</div>
  <div>
    <div style="font-size:.66rem;color:#9FB8AC;letter-spacing:.09em;font-weight:700">RÉPUBLIQUE TOGOLAISE</div>
    <div style="font-size:1.08rem;font-weight:800;color:#fff;line-height:1.2">Mobilité et<br>sécurité routière</div>
  </div>
</div>
""", unsafe_allow_html=True)

nav = st.navigation(pages)

nav.run()

# Le bloc « Sources » est rendu après la page pour apparaître sous les filtres de la barre latérale.
with st.sidebar:
    st.markdown(
        """
<div style="margin-top:1.3rem;padding-top:.9rem;border-top:1px solid rgba(255,255,255,.12);font-size:.73rem;color:#9FB8AC;line-height:1.55">
<b style="color:#E6F0EA">Sources</b><br>
Géoportail Open Data du Togo · séries sectorielles transport · RGPH-5 2022 (INSEED) · geoBoundaries<br><br>
<b style="color:#E6F0EA">Auteur</b><br>SADJINA Christ · octobre 2026<br>
<span style="color:#4ADE80">Data Challenge · Défi 1</span>
</div>
""", unsafe_allow_html=True)

