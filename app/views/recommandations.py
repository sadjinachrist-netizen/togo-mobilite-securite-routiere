import plotly.graph_objects as go
import streamlit as st

from lib import data as D
from lib.ui import C, REGION_COLORS, fmt, header, insight, plotly, reco, section, source

D.sidebar_filters()
k, pref, reg, secu = D.kpi(), D.prefectures(), D.regions(), D.securite()

header("Six recommandations pour une mobilité plus sûre",
       "Chacune est rattachée à un territoire nommé, à un nombre d'habitants et à une cible chiffrée issue du tableau de bord.")

sans_ae = pref[pref.sans_auto_ecole].sort_values("population", ascending=False)
sans_agr = pref[pref.sans_auto_ecole_agreee].sort_values("population", ascending=False)
savanes = reg[reg.region == "Savanes"].iloc[0]
s22 = secu[secu.annee == 2022].iloc[0]
# cible : une auto-école agréée par préfecture qui n'en a aucune
cible_ae = int(sans_agr.shape[0])

reco(1, "Faire du permis moto la priorité de la formation routière",
     fmt(k["parc_deux_roues"]), f"deux-roues immatriculés en 2022, pour seulement {fmt(k['permis_moto'])} permis A délivrés",
     f"Les deux-roues représentent {fmt(k['part_deux_roues'], 1)} % des véhicules immatriculés et une part majeure des victimes, "
     f"mais {fmt(k['permis_moto']/k['permis_total']*100, 1)} % seulement des permis délivrés. L'effort de 2022 (4 837 permis A contre 211 en 2021) "
     "montre que la capacité existe : il faut l'installer durablement. Cible : porter la part des permis A à 40 % des permis "
     "délivrés en trois ans, par des sessions d'examen décentralisées et un format court adapté aux conducteurs déjà en circulation.",
     "Priorité haute", "red", red=True)

reco(2, f"Implanter une auto-école agréée dans les {cible_ae} préfectures qui n'en ont aucune",
     fmt(int(sans_agr.population.sum())), "habitants sans structure de formation encadrée dans leur préfecture",
     "Quinze préfectures n'ont aucune auto-école, huit autres n'en ont aucune agréée. Les plus peuplées : "
     + ", ".join(f"{r.prefecture} ({fmt(r.population)})" for r in sans_agr.head(5).itertuples())
     + ". Cible : au moins une structure agréée par chef-lieu de préfecture, en priorisant par population non desservie. "
       "Un dispositif d'antennes agréées — déjà utilisé pour 47 structures — permet d'y parvenir sans créer 23 écoles complètes.",
     "Priorité haute", "red", red=True)

reco(3, "Régulariser ou fermer les auto-écoles non agréées",
     fmt(k["auto_ecoles_non_agreees"]), f"écoles non agréées sur {fmt(k['auto_ecoles'])} recensées ({fmt(k['part_non_agreees'], 1)} %)",
     "Une école sur deux fonctionne hors agrément, avec des pointes à deux tiers dans la Centrale et 60 % dans les Savanes. "
     "Deux actions complémentaires : une campagne de mise en conformité assortie d'un délai, puis la publication d'un "
     "registre public des écoles agréées, consultable avant inscription. Fermer sans alternative aggraverait le déficit "
     "de formation : la régularisation doit précéder la sanction.",
     "Priorité haute", "red", red=True)

reco(4, "Concentrer l'entretien sur les routes nationales les plus dégradées",
     fmt(k["km_etat"].get("Mauvais état", 0), 0, " km"), f"en mauvais état sur {fmt(sum(k['km_etat'].values()), 0)} km évalués en 2020",
     f"Le réseau compte {fmt(k['km_etat'].get('Bon état', 0), 0)} km en bon état seulement, et {fmt(k['km_etat'].get('Travaux en cours', 0), 0)} km "
     f"en travaux. Les Savanes n'ont que {fmt(savanes.part_revetue, 0)} % de réseau revêtu contre {fmt(reg[reg.region=='Grand Lomé'].part_revetue.iloc[0], 0)} % "
     "au Grand Lomé. Cible : porter chaque région au-dessus de 60 % de réseau revêtu, en traitant en premier les routes "
     "nationales dont plus de la moitié des kilomètres sont classés en mauvais état (page « Réseau routier »).",
     "Priorité moyenne", "gold")

