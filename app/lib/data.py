"""Chargement des données préparées et filtres globaux partagés entre les pages."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data" / "processed"

REGION_ORDER = ["Grand Lomé", "Maritime", "Plateaux", "Centrale", "Kara", "Savanes"]


@st.cache_data(show_spinner=False)
def kpi() -> dict:
    return json.load(open(P / "kpi_national.json", encoding="utf-8"))


@st.cache_data(show_spinner=False)
def regions() -> pd.DataFrame:
    d = pd.read_csv(P / "regions.csv")
    d["region"] = pd.Categorical(d["region"], REGION_ORDER, ordered=True)
    return d.sort_values("region").reset_index(drop=True)


@st.cache_data(show_spinner=False)
def prefectures() -> pd.DataFrame:
    return pd.read_csv(P / "prefectures.csv")


@st.cache_data(show_spinner=False)
def routes() -> pd.DataFrame:
    return pd.read_csv(P / "routes.csv")


@st.cache_data(show_spinner=False)
def auto_ecoles() -> pd.DataFrame:
    return pd.read_csv(P / "auto_ecoles.csv")


@st.cache_data(show_spinner=False)
def securite() -> pd.DataFrame:
    return pd.read_csv(P / "ts_securite_routiere.csv")


@st.cache_data(show_spinner=False)
def parc() -> pd.DataFrame:
    return pd.read_csv(P / "ts_parc_vehicules.csv")


@st.cache_data(show_spinner=False)
def permis() -> pd.DataFrame:
    return pd.read_csv(P / "ts_permis.csv")


@st.cache_data(show_spinner=False)
def transport() -> pd.DataFrame:
    return pd.read_csv(P / "ts_transport.csv")


@st.cache_data(show_spinner=False)
def etat_national() -> pd.DataFrame:
    return pd.read_csv(P / "etat_reseau_national.csv")


@st.cache_data(show_spinner=False)
def etat_par_rn() -> pd.DataFrame:
    return pd.read_csv(P / "etat_par_route_nationale.csv")


@st.cache_data(show_spinner=False)
def geo_prefectures() -> dict:
    return json.load(open(P / "prefectures.geojson", encoding="utf-8"))


@st.cache_data(show_spinner=False)
def geo_regions() -> dict:
    return json.load(open(P / "regions.geojson", encoding="utf-8"))


@st.cache_data(show_spinner=False)
def geo_routes() -> dict:
    return json.load(open(P / "routes.geojson", encoding="utf-8"))


# ------------------------------------------------------------------ filtres globaux
def sidebar_filters() -> dict:
    """Filtres territoriaux persistants, affichés dans la barre latérale de chaque page."""
    pref = prefectures()
    st.sidebar.markdown("<div style='margin-top:.6rem'></div>", unsafe_allow_html=True)
    st.sidebar.markdown(
        "<div style='color:#4ADE80;font-size:.72rem;font-weight:700;letter-spacing:.08em'>FILTRES TERRITORIAUX</div>",
        unsafe_allow_html=True)

    regs = st.sidebar.multiselect("Région", REGION_ORDER, default=[], placeholder="Toutes les régions",
                                  key="f_regions")
    base = pref if not regs else pref[pref.region.isin(regs)]
    prefs = st.sidebar.multiselect("Préfecture", sorted(base.prefecture), default=[],
                                   placeholder="Toutes les préfectures", key="f_prefs")

    st.sidebar.markdown(
        "<div style='color:#4ADE80;font-size:.72rem;font-weight:700;letter-spacing:.08em;margin-top:.9rem'>RÉSEAU ET FORMATION</div>",
        unsafe_allow_html=True)
    types = st.sidebar.multiselect("Type de route", sorted(routes().route_type.unique()), default=[],
                                   placeholder="Tous les types", key="f_types")
    statuts = st.sidebar.multiselect("Statut des auto-écoles", ["Agréée", "Antenne agréée", "Non agréée", "Non renseigné"],
                                     default=[], placeholder="Tous les statuts", key="f_statuts")

    active = bool(regs or prefs or types or statuts)
    if active and st.sidebar.button("Réinitialiser les filtres", use_container_width=True):
        for k in ("f_regions", "f_prefs", "f_types", "f_statuts"):
            st.session_state.pop(k, None)
        st.rerun()

    sel = base if not prefs else base[base.prefecture.isin(prefs)]
    scope = "Togo entier"
    if prefs:
        scope = ", ".join(prefs) if len(prefs) <= 3 else f"{len(prefs)} préfectures"
    elif regs:
        scope = ", ".join(regs) if len(regs) <= 3 else f"{len(regs)} régions"
    if active:
        st.sidebar.markdown(
            f"<div style='font-size:.76rem;color:#9FB8AC;margin-top:.5rem'>Périmètre : <b style='color:#E6F0EA'>{scope}</b> · "
            f"{len(sel)} préfecture(s) · {sel.population.sum():,.0f} habitants</div>".replace(",", " "),
            unsafe_allow_html=True)
    return {"regions": regs, "prefectures": prefs, "types": types, "statuts": statuts,
            "pref": sel, "scope": scope, "active": active}


def apply_routes(f: dict) -> pd.DataFrame:
    d = routes()
    if f["prefectures"]:
        d = d[d.prefecture.isin(f["prefectures"])]
    elif f["regions"]:
        d = d[d.region.isin(f["regions"])]
    if f["types"]:
        d = d[d.route_type.isin(f["types"])]
    return d


def apply_ecoles(f: dict) -> pd.DataFrame:
    d = auto_ecoles()
    if f["prefectures"]:
        d = d[d.prefecture.isin(f["prefectures"])]
    elif f["regions"]:
        d = d[d.region.isin(f["regions"])]
    if f["statuts"]:
        d = d[d.statut.isin(f["statuts"])]
    return d
