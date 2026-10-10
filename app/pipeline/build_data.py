"""
Pipeline de préparation des données — Administration territoriale et mobilité · Défi 1
Data Challenge · Togo AI Lab / MESPTN

Entrées  : data/raw/*.csv (Géoportail Open Data, INSEED, séries sectorielles)
           data/geo/togo_adm1.geojson, togo_adm2.geojson (geoBoundaries, OSM 2017)
Sorties  : data/processed/*.csv, *.geojson, kpi_national.json

Lancer   : python pipeline/build_data.py   (depuis app/)
"""
from __future__ import annotations

import csv
import json
import math
import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd
from shapely.geometry import mapping, shape
from shapely.ops import unary_union

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
csv.field_size_limit(10 ** 9)

ROOT = Path(__file__).resolve().parents[1]
RAW, GEO, OUT = ROOT / "data" / "raw", ROOT / "data" / "geo", ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

GRAND_LOME = {"GOLFE", "AGOE-NYIVE"}
REGIONS_SOURCE = {"SAVANES", "KARA", "CENTRALE", "PLATEAUX", "MARITIME"}


# ----------------------------------------------------------------- utilitaires
def norm(s) -> str:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s.upper().strip())


def haversine(a, b) -> float:
    R = 6371.0088
    (x1, y1), (x2, y2) = a, b
    p1, p2 = math.radians(y1), math.radians(y2)
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(x2 - x1) / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


def wkt_lines(wkt: str) -> list[list[tuple[float, float]]]:
    """MULTILINESTRING -> liste de polylignes [(lon, lat), ...]."""
    return [[tuple(map(float, c.split())) for c in part.split(",") if c.strip()]
            for part in re.findall(r"\(([-0-9.,\s]+)\)", wkt)]


def line_km(wkt: str) -> float:
    return sum(sum(haversine(l[i], l[i + 1]) for i in range(len(l) - 1)) for l in wkt_lines(wkt))


def parse_point(wkt: str) -> tuple[float, float]:
    lon, lat = wkt.strip()[len("POINT ("):-1].split()
    return float(lon), float(lat)


def rn_number(label: str) -> str | None:
    """Numéro de route nationale : 'TGRKRTRN38 RN1 BAFILO-DAKO' -> '1'."""
    m = re.findall(r"RN\s?(\d+(?:BIS|[A-Z])?)", str(label).upper())
    return m[-1] if m else None


def simplify_line(line: list[tuple[float, float]], tol: float = 0.0015) -> list[list[float]]:
    """Douglas-Peucker léger : ~150 m, suffisant pour une carte web."""
    from shapely.geometry import LineString
    if len(line) < 3:
        return [list(p) for p in line]
    g = LineString(line).simplify(tol, preserve_topology=False)
    return [list(p) for p in g.coords]


# ----------------------------------------------------------------- 1. population (RGPH-5 2022)
routes_raw = pd.read_csv(RAW / "routes_classees.csv")
ae_raw = pd.read_csv(RAW / "auto_ecoles.csv")
for d in (routes_raw, ae_raw):
    for c in [c for c in d.columns if c.endswith("_nom_bdd") or c.startswith("nom_") or c.startswith("route_") or c == "agregation"]:
        d[c] = d[c].astype(str).str.strip()

LIB_PREF = {}
PREF_TO_REGION = {}
for d in (routes_raw, ae_raw):
    for p, r in zip(d["prefecture_nom_bdd"], d["region_nom_bdd"]):
        LIB_PREF.setdefault(norm(p), p)
        PREF_TO_REGION.setdefault(norm(p), r)
# La préfecture de Mô (Centrale) n'apparaît dans aucun des deux jeux géolocalisés : ni route
# nationale classée, ni auto-école. Elle est ajoutée au référentiel pour figurer dans les
# classements avec des valeurs nulles — c'est un résultat, pas une donnée manquante.
LIB_PREF.setdefault("MO", "Mô")
PREF_TO_REGION.setdefault("MO", "Centrale")
PREFS = set(LIB_PREF)


def region6(pref_key: str) -> str:
    return "Grand Lomé" if pref_key in GRAND_LOME else PREF_TO_REGION.get(pref_key, "?")


