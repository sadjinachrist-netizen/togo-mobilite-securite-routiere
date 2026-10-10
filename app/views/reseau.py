import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from lib import data as D
from lib.ui import C, ETAT_COLORS, REGION_COLORS, SEQ, SEQ_RED, fmt, header, insight, kpi_row, plotly, section, source

f = D.sidebar_filters()
k, reg, pref = D.kpi(), D.regions(), D.prefectures()
ro = D.apply_routes(f)
geo_routes, geo_pref = D.geo_routes(), D.geo_prefectures()
etat_nat, etat_rn = D.etat_national(), D.etat_par_rn()

header("Le réseau routier classé : 3 373 km, inégalement répartis et inégalement entretenus",
       "Tracé géolocalisé des routes classées, état du réseau en 2020 et densité routière rapportée à la population.")

km = ro.km.sum()
rev = ro[ro.revetue].km.sum()
section("Le réseau", f"Périmètre : {f['scope']} · {len(ro)} tronçons géolocalisés")
kpi_row([
    {"label": "Longueur du réseau classé", "value": fmt(km, 0, " km"),
     "sub": f"{len(ro)} tronçons · longueurs calculées sur les tracés (formule de haversine)",
     "source": "Géoportail Open Data · routes classées, 12/2024"},
    {"label": "Réseau revêtu", "value": fmt(rev / km * 100 if km else 0, 1, " %"),
     "sub": f"{fmt(rev, 0)} km bitumés, bétonnés ou pavés sur {fmt(km, 0)} km",
     "source": "Champ « revêtement » des tronçons"},
    {"label": "Routes nationales", "value": fmt(ro[ro.route_type.str.startswith('Route nationale')].km.sum(), 0, " km"),
     "sub": f"{fmt(ro[ro.route_type == 'Voirie urbaine'].km.sum(), 0)} km de voirie urbaine · {fmt(ro[ro.route_type == 'Piste rurale'].km.sum(), 0)} km de pistes rurales",
     "source": "Champ « type de route »"},
    {"label": "En mauvais état", "value": fmt(k["km_etat"].get("Mauvais état", 0), 0, " km"), "tone": "red",
     "sub": f"soit {fmt(k['km_etat'].get('Mauvais état', 0)/sum(k['km_etat'].values())*100, 0)} % du réseau évalué en 2020",
     "source": "2020 · état du réseau par tronçon"},
    {"label": "En travaux", "value": fmt(k["km_etat"].get("Travaux en cours", 0), 0, " km"), "tone": "gold",
     "sub": f"{fmt(k['km_etat'].get('Bon état', 0), 0)} km en bon état · {fmt(k['km_etat'].get('État moyen', 0), 0)} km en état moyen",
     "source": "2020 · état du réseau par tronçon"},
])

# ------------------------------------------------------------------ carte
section("Carte du réseau", "Choisissez la variable qui colore les tronçons ; survolez une route pour son détail")
COLORBY = {"État du réseau (2020)": ("etat", ETAT_COLORS),
           "Type de route": ("type", {"Route nationale revêtue": C["green_dark"], "Route nationale non revêtue": C["gold"],
                                      "Voirie urbaine": C["blue"], "Piste rurale": C["red"]}),
           "Revêtement": ("revetement", {"Bitume": C["green_dark"], "Beton": "#3A9A6E", "Pavé": "#8FBFA3",
                                         "Gravier amenagé": "#BFE0D0", "Terre amenagée": C["gold"],
                                         "Gravier non amenagé": "#B8742A", "Terre non amenagée": C["red"]})}
m1, m2 = st.columns([1, 1.15])
with m1:
    colorby = st.radio("Colorer les routes par", list(COLORBY), horizontal=False, key="r_colorby")
with m2:
    fond = st.selectbox("Fond de préfecture", ["Aucun", "Mètres de route par habitant", "Part du réseau revêtue (%)",
                                               "Longueur du réseau (km)"], key="r_fond")
prop, colmap = COLORBY[colorby]

keep = set(ro.FID)
fig = go.Figure()

