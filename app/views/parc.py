import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from lib import data as D
from lib.ui import C, fmt, header, insight, kpi_row, plotly, section, source

D.sidebar_filters()
k, parc, permis, tr = D.kpi(), D.parc(), D.permis(), D.transport()

header("Immatriculations et permis : un parc qui bascule vers le deux-roues",
       "Évolution des véhicules immatriculés par type (1990-2022) et des permis de conduire délivrés par catégorie (2007-2022).")

tot = parc[parc.type == "Total"].set_index("annee").value
deux = parc[parc.type == "Deux-roues"].set_index("annee").value
part90 = deux.get(1990, 0) / tot.get(1990, 1) * 100
cumul = int(tot.loc[1990:2022].sum())

section("Vingt ans de motorisation", "Les séries publiées comptent les véhicules immatriculés chaque année, et non le parc en circulation")
kpi_row([
    {"label": "Véhicules immatriculés en 2022", "value": fmt(k["parc_total"]),
     "sub": f"contre {fmt(k['parc_1990'])} en 1990, soit ×{fmt(k['parc_total']/k['parc_1990'], 1)}",
     "source": "Immatriculations annuelles, 1990-2022"},
    {"label": "Part des deux-roues", "value": fmt(k["part_deux_roues"], 1, " %"), "tone": "gold",
     "sub": f"{fmt(part90, 1)} % en 1990 — la motorisation du pays s'est faite à deux roues",
     "source": "Immatriculations par type de véhicule"},
    {"label": "Cumul 1990-2022", "value": fmt(cumul),
     "sub": "véhicules immatriculés sur la période, hors sorties de parc (non publiées)",
     "source": "Somme des immatriculations annuelles"},
    {"label": "Permis délivrés en 2022", "value": fmt(k["permis_total"]),
     "sub": f"×{fmt(k['permis_total']/6931, 1)} depuis 2007 ({fmt(6931)} permis)",
     "source": "Examens du permis de conduire, 2007-2022"},
    {"label": "Permis moto (A) en 2022", "value": fmt(k["permis_moto"]), "tone": "red",
     "sub": f"{fmt(k['permis_moto']/k['permis_total']*100, 1)} % des permis, pour {fmt(k['part_deux_roues'], 1)} % des véhicules",
     "source": "Permis délivrés par catégorie"},
])

c1, c2 = st.columns([1.3, 1])
with c1:
    st.markdown("### Immatriculations annuelles par type de véhicule")
    d = parc[parc.type != "Total"].copy()
    order = d.groupby("type").value.sum().sort_values(ascending=False).index.tolist()
    fig = px.area(d, x="annee", y="value", color="type", category_orders={"type": order},
                  color_discrete_sequence=[C["red"], C["green"], C["gold"], C["blue"], "#8FBFA3", "#B8742A", "#B8C4BE"],
                  labels={"value": "Véhicules immatriculés", "annee": "", "type": ""})
    fig.update_traces(hovertemplate="%{x} : %{y:,.0f}<extra>%{fullData.name}</extra>")
    fig.update_layout(legend_y=1.1, xaxis=dict(dtick=4))
    plotly(fig, 400)
    source("Immatriculations par type de véhicule, 1990-2022 · « Voitues » corrigé en « Voitures » dans la source")
with c2:
    st.markdown("### La bascule vers le deux-roues")
    sh = (deux / tot * 100).dropna()
    fig = go.Figure(go.Scatter(x=sh.index, y=sh.values, mode="lines", line=dict(color=C["red"], width=3),
                               fill="tozeroy", fillcolor="rgba(200,69,59,.10)",
                               hovertemplate="%{x} : %{y:.1f} %% de deux-roues<extra></extra>"))
    fig.add_hline(y=50, line_dash="dot", line_color=C["muted"], annotation_text="50 %", annotation_position="top left")
    fig.update_layout(yaxis=dict(title="Part des deux-roues (%)", ticksuffix=" %"), xaxis=dict(dtick=4, title=""))
    plotly(fig, 400)
    source("Deux-roues ÷ total des véhicules immatriculés dans l'année")