reco(5, "Désenclaver Mô et les préfectures sans réseau structurant",
     "52 448", "habitants dans la seule préfecture sans aucune route nationale classée recensée",
     "Mô (Centrale) n'apparaît ni dans le réseau classé, ni dans les auto-écoles : c'est le territoire le plus isolé du pays "
     "sur les deux dimensions à la fois. Au-delà, treize préfectures restent sous 0,30 m de route classée par habitant. "
     "Cible : vérifier et compléter le recensement du réseau sur ces territoires avant d'arbitrer les investissements — "
     "une absence de donnée n'est pas une absence de besoin.",
     "Priorité moyenne", "gold")

reco(6, "Publier des données de sécurité routière localisées et à jour",
     "2022", "dernière année disponible · aucune donnée d'accident en dessous du niveau national",
     "Les accidents, morts et blessés ne sont publiés qu'au niveau national : impossible de savoir où l'on meurt sur la route, "
     "ni sur quel axe. Trois corrections à apporter : localiser les accidents au moins à la préfecture, corriger l'intitulé "
     "de la série « Accidents mortels /100 000 hab » qui compte en réalité tous les accidents, et documenter la rupture de "
     "série de 2015. Sans cela, aucune politique ne peut être ciblée ni évaluée.",
     "Données", "green")

# ------------------------------------------------------------------ indice
section("Indice de priorité d'intervention", "Trois déficits combinés, normalisés et pondérés")
st.markdown("<div class='kicker'>40 % accès à la formation (habitants par auto-école agréée) · 30 % densité du réseau classé "
            "(mètres par habitant, inversé) · 30 % qualité du réseau (part non revêtue). 0 = aucun déficit, 100 = déficit maximal observé.</div>",
            unsafe_allow_html=True)


def rank01(s, invert=False):
    s = s.fillna(s.max())
    r = (s - s.min()) / (s.max() - s.min()) if s.max() > s.min() else s * 0
    return 1 - r if invert else r


p = pref.copy()
p["hab_par_agreee"] = p.population / p.auto_ecoles_agreees.where(p.auto_ecoles_agreees > 0)
p["part_non_revetue"] = 100 - p.part_revetue.fillna(0)
p["score"] = (100 * (0.40 * rank01(p.hab_par_agreee)
                     + 0.30 * rank01(p.m_route_par_hab, invert=True)
                     + 0.30 * rank01(p.part_non_revetue))).round(0)
p = p.sort_values("score", ascending=False)

fig = go.Figure()
for r_ in D.REGION_ORDER:
    d = p[p.region == r_]
    if not len(d):
        continue
    fig.add_trace(go.Bar(x=d.prefecture, y=d.score, name=r_, marker_color=REGION_COLORS[r_],
                         customdata=d[["region", "population", "auto_ecoles", "auto_ecoles_agreees",
                                       "m_route_par_hab", "part_revetue"]].values,
                         hovertemplate="<b>%{x}</b> (%{customdata[0]}) · indice %{y}<br>%{customdata[1]:,.0f} habitants"
                                       "<br>%{customdata[2]} auto-école(s) dont %{customdata[3]} agréée(s)"
                                       "<br>%{customdata[4]:.2f} m de route/hab. · %{customdata[5]:.0f} %% revêtu<extra></extra>"))
fig.update_layout(barmode="stack", xaxis=dict(categoryorder="array", categoryarray=list(p.prefecture), tickangle=-45, title=""),
                  yaxis_title="Indice de priorité (0-100)", legend_y=1.08)
plotly(fig, 400)
source("Calcul : 40 % habitants par auto-école agréée · 30 % mètres de route par habitant (inversé) · 30 % part non revêtue — "
       "normalisation min-max sur les 39 préfectures")

top = p.head(6)
insight("<b>Six préfectures prioritaires : " + ", ".join(top.prefecture) + ".</b> Elles totalisent "
        f"{fmt(top.population.sum())} habitants, soit {fmt(top.population.sum()/k['population_2022']*100, 1)} % de la population. "
        f"Aucune n'est dans le Grand Lomé. {int(top.sans_auto_ecole_agreee.sum())} sur 6 n'ont aucune auto-école agréée.", "red")

with st.expander("Table de l'indice de priorité"):
    t = p[["prefecture", "region", "population", "score", "auto_ecoles", "auto_ecoles_agreees",
           "m_route_par_hab", "part_revetue", "km_routes"]].rename(columns={
        "prefecture": "Préfecture", "region": "Région", "population": "Population", "score": "Indice",
        "auto_ecoles": "Auto-écoles", "auto_ecoles_agreees": "dont agréées", "m_route_par_hab": "m route/hab.",
        "part_revetue": "% revêtu", "km_routes": "Km réseau"})
    st.dataframe(t, hide_index=True, use_container_width=True)
    st.download_button("Télécharger (CSV)", t.to_csv(index=False).encode("utf-8-sig"), "indice_priorite_mobilite.csv", "text/csv")