if fond != "Aucun":
    col = {"Mètres de route par habitant": ("m_route_par_hab", SEQ, "m / hab."),
           "Part du réseau revêtue (%)": ("part_revetue", SEQ, "% revêtu"),
           "Longueur du réseau (km)": ("km_routes", SEQ, "km")}[fond]
    g = pref.groupby("map_key", as_index=False).agg(libelle=("prefecture", lambda s: " + ".join(s)),
                                                    population=("population", "sum"), km_routes=("km_routes", "sum"),
                                                    km_revetues=("km_revetues", "sum"))
    g["m_route_par_hab"] = (g.km_routes * 1000 / g.population).round(2)
    g["part_revetue"] = (g.km_revetues / g.km_routes.where(g.km_routes > 0) * 100).round(1)
    fig.add_trace(go.Choroplethmap(geojson=geo_pref, locations=g.map_key, featureidkey="properties.map_key",
                                   z=g[col[0]], colorscale=col[1], marker_line_color="white", marker_line_width=0.6,
                                   marker_opacity=0.65, customdata=g[["libelle", "km_routes", "population"]].values,
                                   colorbar=dict(title=dict(text=col[2], side="right"), orientation="h", thickness=9,
                                                 len=0.5, y=0.99, x=0.74, yanchor="top", bgcolor="rgba(255,255,255,.85)",
                                                 tickfont_size=10),
                                   hovertemplate="<b>%{customdata[0]}</b><br>" + col[2] + " : %{z}"
                                                 "<br>%{customdata[1]:,.0f} km · %{customdata[2]:,.0f} hab.<extra></extra>"))

for val, color in colmap.items():
    lats, lons, names = [], [], []
    for ft in geo_routes["features"]:
        p = ft["properties"]
        if p.get(prop) != val or (keep and ft["id"] not in keep and len(keep) < 799):
            continue
        for line in ft["geometry"]["coordinates"]:
            lons += [c[0] for c in line] + [None]
            lats += [c[1] for c in line] + [None]
        names.append(p["nom"])
    if not lats:
        continue
    fig.add_trace(go.Scattermap(lat=lats, lon=lons, mode="lines", name=f"{val} ({len(names)})",
                                line=dict(width=2.2, color=color), hoverinfo="skip"))

fig.update_layout(map=dict(style="carto-positron", center={"lat": 8.6, "lon": 1.0}, zoom=6.15),
                  margin=dict(l=0, r=0, t=0, b=0),
                  legend=dict(orientation="v", y=0.985, x=0.01, yanchor="top", xanchor="left",
                              bgcolor="rgba(255,255,255,.88)", font_size=11))
plotly(fig, 620)
source("Tracés : Géoportail Open Data, routes classées (12/2024), simplifiés à ~150 m pour l'affichage · "
       "État : table nationale 2020, rattachée aux tracés par numéro de route nationale · "
       "Contours : geoBoundaries (OSM, 2017)")

insight(
    "<b>Comment l'état a été rattaché aux tracés.</b> L'état du réseau est publié par tronçon administratif nommé "
    "(« RN1 BABAME-SOKODE », 87 tronçons), tandis que les tracés géolocalisés portent un autre libellé. Les deux ont été "
    f"joints par <b>numéro de route nationale</b> : les 50 routes nationales de la table d'état sont toutes retrouvées, et "
    f"<b>{(D.routes().etat_dominant != 'Non renseigné').sum()} tronçons sur 799</b> reçoivent ainsi un état. Chaque tronçon se voit attribuer "
    "l'<b>état dominant de sa route nationale</b> — une approximation assumée : l'état réel peut varier le long d'un même axe.", "gold")

# ------------------------------------------------------------------ état et territoires
c1, c2 = st.columns([1, 1.25])
with c1:
    st.markdown("### État du réseau évalué en 2020")
    e = etat_nat.groupby("etat_lib", as_index=False).km.sum().sort_values("km", ascending=False)
    fig = go.Figure(go.Pie(labels=e.etat_lib, values=e.km, hole=0.58, sort=False,
                           marker_colors=[ETAT_COLORS.get(x, "#B8C4BE") for x in e.etat_lib],
                           texttemplate="%{value:,.0f} km<br>%{percent}",
                           hovertemplate="<b>%{label}</b><br>%{value:,.0f} km<extra></extra>"))
    fig.update_layout(legend=dict(orientation="v", y=0.5, x=1.0),
                      annotations=[dict(text=f"{e.km.sum():,.0f} km".replace(",", " "), x=0.5, y=0.5, showarrow=False,
                                        font_size=15, font_color=C["green_dark"])], margin=dict(t=10))
    plotly(fig, 330)
    source("Table « état du réseau » 2020, routes revêtues et en terre, toutes catégories")
