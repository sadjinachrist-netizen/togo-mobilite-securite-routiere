import plotly.graph_objects as go
import streamlit as st

from lib import data as D
from lib.ui import C, REGION_COLORS, fmt, header, insight, kpi_row, plotly, section, source

f = D.sidebar_filters()
k, reg, pref = D.kpi(), D.regions(), D.prefectures()
secu, parc, permis = D.securite(), D.parc(), D.permis()

header("Le Togo roule à moto, mais forme des automobilistes",
       "Diagnostic de la mobilité et de la sécurité routière à partir des données ouvertes : immatriculations, permis, "
       "accidents, réseau routier classé, auto-écoles et population 2022.")

section("Sécurité routière", f"Dernière année disponible : {k['annee_securite']}")
kpi_row([
    {"label": "Accidents de la circulation", "value": fmt(k["accidents"]), "tone": "red",
     "sub": f"{fmt(k['accidents_100k'], 1)} pour 100 000 habitants — plus haut niveau depuis 2012",
     "source": f"{k['annee_securite']} · séries sectorielles transport"},
    {"label": "Morts sur la route", "value": fmt(k["morts"]), "tone": "red",
     "sub": f"{fmt(k['morts_100k'], 1)} pour 100 000 habitants · létalité {fmt(k['letalite_pct'], 1)} %",
     "source": f"{k['annee_securite']} · séries sectorielles transport"},
    {"label": "Blessés", "value": fmt(k["blesses"]), "tone": "red",
     "sub": f"{fmt(k['blesses'] + k['morts'])} victimes au total dans l'année",
     "source": f"{k['annee_securite']} · séries sectorielles transport"},
    {"label": "Véhicules immatriculés dans l'année", "value": fmt(k["parc_total"]),
     "sub": f"dont {fmt(k['part_deux_roues'], 1, ' %')} de deux-roues · {fmt(k['parc_1990'])} en 1990",
     "source": "2022 · immatriculations annuelles"},
    {"label": "Permis délivrés dans l'année", "value": fmt(k["permis_total"]),
     "sub": f"dont {fmt(k['permis_moto'])} permis moto (A) et {fmt(k['permis_voiture'])} permis voiture (B)",
     "source": "2022 · examens du permis de conduire"},
])

insight(
    f"<b>Le déséquilibre central.</b> Les deux-roues représentent <b>{fmt(k['part_deux_roues'], 1)} %</b> des véhicules "
    f"immatriculés en 2022 — {fmt(k['parc_deux_roues'])} motos sur {fmt(k['parc_total'])} véhicules. Mais seuls "
    f"<b>{fmt(k['permis_moto'])} permis moto</b> ont été délivrés, contre {fmt(k['permis_voiture'])} permis voiture. "
    "Le pays motorise sa population à deux roues et la forme à quatre.", "red")

section("Réseau routier et formation", "Infrastructures classées et offre de formation, rapportées à la population")
kpi_row([
    {"label": "Réseau routier classé", "value": fmt(k["km_routes"], 0, " km"),
     "sub": f"{k['segments']} tronçons géolocalisés · {fmt(k['part_revetue'], 1, ' %')} revêtus",
     "source": "Géoportail Open Data · routes classées, 12/2024"},
    {"label": "Routes en mauvais état ou en travaux", "value": fmt(k["km_etat"].get("Mauvais état", 0) + k["km_etat"].get("Travaux en cours", 0), 0, " km"),
     "tone": "gold",
     "sub": f"{fmt(k['km_etat'].get('Bon état', 0), 0)} km en bon état sur {fmt(sum(k['km_etat'].values()), 0)} km évalués",
     "source": "2020 · état du réseau par tronçon"},
    {"label": "Mètres de route par habitant", "value": fmt(k["m_route_par_hab"], 2, " m"),
     "sub": "0,07 m au Grand Lomé contre 0,75 m dans la Kara",
     "source": "Réseau classé ÷ population RGPH-5 2022"},
    {"label": "Auto-écoles recensées", "value": fmt(k["auto_ecoles"]), "tone": "red",
     "sub": f"dont <b>{fmt(k['auto_ecoles_non_agreees'])} non agréées</b> ({fmt(k['part_non_agreees'], 1)} %) · {fmt(k['part_auto_ecoles_maritime'], 1)} % dans le Grand Lomé et le Maritime",
     "source": "Géoportail Open Data · auto-écoles, 01/2025"},
    {"label": "Préfectures sans auto-école agréée", "value": f"{k['prefectures_sans_auto_ecole_agreee']} / 39", "tone": "red",
     "sub": f"dont {k['prefectures_sans_auto_ecole']} sans aucune auto-école — {fmt(k['population_sans_auto_ecole'])} habitants",
     "source": "Croisement auto-écoles × RGPH-5 2022"},
])