pop_raw = pd.read_csv(RAW / "population_rgph5_2022.csv")
pop_raw["key"] = pop_raw["découpage-administratif"].map(norm)
pop_raw["value"] = pop_raw["Value"].astype(int)

rows, pref_cur = [], None
for key, val in zip(pop_raw["key"], pop_raw["value"]):
    if key == "TOGO":
        lvl = "pays"
    elif key in REGIONS_SOURCE:
        lvl, pref_cur = "region", None
    elif pref_cur and re.fullmatch(re.escape(pref_cur) + r" \d+", key):
        lvl = "commune"
    elif key in PREFS and key != pref_cur:
        lvl, pref_cur = "prefecture", key
    else:
        lvl = "infra"
    rows.append((lvl, pref_cur, key, val))
pop = pd.DataFrame(rows, columns=["niveau", "prefecture_key", "key", "population"])

pop_pref = pop[pop.niveau == "prefecture"][["key", "population"]].rename(columns={"key": "prefecture_key"})
if "AVE" not in set(pop_pref.prefecture_key):           # préfecture absente de la source
    ave = int(pop.loc[pop.key.str.fullmatch(r"AVE \d+"), "population"].sum())
    pop_pref = pd.concat([pop_pref, pd.DataFrame([{"prefecture_key": "AVE", "population": ave}])], ignore_index=True)
    print(f"  Avé reconstruite : {ave:,} habitants (Avé 1 + Avé 2)")
POP_TOTAL = int(pop.loc[pop.niveau == "pays", "population"].iloc[0])
assert len(pop_pref) == 39, f"{len(pop_pref)} préfectures (39 attendues)"
assert abs(pop_pref.population.sum() - POP_TOTAL) < 1000, "somme des préfectures ≠ total national"

# ----------------------------------------------------------------- 2. réseau routier
ro = routes_raw.copy()
ro["km"] = ro["geometry"].map(line_km)
ro["rn"] = ro["route_nom"].map(rn_number)
ro["prefecture_key"] = ro["prefecture_nom_bdd"].map(norm)
ro["region"] = ro["prefecture_key"].map(region6)
ro["revetue"] = ro["route_recouvrement"].isin(["Bitume", "Beton", "Pavé", "Gravier amenagé"])
ro["voies_nbr"] = pd.to_numeric(ro["voies_nbr"], errors="coerce")

# état du réseau 2020 : agrégé par route nationale, puis état dominant par RN
et = pd.read_csv(RAW / "etat_reseau_2020.csv")
et.columns = [c.strip().lower() for c in et.columns]
et["value"] = pd.to_numeric(et["value"], errors="coerce")
et_tr = et[et["tronçon"] != "TOTAL"].copy()
et_tr["rn"] = et_tr["tronçon"].map(rn_number)
etat_rn = (et_tr[et_tr.etat != "TOTAL"].groupby(["rn", "etat"], as_index=False).value.sum()
           .rename(columns={"value": "km"}))
etat_rn.to_csv(OUT / "etat_par_route_nationale.csv", index=False)
dominant = etat_rn.sort_values("km", ascending=False).drop_duplicates("rn").set_index("rn")["etat"].to_dict()
ETAT_LIB = {"BON": "Bon état", "MOYEN": "État moyen", "MAUVAIS": "Mauvais état", "TRAVAUX": "Travaux en cours"}
ro["etat_dominant"] = ro["rn"].map(lambda r: ETAT_LIB.get(dominant.get(r), "Non renseigné"))

# totaux nationaux publiés (table état, ligne TOTAL)
etat_national = (et[(et["tronçon"] == "TOTAL") & (et.etat != "TOTAL")]
                 .groupby(["indicateur", "etat"], as_index=False).value.sum().rename(columns={"value": "km"}))
etat_national["etat_lib"] = etat_national["etat"].map(ETAT_LIB)
etat_national.to_csv(OUT / "etat_reseau_national.csv", index=False)

ro_out = ro[["FID", "region", "prefecture_nom_bdd", "commune_nom_bdd", "canton_nom_bdd", "route_nom", "rn",
             "route_type", "route_recouvrement", "etat_dominant", "voies_nbr", "revetue", "km", "prefecture_key"]]
ro_out = ro_out.rename(columns={"prefecture_nom_bdd": "prefecture", "commune_nom_bdd": "commune", "canton_nom_bdd": "canton"})
ro_out.to_csv(OUT / "routes.csv", index=False)

