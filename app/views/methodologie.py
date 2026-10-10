from pathlib import Path

import pandas as pd
import streamlit as st

from lib import data as D
from lib.ui import header, insight, section, source

D.sidebar_filters()
k = D.kpi()

header("Méthodologie, sources et limites",
       "Tout ce qui a été fait aux données avant d'être montré — et ce que ces données ne permettent pas de dire.")

section("Sources", "Sept jeux de données, dont un référentiel de contours externe")
src = pd.DataFrame([
    ["Routes classées", "Géoportail Open Data du Togo", "799 tronçons géolocalisés (MULTILINESTRING) : type, revêtement, nombre de voies", "Export 12/2024"],
    ["Auto-écoles", "Géoportail Open Data du Togo", "272 établissements géolocalisés, statut d'agrément", "Export 01/2025"],
    ["État du réseau routier", "Séries sectorielles transport", "87 tronçons nommés × 4 états (bon, moyen, mauvais, travaux)", "2020"],
    ["Immatriculations", "Séries sectorielles transport", "Véhicules immatriculés par type, 8 catégories", "1990-2022"],
    ["Permis de conduire", "Séries sectorielles transport", "Permis délivrés par catégorie, 7 catégories", "2007-2022"],
    ["Accidents, morts, blessés", "Séries sectorielles transport", "Extraits d'un export regroupant 13 indicateurs de transport", "2010-2022"],
    ["Population résidente", "INSEED, RGPH-5", "759 unités : pays, régions, préfectures, communes, cantons", "2022"],
    ["Contours administratifs", "geoBoundaries (OSM), gbOpen", "5 régions, 37 préfectures — découpage 2017", "Source externe, ODbL / CC-BY-SA"],
], columns=["Jeu de données", "Producteur", "Contenu", "Période"])
NL = chr(10)
md = "| " + " | ".join(src.columns) + " |" + NL + "|" + "---|" * len(src.columns) + NL
md += NL.join("| " + " | ".join(str(v) for v in row) + " |" for row in src.values)
st.markdown(md)

section("Deux pièges d'étiquetage identifiés dans les sources", "Signalés, corrigés, et documentés ici")
insight("""
<b>① « Accidents mortels /100 000 hab » compte en réalité tous les accidents.</b>
La série vaut 92,7 en 2022. Or 7 507 accidents ÷ 8 095 498 habitants × 100 000 = 92,7 — et la même vérification tient
sur 2010 (3 101 ÷ 6,2 M = 50,0). Il s'agit donc du taux d'accidents, toutes gravités confondues. Le véritable taux de
mortalité routière est de <b>8,4 morts pour 100 000 habitants</b> en 2022. Tous les taux du tableau de bord sont recalculés
à partir des effectifs bruts et de la population implicite déduite de cette série.
""", "gold")
insight("""
<b>② « Parc automobile immatriculé » est un flux, pas un stock.</b>
La série décroît plusieurs années de suite (85 748 en 2015, 64 120 en 2016) : elle ne peut pas décrire un parc cumulé.
Ce sont les <b>véhicules immatriculés dans l'année</b>. Vérification croisée : les deux fichiers concordent exactement —
93 770 immatriculations totales en 2022 moins 67 639 deux-roues = 26 131, soit précisément la valeur publiée pour
« parc 4 roues et plus ». Le tableau de bord parle donc systématiquement d'immatriculations annuelles.
""", "gold")