insight(
    f"<b>Une auto-école sur deux n'est pas agréée</b> ({fmt(k['auto_ecoles_non_agreees'])} sur {fmt(k['auto_ecoles'])}), et "
    f"<b>{k['prefectures_sans_auto_ecole_agreee']} préfectures sur 39 n'en comptent aucune qui le soit</b>. Là où la formation "
    "est absente ou non encadrée, la conduite s'apprend sans contrôle — au moment précis où le parc deux-roues explose.", "red")

# ------------------------------------------------------------------ graphiques
c1, c2 = st.columns([1.25, 1])
with c1:
    st.markdown("### Immatriculations et accidents suivent la même pente")
    tot = parc[parc.type == "Total"].sort_values("annee")
    tot = tot[tot.annee >= 2010]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=tot.annee, y=tot.value, name="Véhicules immatriculés dans l'année",
                         marker_color="#A8C8B6", hovertemplate="%{x} : %{y:,.0f} véhicules<extra></extra>"))
    fig.add_trace(go.Scatter(x=secu.annee, y=secu.accidents, name="Accidents de la circulation", yaxis="y2",
                             line=dict(color=C["red"], width=3), mode="lines+markers",
                             hovertemplate="%{x} : %{y:,.0f} accidents<extra></extra>"))
    fig.update_layout(yaxis=dict(title="Véhicules immatriculés"), xaxis=dict(dtick=2),
                      yaxis2=dict(title="Accidents de la circulation", overlaying="y", side="right", showgrid=False, rangemode="tozero"),
                      legend_y=1.1)
    plotly(fig, 380)
    source("Immatriculations annuelles (1990-2022) et sécurité routière (2010-2022), séries sectorielles transport")
with c2:
    st.markdown("### Ce qui roule et ce qui est formé")
    p22 = parc[parc.annee == 2022]
    deux = float(p22[p22.type == "Deux-roues"].value.iloc[0])
    quatre = float(p22[p22.type == "Total"].value.iloc[0]) - deux
    pe22 = permis[permis.annee == 2022]
    pmoto = float(pe22[pe22.categorie == "Moto (A)"].value.iloc[0])
    pautre = float(pe22[pe22.categorie == "Total"].value.iloc[0]) - pmoto
    fig = go.Figure()
    fig.add_trace(go.Bar(y=["Permis délivrés", "Véhicules immatriculés"], x=[pmoto, deux], name="Deux-roues / permis moto (A)",
                         orientation="h", marker_color=C["red"],
                         text=[f"{pmoto/(pmoto+pautre)*100:.0f} %", f"{deux/(deux+quatre)*100:.0f} %"],
                         textposition="inside", insidetextanchor="middle", textfont_color="white",
                         hovertemplate="%{y} · deux-roues : %{x:,.0f}<extra></extra>"))
    fig.add_trace(go.Bar(y=["Permis délivrés", "Véhicules immatriculés"], x=[pautre, quatre], name="Quatre-roues et plus / autres permis",
                         orientation="h", marker_color=C["green"],
                         text=[f"{pautre/(pmoto+pautre)*100:.0f} %", f"{quatre/(deux+quatre)*100:.0f} %"],
                         textposition="inside", insidetextanchor="middle", textfont_color="white",
                         hovertemplate="%{y} · autres : %{x:,.0f}<extra></extra>"))
    fig.update_layout(barmode="stack", barnorm="percent", xaxis=dict(title="Répartition (%)", ticksuffix=" %"),
                      yaxis=dict(title=""), legend_y=1.14)
    plotly(fig, 380)
    source("Année 2022 · immatriculations par type et permis délivrés par catégorie")

