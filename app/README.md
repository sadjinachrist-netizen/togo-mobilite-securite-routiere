# Mobilité et sécurité routière au Togo — tableau de bord

Data Challenge « Administration territoriale et mobilité » · Défi 1 · Togo AI Lab / MESPTN
Auteur : **SADJINA Christ** · octobre 2026

Tableau de bord interactif (Python · Streamlit · Plotly) qui mesure l'évolution de la mobilité et de la sécurité
routière au Togo, à partir des données ouvertes sur les immatriculations, les permis de conduire, les accidents,
l'état et le tracé du réseau routier, les auto-écoles et la population 2022.

## Lancer en local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Reconstruire les données préparées

```bash
python pipeline/build_data.py
```

Le pipeline lit `data/raw/` (exports bruts) et `data/geo/` (contours geoBoundaries) et écrit `data/processed/`.
Il inclut les contrôles de cohérence (39 préfectures, somme des populations, jointure état × tracés).

## Structure

```
app.py                 point d'entrée et navigation
views/                 7 pages : vue d'ensemble, parc et permis, sécurité routière,
                       réseau routier, formation, recommandations, méthodologie
lib/data.py            chargement des données et filtres globaux partagés
lib/ui.py              charte graphique, composants, thème Plotly
pipeline/build_data.py préparation des données
tools/shoot.py         captures automatiques des pages (Playwright)
data/raw/              8 jeux bruts + 2 dictionnaires de champs
data/geo/              contours ADM1 / ADM2 (geoBoundaries, ODbL / CC-BY-SA)
data/processed/        tables, GeoJSON et indicateurs prêts à l'emploi
```

## Points de méthode

- Longueurs de route calculées par formule de haversine sur les tracés `MULTILINESTRING` (3 373 km).
- État du réseau rattaché aux tracés par numéro de route nationale (644 tronçons sur 799).
- Deux pièges d'étiquetage de la source identifiés et corrigés, documentés dans la page « Méthodologie » :
  la série « Accidents mortels /100 000 hab » compte en réalité tous les accidents ; la série « parc automobile
  immatriculé » est un flux annuel et non un stock.

## Sources

Géoportail Open Data de la République Togolaise · séries sectorielles transport · INSEED (RGPH-5 2022) ·
geoBoundaries (OpenStreetMap)