# GeoJSON allégé pour la carte
feats = []
for i, r in ro.iterrows():
    lines = [simplify_line(l) for l in wkt_lines(r["geometry"])]
    lines = [l for l in lines if len(l) >= 2]
    if not lines:
        continue
    feats.append({"type": "Feature", "id": int(i),
                  "properties": {"nom": r["route_nom"], "rn": r["rn"] or "", "type": r["route_type"],
                                 "revetement": r["route_recouvrement"], "etat": r["etat_dominant"],
                                 "region": r["region"], "prefecture": r["prefecture_nom_bdd"],
                                 "km": round(float(r["km"]), 1), "voies": None if pd.isna(r["voies_nbr"]) else int(r["voies_nbr"])},
                  "geometry": {"type": "MultiLineString", "coordinates": lines}})
json.dump({"type": "FeatureCollection", "features": feats}, open(OUT / "routes.geojson", "w", encoding="utf-8"))

# ----------------------------------------------------------------- 3. auto-écoles
ae = ae_raw.copy()
ae[["lon", "lat"]] = ae["geometry"].apply(lambda w: pd.Series(parse_point(w)))
ae["prefecture_key"] = ae["prefecture_nom_bdd"].map(norm)
ae["region"] = ae["prefecture_key"].map(region6)
STATUT = {"Agréée": "Agréée", "Antenne agréée": "Antenne agréée", "Non agréée": "Non agréée"}
ae["statut"] = ae["agregation"].map(lambda s: STATUT.get(s, "Non renseigné"))
ae["agreee"] = ae["statut"].isin(["Agréée", "Antenne agréée"])
ae_out = ae[["FID", "region", "prefecture_nom_bdd", "commune_nom_bdd", "canton_nom_bdd", "nom_localite",
             "nom_etablissement", "statut", "agreee", "lon", "lat", "prefecture_key"]]
ae_out = ae_out.rename(columns={"prefecture_nom_bdd": "prefecture", "commune_nom_bdd": "commune",
                                "canton_nom_bdd": "canton", "nom_localite": "localite", "nom_etablissement": "nom"})
ae_out.to_csv(OUT / "auto_ecoles.csv", index=False)

# ----------------------------------------------------------------- 4. table PRÉFECTURES
pref = pd.DataFrame({"prefecture_key": sorted(PREFS)})
pref["prefecture"] = pref.prefecture_key.map(LIB_PREF)
pref["region"] = pref.prefecture_key.map(region6)
pref = pref.merge(pop_pref, on="prefecture_key", how="left")
g_ro = ro.groupby("prefecture_key")
pref["km_routes"] = pref.prefecture_key.map(g_ro.km.sum()).fillna(0).round(1)
pref["km_revetues"] = pref.prefecture_key.map(ro[ro.revetue].groupby("prefecture_key").km.sum()).fillna(0).round(1)
pref["segments"] = pref.prefecture_key.map(g_ro.size()).fillna(0).astype(int)
pref["auto_ecoles"] = pref.prefecture_key.map(ae.groupby("prefecture_key").size()).fillna(0).astype(int)
pref["auto_ecoles_agreees"] = pref.prefecture_key.map(ae[ae.agreee].groupby("prefecture_key").size()).fillna(0).astype(int)
pref["auto_ecoles_non_agreees"] = pref.auto_ecoles - pref.auto_ecoles_agreees
pref["part_revetue"] = (pref.km_revetues / pref.km_routes.where(pref.km_routes > 0) * 100).round(1)
pref["m_route_par_hab"] = (pref.km_routes * 1000 / pref.population).round(2)
pref["hab_par_auto_ecole"] = (pref.population / pref.auto_ecoles.where(pref.auto_ecoles > 0)).round(0)
pref["hab_par_auto_ecole_agreee"] = (pref.population / pref.auto_ecoles_agreees.where(pref.auto_ecoles_agreees > 0)).round(0)
pref["part_agreees"] = (pref.auto_ecoles_agreees / pref.auto_ecoles.where(pref.auto_ecoles > 0) * 100).round(1)
pref["sans_auto_ecole"] = pref.auto_ecoles == 0
pref["sans_auto_ecole_agreee"] = pref.auto_ecoles_agreees == 0
pref["part_population"] = (pref.population / POP_TOTAL * 100).round(2)