section("Territoires", "Les trois déséquilibres régionaux, rapportés à la population")
c3, c4, c5 = st.columns(3)
with c3:
    d = reg.sort_values("m_route_par_hab")
    fig = go.Figure(go.Bar(x=d.m_route_par_hab, y=d.region.astype(str), orientation="h",
                           marker_color=[REGION_COLORS[r] for r in d.region.astype(str)],
                           text=[fmt(v, 2) for v in d.m_route_par_hab], textposition="outside", cliponaxis=False,
                           customdata=d[["km_routes", "population"]].values,
                           hovertemplate="<b>%{y}</b><br>%{x:.2f} m de route par habitant<br>%{customdata[0]:,.0f} km · %{customdata[1]:,.0f} hab.<extra></extra>"))
    fig.update_layout(title="Mètres de route classée par habitant", xaxis=dict(showticklabels=False, title=""),
                      yaxis_title="", margin=dict(r=55))
    plotly(fig, 310)
with c4:
    d = reg.sort_values("part_revetue")
    fig = go.Figure(go.Bar(x=d.part_revetue, y=d.region.astype(str), orientation="h",
                           marker_color=[C["red"] if v < 60 else C["gold"] if v < 80 else C["green"] for v in d.part_revetue],
                           text=[fmt(v, 0, " %") for v in d.part_revetue], textposition="outside", cliponaxis=False,
                           hovertemplate="<b>%{y}</b> : %{x:.1f} %% du réseau revêtu<extra></extra>"))
    fig.update_layout(title="Part du réseau revêtu", xaxis=dict(showticklabels=False, title=""), yaxis_title="",
                      margin=dict(r=55))
    plotly(fig, 310)
with c5:
    d = reg.sort_values("hab_par_auto_ecole", ascending=False)
    fig = go.Figure(go.Bar(x=d.hab_par_auto_ecole, y=d.region.astype(str), orientation="h",
                           marker_color=[C["red"] if v > 60000 else C["gold"] if v > 30000 else C["green"] for v in d.hab_par_auto_ecole],
                           text=[fmt(v) for v in d.hab_par_auto_ecole], textposition="outside", cliponaxis=False,
                           customdata=d[["auto_ecoles"]].values,
                           hovertemplate="<b>%{y}</b><br>%{x:,.0f} habitants par auto-école<br>%{customdata[0]} auto-école(s)<extra></extra>"))
    fig.update_layout(title="Habitants par auto-école", xaxis=dict(showticklabels=False, title=""), yaxis_title="",
                      margin=dict(r=75))
    plotly(fig, 310)
source("Réseau classé, auto-écoles recensées et population RGPH-5 2022, par région (Grand Lomé distingué du Maritime)")

gl = reg[reg.region == "Grand Lomé"].iloc[0]
pl = reg[reg.region == "Plateaux"].iloc[0]
insight(
    f"<b>Trois déséquilibres se superposent.</b> Les Savanes n'ont que {fmt(reg[reg.region=='Savanes'].part_revetue.iloc[0], 0)} % "
    f"de réseau revêtu contre {fmt(gl.part_revetue, 0)} % au Grand Lomé. Les Plateaux comptent "
    f"{fmt(pl.hab_par_auto_ecole)} habitants par auto-école contre {fmt(gl.hab_par_auto_ecole)} au Grand Lomé — "
    f"<b>un rapport de {fmt(pl.hab_par_auto_ecole / gl.hab_par_auto_ecole, 0)} à 1</b>. Et le Grand Lomé, qui concentre "
    f"{fmt(gl.part_population, 0)} % de la population, ne dispose que de {fmt(gl.part_km, 1)} % du réseau classé : "
    "l'engorgement urbain et l'enclavement rural sont deux problèmes distincts.", "gold")