with c2:
    st.markdown("### Les dix routes nationales les plus dégradées")
    d = etat_rn.pivot_table(index="rn", columns="etat", values="km", aggfunc="sum").fillna(0)
    for c in ["BON", "MOYEN", "MAUVAIS", "TRAVAUX"]:
        if c not in d.columns:
            d[c] = 0
    d["total"] = d[["BON", "MOYEN", "MAUVAIS", "TRAVAUX"]].sum(axis=1)
    d = d[d.total >= 20]
    d["part_degradee"] = (d.MAUVAIS / d.total * 100).round(1)
    d = d.sort_values("part_degradee", ascending=False).head(10).reset_index()
    fig = go.Figure()
    for c, lab in [("BON", "Bon état"), ("MOYEN", "État moyen"), ("TRAVAUX", "Travaux en cours"), ("MAUVAIS", "Mauvais état")]:
        fig.add_trace(go.Bar(y="RN " + d.rn, x=d[c], name=lab, orientation="h", marker_color=ETAT_COLORS[lab],
                             customdata=d[["total"]].values,
                             hovertemplate="<b>%{y}</b> · " + lab + " : %{x:,.0f} km sur %{customdata[0]:,.0f} km<extra></extra>"))
    fig.update_layout(barmode="stack", barnorm="percent", yaxis=dict(autorange="reversed", title=""),
                      xaxis=dict(title="Répartition des kilomètres (%)", ticksuffix=" %"), legend_y=1.12)
    plotly(fig, 330)
    source("Routes nationales de plus de 20 km évaluées, classées par part de kilomètres en mauvais état")

section("Densité routière par territoire", "Le réseau classé rapporté à la population")
d = pref.sort_values("m_route_par_hab")
fig = go.Figure(go.Bar(x=d.prefecture, y=d.m_route_par_hab,
                       marker_color=[REGION_COLORS[r] for r in d.region],
                       customdata=d[["region", "km_routes", "population", "part_revetue"]].values,
                       hovertemplate="<b>%{x}</b> (%{customdata[0]})<br>%{y:.2f} m de route par habitant"
                                     "<br>%{customdata[1]:,.0f} km · %{customdata[2]:,.0f} hab. · %{customdata[3]:.0f} %% revêtu<extra></extra>"))
fig.add_hline(y=k["m_route_par_hab"], line_dash="dot", line_color=C["muted"],
              annotation_text=f"Moyenne nationale : {fmt(k['m_route_par_hab'], 2)} m", annotation_position="top left")
fig.update_layout(xaxis_tickangle=-45, xaxis_title="", yaxis_title="Mètres de route classée par habitant")
plotly(fig, 380)
source("Longueur du réseau classé ÷ population RGPH-5 2022, par préfecture")

insight(
    "<b>Deux lectures opposées du même chiffre.</b> Le Grand Lomé affiche 0,07 m de route classée par habitant, les "
    "préfectures rurales de la Kara jusqu'à 2 m. Cela ne signifie pas que Lomé est mal dotée : le réseau <i>classé</i> "
    "recense les routes nationales et grandes voiries, pas le maillage urbain local. L'indicateur mesure donc "
    "<b>l'accès au réseau structurant</b> — pertinent pour l'enclavement rural, trompeur pour la congestion urbaine. "
    "Mô, seule préfecture sans aucune route nationale classée recensée, est à ce titre le territoire le plus isolé du pays.", "gold")

with st.expander("Table du réseau par préfecture"):
    t = pref[["prefecture", "region", "population", "km_routes", "km_revetues", "part_revetue", "m_route_par_hab", "segments"]]
    t = t.rename(columns={"prefecture": "Préfecture", "region": "Région", "population": "Population",
                          "km_routes": "Km de réseau", "km_revetues": "Km revêtus", "part_revetue": "% revêtu",
                          "m_route_par_hab": "m / habitant", "segments": "Tronçons"})
    st.dataframe(t.sort_values("Km de réseau", ascending=False), hide_index=True, use_container_width=True)
    st.download_button("Télécharger (CSV)", t.to_csv(index=False).encode("utf-8-sig"), "reseau_par_prefecture.csv", "text/csv")