MAP_MERGE = {"AGOE-NYIVE": "GOLFE", "KPENDJAL-OUEST": "KPENDJAL", "OTI-SUD": "OTI"}
pref["map_key"] = pref.prefecture_key.map(lambda k: MAP_MERGE.get(k, k))
pref = pref.sort_values(["region", "prefecture"]).reset_index(drop=True)
pref.to_csv(OUT / "prefectures.csv", index=False)

# ----------------------------------------------------------------- 5. table RÉGIONS
reg = pref.groupby("region", as_index=False).agg(
    population=("population", "sum"), km_routes=("km_routes", "sum"), km_revetues=("km_revetues", "sum"),
    auto_ecoles=("auto_ecoles", "sum"), auto_ecoles_agreees=("auto_ecoles_agreees", "sum"),
    prefectures=("prefecture", "count"), sans_auto_ecole=("sans_auto_ecole", "sum"))
reg["auto_ecoles_non_agreees"] = reg.auto_ecoles - reg.auto_ecoles_agreees
reg["part_revetue"] = (reg.km_revetues / reg.km_routes * 100).round(1)
reg["m_route_par_hab"] = (reg.km_routes * 1000 / reg.population).round(2)
reg["hab_par_auto_ecole"] = (reg.population / reg.auto_ecoles.where(reg.auto_ecoles > 0)).round(0)
reg["part_agreees"] = (reg.auto_ecoles_agreees / reg.auto_ecoles.where(reg.auto_ecoles > 0) * 100).round(1)
reg["part_population"] = (reg.population / POP_TOTAL * 100).round(1)
reg["part_km"] = (reg.km_routes / reg.km_routes.sum() * 100).round(1)
reg["part_auto_ecoles"] = (reg.auto_ecoles / reg.auto_ecoles.sum() * 100).round(1)
reg.to_csv(OUT / "regions.csv", index=False)

# ----------------------------------------------------------------- 6. séries temporelles
def load_obs(fname: str, dim: str | None = None) -> pd.DataFrame:
    d = pd.read_csv(RAW / fname)
    d.columns = [c.strip().lower() for c in d.columns]
    d["value"] = pd.to_numeric(d["value"], errors="coerce")
    d["annee"] = pd.to_numeric(d["date"], errors="coerce").astype("Int64")
    keep = ["indicateur", "annee", "value"] + ([dim] if dim else [])
    return d[keep].dropna(subset=["annee", "value"])


# --- sécurité routière (extrait d'un fichier qui mélange 13 indicateurs)
tr = load_obs("transport_accidents_series.csv")
SECU = {"Nombre de cas d'accidents de la circulation": "accidents",
        "Nombre de morts": "morts", "Nombre de blessés": "blesses",
        "Accidents mortels /100.000 hab": "taux_source"}
secu = (tr[tr.indicateur.isin(SECU)].assign(k=lambda d: d.indicateur.map(SECU))
        .pivot_table(index="annee", columns="k", values="value").reset_index())
# Population annuelle implicite de la source : la série « taux » est en réalité
# le nombre d'accidents (tous) pour 100 000 habitants — vérifié : accidents / pop × 1e5 = taux.
secu["population_implicite"] = (secu.accidents / secu.taux_source * 1e5).round(0)
secu["accidents_100k"] = secu.taux_source.round(1)
secu["morts_100k"] = (secu.morts / secu.population_implicite * 1e5).round(1)
secu["blesses_100k"] = (secu.blesses / secu.population_implicite * 1e5).round(1)
secu["letalite_pct"] = (secu.morts / secu.accidents * 100).round(1)
secu["victimes"] = secu.morts + secu.blesses
secu = secu[["annee", "accidents", "morts", "blesses", "victimes", "accidents_100k", "morts_100k",
             "blesses_100k", "letalite_pct", "population_implicite"]]
secu.to_csv(OUT / "ts_securite_routiere.csv", index=False)

# --- parc automobile par type (1990-2022)
parc = load_obs("parc_par_type_1990_2022.csv", "types-de-vehicule").rename(columns={"types-de-vehicule": "type"})
parc["type"] = parc["type"].replace({"Voitues": "Voitures", "2 roues et assimilées": "Deux-roues"})
parc.to_csv(OUT / "ts_parc_vehicules.csv", index=False)

