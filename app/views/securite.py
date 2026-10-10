import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from lib import data as D
from lib.ui import C, fmt, header, insight, kpi_row, plotly, section, source

D.sidebar_filters()
k, secu, parc = D.kpi(), D.securite(), D.parc()

header("Sécurité routière : 7 507 accidents et 683 morts en 2022",
       "Accidents, morts et blessés de 2010 à 2022, rapportés à la population et au nombre de véhicules immatriculés.")

s22 = secu[secu.annee == 2022].iloc[0]
s10 = secu[secu.annee == 2010].iloc[0]
pire = secu.loc[secu.accidents.idxmax()]

section("Bilan 2022", "Dernière année publiée · taux recalculés sur la population de l'année")
kpi_row([
    {"label": "Accidents", "value": fmt(s22.accidents), "tone": "red",
     "sub": f"+{fmt((s22.accidents/s10.accidents-1)*100, 0)} % depuis 2010 · plus haut niveau depuis {int(pire.annee)}",
     "source": "Séries sectorielles transport, 2010-2022"},
    {"label": "Morts", "value": fmt(s22.morts), "tone": "red",
     "sub": f"{fmt(s22.morts_100k, 1)} pour 100 000 habitants · près de 2 morts par jour",
     "source": "Séries sectorielles transport"},
    {"label": "Blessés", "value": fmt(s22.blesses), "tone": "red",
     "sub": f"{fmt(s22.blesses_100k, 1)} pour 100 000 habitants",
     "source": "Séries sectorielles transport"},
    {"label": "Létalité", "value": fmt(s22.letalite_pct, 1, " %"), "tone": "gold",
     "sub": f"morts ÷ accidents · {fmt(s10.letalite_pct, 1)} % en 2010 — la létalité a reculé d'un tiers",
     "source": "Calcul à partir des séries publiées"},
    {"label": "Victimes totales", "value": fmt(s22.victimes), "tone": "red",
     "sub": "morts et blessés cumulés dans l'année, soit 29 personnes par jour",
     "source": "Morts + blessés, 2022"},
])

insight(
    "<b>Avertissement de lecture.</b> La source publie une série intitulée « Accidents mortels /100 000 hab » qui vaut 92,7 en 2022. "
    "Or 7 507 accidents ÷ 8 095 498 habitants × 100 000 = <b>92,7</b> : cette série compte en réalité <b>tous les accidents</b>, "
    "pas les seuls accidents mortels (vérifié également sur 2010). Le véritable taux de mortalité routière est de "
    f"<b>{fmt(s22.morts_100k, 1)} morts pour 100 000 habitants</b>. Tous les taux affichés ici sont recalculés à partir des "
    "effectifs bruts et de la population implicite de la source.", "gold")

c1, c2 = st.columns([1.35, 1])
with c1:
    st.markdown("### Accidents, morts et blessés depuis 2010")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=secu.annee, y=secu.blesses, name="Blessés", marker_color="#F0ADA6",
                         hovertemplate="%{x} : %{y:,.0f} blessés<extra></extra>"))
    fig.add_trace(go.Bar(x=secu.annee, y=secu.morts, name="Morts", marker_color=C["red"],
                         hovertemplate="%{x} : %{y:,.0f} morts<extra></extra>"))
    fig.add_trace(go.Scatter(x=secu.annee, y=secu.accidents, name="Accidents", mode="lines+markers",
                             line=dict(color=C["green_dark"], width=3),
                             hovertemplate="%{x} : %{y:,.0f} accidents<extra></extra>"))
    fig.add_vrect(x0=2014.5, x1=2015.5, fillcolor=C["gold"], opacity=0.12, line_width=0,
                  annotation_text="2015 : rupture de série", annotation_position="top left", annotation_font_size=10)
    fig.update_layout(barmode="stack", yaxis_title="Personnes / accidents", xaxis=dict(dtick=1), legend_y=1.1)
    plotly(fig, 400)
    source("Séries sectorielles transport, 2010-2022")