insight(
    f"<b>En 1990, les deux-roues représentaient {fmt(part90, 1)} % des immatriculations ; en 2022, {fmt(k['part_deux_roues'], 1)} %.</b> "
    "La motorisation du Togo ne s'est pas faite en voitures mais en motos — un mode plus accessible, plus souple en ville, "
    "et nettement plus exposé en cas de choc. Toute politique de sécurité routière qui ne cible pas le deux-roues manque sa cible.", "red")

section("Formation des conducteurs", "Permis délivrés par catégorie aux examens")
c3, c4 = st.columns([1.3, 1])
with c3:
    d = permis[permis.categorie != "Total"]
    fig = px.bar(d, x="annee", y="value", color="categorie",
                 color_discrete_sequence=[C["green_dark"], C["red"], C["gold"], C["blue"], "#8FBFA3", "#B8C4BE"],
                 labels={"value": "Permis délivrés", "annee": "", "categorie": ""})
    fig.update_traces(hovertemplate="%{x} : %{y:,.0f}<extra>%{fullData.name}</extra>")
    fig.update_layout(barmode="stack", legend_y=1.1, xaxis=dict(dtick=2))
    plotly(fig, 380)
    source("Permis de conduire délivrés par catégorie, 2007-2022")
with c4:
    st.markdown("**Le décalage moto, année par année**")
    pm = permis[permis.categorie == "Moto (A)"].set_index("annee").value
    ratio = pd.DataFrame({"annee": sorted(set(pm.index) & set(deux.index))})
    ratio["motos"] = ratio.annee.map(deux)
    ratio["permis"] = ratio.annee.map(pm)
    ratio["motos_par_permis"] = (ratio.motos / ratio.permis).round(1)
    fig = go.Figure(go.Bar(x=ratio.annee, y=ratio.motos_par_permis, marker_color=C["red"],
                           text=[fmt(v, 0) for v in ratio.motos_par_permis], textposition="outside", cliponaxis=False,
                           customdata=ratio[["motos", "permis"]].values,
                           hovertemplate="%{x} : %{y:.1f} motos immatriculées par permis moto délivré"
                                         "<br>%{customdata[0]:,.0f} motos · %{customdata[1]:,.0f} permis<extra></extra>"))
    fig.update_layout(yaxis_title="Motos immatriculées par permis moto", xaxis=dict(dtick=1, title=""))
    plotly(fig, 380)
    source("Deux-roues immatriculés ÷ permis moto (A) délivrés, par année")

r22 = ratio[ratio.annee == 2022].iloc[0] if 2022 in set(ratio.annee) else None
if r22 is not None:
    insight(
        f"<b>En 2022, {fmt(r22.motos_par_permis, 0)} motos ont été immatriculées pour un seul permis moto délivré.</b> "
        "Le ratio s'est amélioré cette année-là — 4 837 permis A contre 211 en 2021 — mais il reste très déséquilibré, "
        "et les années 2018, 2020 et 2021 montrent que cet effort n'est pas encore installé dans la durée.", "gold")

with st.expander("Autres séries de transport disponibles (fret, trafic, rail, premières mises en circulation)"):
    sel = st.multiselect("Indicateurs", sorted(tr.libelle.unique()),
                         default=["Fret routier", "Trafic passagers", "Trafic marchandises"])
    if sel:
        d = tr[tr.libelle.isin(sel)]
        fig = px.line(d, x="annee", y="value", color="libelle", markers=True,
                      labels={"value": "", "annee": "", "libelle": ""})
        fig.update_layout(legend_y=1.12)
        plotly(fig, 330)
    st.caption("Ces séries proviennent du même fichier que les accidents : un export qui regroupe 13 indicateurs de transport "
               "sans colonne de thème. Elles sont fournies ici pour exploration, sans être mobilisées dans le diagnostic principal.")