# --- permis par catégorie (2007-2022)
permis = load_obs("permis_par_categorie.csv", "categories-de-permis").rename(columns={"categories-de-permis": "categorie"})
permis["categorie"] = permis["categorie"].replace({"Voiture légèr (B)": "Voiture légère (B)"})
permis.to_csv(OUT / "ts_permis.csv", index=False)

# --- autres séries transport (fret, trafic, rail, mises en circulation)
AUTRES = {"Evolution du volume de fret routier": "Fret routier",
          "Trafic de véhicules de transports de marchandises sur le réseau routier": "Trafic marchandises",
          "Trafic de véhicules de transports de passagers sur le réseau routier": "Trafic passagers",
          "Evolution des premières mise en circulation du parc automobile 4 roues et plus immatriculés": "Premières mises en circulation (4 roues et +)",
          "Evolution du parc automobile 4 roues et plus immatriculé": "Parc 4 roues et plus",
          "Evolution des deux roues et assimilées immatriculées": "Deux-roues immatriculés",
          "Réseau total (chemins de fer-km)": "Réseau ferroviaire (km)",
          "Evolution du volume de tonne de marchandises transportées par rails": "Fret ferroviaire (tonnes)",
          "Nombre de permis de conduire délivrés aux examens de permis de conduire": "Permis délivrés (total)"}
autres = tr[tr.indicateur.isin(AUTRES)].assign(libelle=lambda d: d.indicateur.map(AUTRES))
autres.to_csv(OUT / "ts_transport.csv", index=False)

# ----------------------------------------------------------------- 7. contours cartographiques
adm2 = json.load(open(GEO / "togo_adm2.geojson", encoding="utf-8"))
RENAME_GEO = {"TANDJOUARE": "TANDJOARE", "PLAINE DE MO": "MO", "LOME COMMUNE": "GOLFE"}
groups: dict[str, list] = {}
for f in adm2["features"]:
    k = RENAME_GEO.get(norm(f["properties"]["shapeName"]), norm(f["properties"]["shapeName"]))
    groups.setdefault(k, []).append(shape(f["geometry"]))
LIB_MAP = {"GOLFE": "Golfe + Agoè-Nyivé (Grand Lomé)", "KPENDJAL": "Kpendjal + Kpendjal-Ouest", "OTI": "Oti + Oti-Sud"}
geo_pref = {"type": "FeatureCollection", "features": [
    {"type": "Feature", "id": k, "properties": {"map_key": k, "libelle": LIB_MAP.get(k, LIB_PREF.get(k, k.title()))},
     "geometry": mapping(unary_union(v).simplify(0.002, preserve_topology=True))} for k, v in groups.items()]}
json.dump(geo_pref, open(OUT / "prefectures.geojson", "w", encoding="utf-8"))
missing = set(pref.map_key) - set(groups)
assert not missing, f"préfectures sans contour : {missing}"

adm1 = json.load(open(GEO / "togo_adm1.geojson", encoding="utf-8"))
reg_geoms = {norm(f["properties"]["shapeName"]).replace(" REGION", ""): shape(f["geometry"]) for f in adm1["features"]}
gl = unary_union(groups["GOLFE"])
reg_geoms["MARITIME"] = reg_geoms["MARITIME"].difference(gl)
reg_geoms["GRAND LOME"] = gl
LIB_REG = {"SAVANES": "Savanes", "KARA": "Kara", "CENTRALE": "Centrale", "PLATEAUX": "Plateaux",
           "MARITIME": "Maritime", "GRAND LOME": "Grand Lomé"}
json.dump({"type": "FeatureCollection", "features": [
    {"type": "Feature", "id": LIB_REG[k], "properties": {"region": LIB_REG[k]},
     "geometry": mapping(g.simplify(0.002, preserve_topology=True))} for k, g in reg_geoms.items()]},
    open(OUT / "regions.geojson", "w", encoding="utf-8"))

