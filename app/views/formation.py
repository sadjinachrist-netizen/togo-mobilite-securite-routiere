import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from lib import data as D
from lib.ui import C, REGION_COLORS, SEQ_RED, STATUT_COLORS, fmt, header, insight, kpi_row, plotly, section, source

f = D.sidebar_filters()
k, pref, reg = D.kpi(), D.prefectures(), D.regions()
ae = D.apply_ecoles(f)
geo_pref = D.geo_prefectures()

header("Former les conducteurs : une auto-école sur deux hors agrément, 23 préfectures sans aucune",
       "Répartition des auto-écoles géolocalisées, statut d'agrément et accès à la formation rapporté à la population.")

nb = len(ae)
agr = int(ae.agreee.sum())
section("L'offre de formation", f"Périmètre : {f['scope']} · {nb} auto-école(s)")
kpi_row([
    {"label": "Auto-écoles recensées", "value": fmt(nb),
     "sub": f"{fmt(k['hab_par_auto_ecole'])} habitants par auto-école au niveau national",
     "source": "Géoportail Open Data · auto-écoles, 01/2025"},
    {"label": "Non agréées", "value": fmt(int((ae.statut == 'Non agréée').sum())), "tone": "red",
     "sub": f"{fmt((ae.statut == 'Non agréée').mean()*100 if nb else 0, 1)} % de l'offre recensée · {int((ae.statut=='Non renseigné').sum())} statut non renseigné",
     "source": "Champ « agrégation » du jeu de données"},
    {"label": "Préfectures sans auto-école agréée", "value": f"{k['prefectures_sans_auto_ecole_agreee']} / 39", "tone": "red",
     "sub": f"dont {k['prefectures_sans_auto_ecole']} sans aucune auto-école, agréée ou non",
     "source": "Croisement auto-écoles × référentiel des 39 préfectures"},
    {"label": "Population sans auto-école", "value": fmt(k["population_sans_auto_ecole"]), "tone": "red",
     "sub": f"{fmt(k['population_sans_auto_ecole']/k['population_2022']*100, 1)} % des Togolais vivent dans une préfecture sans auto-école",
     "source": "RGPH-5 2022"},
    {"label": "Concentration", "value": fmt(k["part_auto_ecoles_maritime"], 1, " %"), "tone": "gold",
     "sub": "des auto-écoles sont dans le Grand Lomé et la région Maritime, pour 44 % de la population",
     "source": "Auto-écoles par région"},
])

insight(
    f"<b>L'agrément n'est pas la règle, c'est l'exception dans la plupart des régions.</b> Au niveau national, "
    f"{fmt(k['auto_ecoles_agreees'])} auto-écoles sur {fmt(k['auto_ecoles'])} sont agréées ou antennes agréées "
    f"({fmt(k['part_agreees'], 1)} %). Dans la Centrale, deux tiers des écoles ne le sont pas ; dans les Savanes, 60 %. "
    "Comme les permis moto restent rares, une grande partie des conducteurs de deux-roues apprend donc à conduire "
    "sans formation encadrée — ni par une école agréée, ni par un examen.", "red")

# ------------------------------------------------------------------ carte
section("Où sont les auto-écoles", "Fond : habitants par auto-école agréée · points : écoles, par statut")
g = pref.groupby("map_key", as_index=False).agg(
    libelle=("prefecture", lambda s: " + ".join(s)), population=("population", "sum"),
    auto_ecoles=("auto_ecoles", "sum"), auto_ecoles_agreees=("auto_ecoles_agreees", "sum"))
g["hab_par_agreee"] = (g.population / g.auto_ecoles_agreees.where(g.auto_ecoles_agreees > 0)).round(0)
g["z"] = g.hab_par_agreee.fillna(g.hab_par_agreee.max() * 1.25)
g["lib_val"] = g.apply(lambda r: "aucune auto-école agréée" if pd.isna(r.hab_par_agreee)
                       else f"{r.hab_par_agreee:,.0f} hab. par école agréée".replace(",", " "), axis=1)

fig = go.Figure()
fig.add_trace(go.Choroplethmap(geojson=geo_pref, locations=g.map_key, featureidkey="properties.map_key", z=g.z,
                               colorscale=SEQ_RED, marker_line_color="white", marker_line_width=0.7, marker_opacity=0.8,
                               customdata=g[["libelle", "lib_val", "auto_ecoles", "auto_ecoles_agreees", "population"]].values,
                               colorbar=dict(title=dict(text="hab. / école agréée", side="right"), orientation="h",
                                             thickness=9, len=0.5, y=0.99, x=0.74, yanchor="top",
                                             bgcolor="rgba(255,255,255,.85)", tickfont_size=10),
                               hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}"
                                             "<br>%{customdata[2]} auto-école(s) dont %{customdata[3]} agréée(s)"
                                             "<br>%{customdata[4]:,.0f} habitants<extra></extra>"))