section("Traitements")
st.markdown("""
1. **Longueur du réseau** : les tracés sont publiés en `MULTILINESTRING` (coordonnées géographiques). La longueur de chaque
   tronçon est calculée par **formule de haversine** sommée sur les segments, puis agrégée par préfecture et région.
   Total obtenu : **3 373 km**. Les tracés sont simplifiés à environ 150 m (Douglas-Peucker) pour l'affichage web uniquement ;
   les longueurs sont calculées sur les tracés complets.
2. **Jointure état × tracés** : l'état est publié par tronçon administratif nommé (« RN1 BABAME-SOKODE »), les tracés portent
   un libellé différent. Les deux sont rapprochés par **numéro de route nationale** extrait par expression régulière.
   Les 50 routes nationales de la table d'état sont toutes retrouvées ; 644 tronçons sur 799 reçoivent un état.
   Chaque tronçon se voit attribuer l'**état dominant de sa route nationale** — approximation assumée, l'état réel pouvant
   varier le long d'un même axe. Les 155 tronçons restants (voiries urbaines, pistes) sont marqués « non renseigné ».
3. **Population** : la source liste 759 unités sans colonne de niveau. La hiérarchie est reconstruite par la structure du
   fichier et validée par l'égalité *population de la préfecture = somme de ses communes*. La préfecture d'**Avé**, absente,
   est reconstruite comme Avé 1 + Avé 2 (111 214 habitants).
4. **Six régions** : Golfe et Agoè-Nyivé (2 188 376 habitants) sont publiés hors de la région Maritime dans le RGPH-5,
   conformément au District autonome du Grand Lomé. Le tableau de bord suit ce découpage, ce qui fait apparaître la
   concentration réelle de l'offre.
5. **Référentiel des préfectures** : la préfecture de **Mô** (Centrale, 52 448 habitants) n'apparaît dans aucun des deux jeux
   géolocalisés. Elle est ajoutée au référentiel avec des valeurs nulles — c'est un résultat, pas une donnée manquante.
6. **Cartographie** : les contours 2017 ne connaissent ni Agoè-Nyivé, ni Kpendjal-Ouest, ni Oti-Sud ; ces préfectures sont
   représentées avec leur préfecture d'origine (Golfe, Kpendjal, Oti), les indicateurs étant recalculés sur l'ensemble
   fusionné. Les tableaux conservent les 39 préfectures actuelles.
""")

section("Définitions")
st.markdown("""
- **Réseau classé** : routes nationales, voiries urbaines et pistes rurales inscrites au réseau classé et géolocalisées par le Géoportail. Il ne comprend pas le maillage local non classé.
- **Auto-école agréée** : établissement dont le champ d'agrément vaut « Agréée » ou « Antenne agréée ». « Néant » est traité comme statut non renseigné, non comme non-agrément.
- **Mètres de route par habitant** : longueur du réseau classé ÷ population 2022, à la maille considérée.
- **Létalité** : morts ÷ accidents, en pourcentage.
- **Indice de priorité** : 40 % habitants par auto-école agréée, 30 % mètres de route par habitant (inversé), 30 % part non revêtue — normalisation min-max sur les 39 préfectures.
""")

section("Limites")
insight("""
<b>Ce que ces données ne disent pas.</b>
<ul style="margin:.4rem 0 0 1rem">
<li><b>Aucune donnée d'accident en dessous du niveau national.</b> Impossible de savoir où surviennent les accidents, ni sur quel axe : le croisement accidents × réseau × territoire, qui serait le plus utile, n'est pas réalisable avec les données publiées.</li>
<li>Les immatriculations ne sont pas un parc en circulation : ni les sorties de parc, ni les véhicules non immatriculés ne sont connus.</li>
<li><b>Rupture de série en 2015</b> : les effectifs d'accidents, morts et blessés y sont environ deux fois inférieurs aux années voisines, simultanément pour toutes les catégories. L'anomalie est signalée, non corrigée.</li>
<li>L'état du réseau date de 2020, les tracés de fin 2024, les auto-écoles de début 2025 et la population de 2022 : les ratios croisent des millésimes proches mais distincts.</li>
<li>Les contours administratifs (2017) sont une source externe ; le Géoportail ne publie pas de limites de préfecture.</li>
<li>Le statut d'agrément est celui enregistré lors du recensement : il a pu évoluer depuis.</li>
</ul>
""", "gold")

section("Reproductibilité")
st.markdown("Le pipeline `pipeline/build_data.py` reconstruit l'ensemble des tables à partir des fichiers bruts en une seule "
            "commande, contrôles de cohérence compris. Les tables préparées sont téléchargeables ci-dessous.")
P = Path(__file__).resolve().parents[1] / "data" / "processed"
files = [("prefectures.csv", "Préfectures (39)"), ("regions.csv", "Régions (6)"), ("routes.csv", "Tronçons (799)"),
         ("auto_ecoles.csv", "Auto-écoles (272)"), ("ts_securite_routiere.csv", "Sécurité routière"),
         ("ts_parc_vehicules.csv", "Immatriculations"), ("ts_permis.csv", "Permis"),
         ("etat_par_route_nationale.csv", "État par route nationale")]
cols = st.columns(4)
for i, (fn, lbl) in enumerate(files):
    p = P / fn
    if p.exists():
        cols[i % 4].download_button(lbl, p.read_bytes(), fn, "text/csv", use_container_width=True)
source("Tableau de bord réalisé avec Python, Streamlit et Plotly · SADJINA Christ, octobre 2026")