# ----------------------------------------------------------------- 8. indicateurs nationaux
last = int(secu.annee.max())
s22 = secu[secu.annee == last].iloc[0]
p22 = parc[parc.annee == parc.annee.max()]
parc_total = float(p22[p22.type == "Total"].value.iloc[0])
parc_2r = float(p22[p22.type == "Deux-roues"].value.iloc[0])
per22 = permis[permis.annee == permis.annee.max()]
kpi = {
    "population_2022": POP_TOTAL,
    "annee_securite": last,
    "accidents": int(s22.accidents), "morts": int(s22.morts), "blesses": int(s22.blesses),
    "accidents_100k": float(s22.accidents_100k), "morts_100k": float(s22.morts_100k),
    "letalite_pct": float(s22.letalite_pct),
    "accidents_2015": int(secu.loc[secu.annee == 2015, "accidents"].iloc[0]),
    "parc_total": int(parc_total), "parc_deux_roues": int(parc_2r),
    "part_deux_roues": round(parc_2r / parc_total * 100, 1),
    "parc_1990": int(parc[(parc.type == "Total") & (parc.annee == 1990)].value.iloc[0]),
    "permis_total": int(per22[per22.categorie == "Total"].value.iloc[0]),
    "permis_moto": int(per22[per22.categorie == "Moto (A)"].value.iloc[0]),
    "permis_voiture": int(per22[per22.categorie == "Voiture légère (B)"].value.iloc[0]),
    "km_routes": round(float(ro.km.sum()), 0),
    "km_revetues": round(float(ro[ro.revetue].km.sum()), 0),
    "part_revetue": round(float(ro[ro.revetue].km.sum() / ro.km.sum() * 100), 1),
    "segments": int(len(ro)),
    "m_route_par_hab": round(float(ro.km.sum() * 1000 / POP_TOTAL), 2),
    "auto_ecoles": int(len(ae)),
    "auto_ecoles_agreees": int(ae.agreee.sum()),
    "auto_ecoles_non_agreees": int((ae.statut == "Non agréée").sum()),
    "auto_ecoles_statut_inconnu": int((ae.statut == "Non renseigné").sum()),
    "part_non_agreees": round(float((ae.statut == "Non agréée").mean() * 100), 1),
    "part_agreees": round(float(ae.agreee.mean() * 100), 1),
    "prefectures_sans_auto_ecole": int(pref.sans_auto_ecole.sum()),
    "population_sans_auto_ecole": int(pref.loc[pref.sans_auto_ecole, "population"].sum()),
    "prefectures_sans_auto_ecole_agreee": int(pref.sans_auto_ecole_agreee.sum()),
    "hab_par_auto_ecole": round(POP_TOTAL / len(ae)),
    "part_auto_ecoles_maritime": round(float((ae.region.isin(["Maritime", "Grand Lomé"])).mean() * 100), 1),
    "km_etat": {r.etat_lib: round(float(r.km), 0) for r in etat_national.itertuples() if isinstance(r.etat_lib, str)},
}
json.dump(kpi, open(OUT / "kpi_national.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)

# ----------------------------------------------------------------- rapport
print("=== Pipeline OK ===")
print(f"population                     : {POP_TOTAL:,} · {len(pref)} préfectures · {len(reg)} régions")
print(f"réseau routier                 : {len(ro)} segments · {ro.km.sum():,.0f} km dont {ro[ro.revetue].km.sum():,.0f} revêtus")
print(f"  état joint par n° de RN      : {ro.rn.notna().sum()}/{len(ro)} segments · {(ro.etat_dominant != 'Non renseigné').sum()} avec état")
print(f"auto-écoles                    : {len(ae)} dont {int(ae.agreee.sum())} agréées · {int(pref.sans_auto_ecole.sum())} préfectures sans aucune")
print(f"sécurité routière              : {int(secu.annee.min())}-{last} · {int(s22.accidents):,} accidents, {int(s22.morts)} morts en {last}")
print(f"  taux recalculés              : {s22.accidents_100k} accidents/100k · {s22.morts_100k} morts/100k · létalité {s22.letalite_pct} %")
print(f"parc automobile                : {int(parc_total):,} véhicules dont {kpi['part_deux_roues']} % de deux-roues")
print(f"permis {int(per22.annee.iloc[0])}                    : {kpi['permis_total']:,} dont moto {kpi['permis_moto']:,} · voiture {kpi['permis_voiture']:,}")
print(f"GeoJSON routes                 : {len(feats)} entités, {(OUT / 'routes.geojson').stat().st_size / 1e6:.1f} Mo")