with c2:
    st.markdown("### Taux pour 100 000 habitants")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=secu.annee, y=secu.accidents_100k, name="Accidents", mode="lines+markers",
                             line=dict(color=C["green_dark"], width=3), hovertemplate="%{x} : %{y:.1f}<extra>Accidents</extra>"))
    fig.add_trace(go.Scatter(x=secu.annee, y=secu.blesses_100k, name="Blessés", mode="lines+markers",
                             line=dict(color=C["gold"], width=2), hovertemplate="%{x} : %{y:.1f}<extra>Blessés</extra>"))
    fig.add_trace(go.Scatter(x=secu.annee, y=secu.morts_100k, name="Morts", mode="lines+markers",
                             line=dict(color=C["red"], width=3), hovertemplate="%{x} : %{y:.1f}<extra>Morts</extra>"))
    fig.update_layout(yaxis_title="Pour 100 000 habitants", xaxis=dict(dtick=2, title=""), legend_y=1.1, hovermode="x unified")
    plotly(fig, 400)
    source("Effectifs ÷ population implicite de la source × 100 000")

insight(
    f"<b>Plus d'accidents, mais moins mortels.</b> Le nombre d'accidents a plus que doublé depuis 2010 "
    f"({fmt(s10.accidents)} → {fmt(s22.accidents)}) et dépasse depuis 2020 le niveau d'avant la rupture de série de 2015. "
    f"Le taux de mortalité, lui, reste quasi stable — {fmt(s10.morts_100k, 1)} morts pour 100 000 habitants en 2010, "
    f"{fmt(s22.morts_100k, 1)} en 2022, après un pic à {fmt(secu.morts_100k.max(), 1)} en 2014. "
    f"Ce qui recule nettement, c'est la <b>létalité</b> : {fmt(s10.letalite_pct, 1)} % des accidents étaient mortels en 2010, "
    f"{fmt(s22.letalite_pct, 1)} % en 2022. Autrement dit, on survit mieux à un accident qu'il y a dix ans, mais on en a "
    "beaucoup plus : les soins et l'équipement progressent plus vite que la prévention.")

section("Exposition au risque", "Accidents rapportés aux véhicules immatriculés dans l'année")
c3, c4 = st.columns([1, 1])
with c3:
    tot = parc[parc.type == "Total"].set_index("annee").value
    d = secu[secu.annee.isin(tot.index)].copy()
    d["vehicules"] = d.annee.map(tot)
    d["acc_1000v"] = (d.accidents / d.vehicules * 1000).round(1)
    fig = go.Figure(go.Scatter(x=d.annee, y=d.acc_1000v, mode="lines+markers", line=dict(color=C["blue"], width=3),
                               fill="tozeroy", fillcolor="rgba(47,102,144,.10)",
                               customdata=d[["accidents", "vehicules"]].values,
                               hovertemplate="%{x} : %{y:.1f} accidents pour 1 000 véhicules immatriculés"
                                             "<br>%{customdata[0]:,.0f} accidents · %{customdata[1]:,.0f} véhicules<extra></extra>"))
    fig.update_layout(title="Accidents pour 1 000 véhicules immatriculés dans l'année",
                      yaxis_title="Accidents / 1 000 véhicules", xaxis=dict(dtick=2, title=""))
    plotly(fig, 340)
    source("Accidents ÷ véhicules immatriculés dans l'année × 1 000 — indicateur d'exposition, non de parc en circulation")
with c4:
    st.markdown("**Lecture des trois mesures**")
    insight("<b>En valeur absolue</b>, la situation se dégrade : 7 507 accidents en 2022, le plus haut niveau "
            "depuis 2012, et 683 morts.", "red")
    insight("<b>Rapportée à la population</b>, elle est stable depuis 2020 autour de 92 accidents pour "
            "100 000 habitants, et la mortalité reste sous son niveau de 2010.", "gold")
    insight("<b>Rapportée aux véhicules</b>, elle s'améliore nettement : le risque par véhicule mis en circulation "
            "diminue sur la période. La hausse des accidents suit d'abord la croissance du parc.")

with st.expander("Table des données de sécurité routière (2010-2022)"):
    t = secu.rename(columns={"annee": "Année", "accidents": "Accidents", "morts": "Morts", "blesses": "Blessés",
                             "victimes": "Victimes", "accidents_100k": "Accidents/100k", "morts_100k": "Morts/100k",
                             "blesses_100k": "Blessés/100k", "letalite_pct": "Létalité (%)",
                             "population_implicite": "Population implicite"})
    st.dataframe(t, hide_index=True, use_container_width=True)
    st.download_button("Télécharger (CSV)", t.to_csv(index=False).encode("utf-8-sig"),
                       "securite_routiere_togo.csv", "text/csv")
st.caption("Rupture de série en 2015 : les effectifs publiés cette année-là sont environ deux fois inférieurs aux années "
           "voisines, pour toutes les catégories à la fois. Cette anomalie est signalée mais non corrigée — les données "
           "sont présentées telles que publiées.")