for statut, color in STATUT_COLORS.items():
    d = ae[ae.statut == statut]
    if not len(d):
        continue
    fig.add_trace(go.Scattermap(lat=d.lat, lon=d.lon, mode="markers", name=f"{statut} ({len(d)})",
                                marker=dict(size=8, color=color, opacity=0.9),
                                customdata=d[["nom", "localite", "prefecture"]].values,
                                hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]} · %{customdata[2]}"
                                              "<extra>" + statut + "</extra>"))
fig.update_layout(map=dict(style="carto-positron", center={"lat": 8.6, "lon": 1.0}, zoom=6.15),
                  margin=dict(l=0, r=0, t=0, b=0),
                  legend=dict(orientation="v", y=0.985, x=0.01, yanchor="top", xanchor="left",
                              bgcolor="rgba(255,255,255,.88)", font_size=11))
plotly(fig, 600)
source("Auto-écoles géolocalisées (Géoportail, 01/2025) · population RGPH-5 2022 · contours geoBoundaries (OSM, 2017). "
       "Les préfectures sans école agréée sont affichées à la teinte maximale.")

# ------------------------------------------------------------------ classements
c1, c2 = st.columns([1.2, 1])
with c1:
    st.markdown("### Les préfectures les plus mal desservies")
    d = pref.copy()
    d["hab_par_ae"] = d.hab_par_auto_ecole.fillna(d.population)
    d["label"] = d.apply(lambda r: "aucune" if r.auto_ecoles == 0 else fmt(r.hab_par_auto_ecole), axis=1)
    d = d.sort_values(["auto_ecoles", "population"], ascending=[True, False]).head(15)
    fig = go.Figure(go.Bar(x=d.population, y=d.prefecture, orientation="h",
                           marker_color=[C["red"] if a == 0 else C["gold"] for a in d.auto_ecoles],
                           text=[("aucune auto-école" if a == 0 else f"{int(a)} école(s)") for a in d.auto_ecoles],
                           textposition="outside", cliponaxis=False,
                           customdata=d[["region", "auto_ecoles", "auto_ecoles_agreees"]].values,
                           hovertemplate="<b>%{y}</b> (%{customdata[0]})<br>%{x:,.0f} habitants"
                                         "<br>%{customdata[1]} auto-école(s), dont %{customdata[2]} agréée(s)<extra></extra>"))
    fig.update_layout(yaxis=dict(autorange="reversed", title=""), xaxis=dict(title="Population 2022"),
                      margin=dict(r=130))
    plotly(fig, 420)
    source("Préfectures classées par nombre d'auto-écoles croissant, puis par population décroissante")
with c2:
    st.markdown("### Part des auto-écoles agréées, par région")
    d = ae.groupby(["region", "statut"], as_index=False).size()
    fig = px.bar(d, x="region", y="size", color="statut", color_discrete_map=STATUT_COLORS,
                 category_orders={"region": D.REGION_ORDER, "statut": ["Agréée", "Antenne agréée", "Non agréée", "Non renseigné"]},
                 labels={"size": "Auto-écoles", "region": "", "statut": ""})
    fig.update_layout(barmode="stack", barnorm="percent", legend_y=1.1, xaxis_tickangle=-25,
                      yaxis=dict(title="Part des auto-écoles (%)", ticksuffix=" %"))
    fig.update_traces(hovertemplate="<b>%{x}</b> · %{y} école(s)<extra>%{fullData.name}</extra>")
    plotly(fig, 420)
    source("Répartition en pourcentage ; les effectifs apparaissent au survol. Champ « agrégation » : Agréée, Antenne agréée, Non agréée, Néant (classé non renseigné)")

insight(
    f"<b>Quinze préfectures n'ont aucune auto-école</b> — Haho (305 096 habitants), Dankpen, Est-Mono, Oti-Sud, Tandjoaré, "
    "Kéran, Kpendjal-Ouest, Avé, Moyen-Mono, Kpendjal, Doufelgou, Binah, Akébou, Danyi et Mô. "
    f"<b>Huit autres en ont, mais aucune agréée.</b> Au total, {k['prefectures_sans_auto_ecole_agreee']} préfectures sur 39 "
    "ne disposent d'aucune structure de formation encadrée : leurs habitants doivent se déplacer pour passer le permis, "
    "ou s'en passer.", "red")

with st.expander("Liste complète des auto-écoles"):
    t = ae[["nom", "statut", "localite", "commune", "prefecture", "region"]].rename(columns={
        "nom": "Auto-école", "statut": "Statut", "localite": "Localité", "commune": "Commune",
        "prefecture": "Préfecture", "region": "Région"})
    st.dataframe(t.sort_values(["Région", "Préfecture", "Auto-école"]), hide_index=True, use_container_width=True, height=330)
    st.download_button("Télécharger (CSV)", t.to_csv(index=False).encode("utf-8-sig"), "auto_ecoles_togo.csv", "text/csv")
