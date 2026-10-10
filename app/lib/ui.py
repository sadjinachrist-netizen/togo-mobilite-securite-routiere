"""Charte graphique, composants et thème Plotly — Mobilité et sécurité routière."""
from __future__ import annotations

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

# ---------------------------------------------------------------- palette
C = {
    "green": "#0F6E4E", "green_dark": "#0B3D2E", "green_light": "#DCEFE6", "lime": "#4ADE80",
    "gold": "#D9A521", "red": "#C8453B", "red_light": "#FBE9E7", "ink": "#14201A", "muted": "#5F6B66",
    "bg": "#F6F8F7", "card": "#FFFFFF", "line": "#E3E8E5", "blue": "#2F6690",
}
REGION_COLORS = {"Grand Lomé": "#0B3D2E", "Maritime": "#0F6E4E", "Plateaux": "#3A9A6E",
                 "Centrale": "#D9A521", "Kara": "#B8742A", "Savanes": "#C8453B"}
ETAT_COLORS = {"Bon état": "#1F8A5B", "État moyen": "#D9A521", "Mauvais état": "#C8453B",
               "Travaux en cours": "#2F6690", "Non renseigné": "#B8C4BE"}
STATUT_COLORS = {"Agréée": "#0B3D2E", "Antenne agréée": "#3A9A6E", "Non agréée": "#C8453B", "Non renseigné": "#B8C4BE"}
SEQ = ["#E8F3EE", "#BFE0D0", "#8CC7AC", "#57A986", "#2E8A66", "#0F6E4E", "#0B3D2E"]
SEQ_RED = ["#FDF3F2", "#F8D5D1", "#F0ADA6", "#E5827A", "#D65C52", "#C8453B", "#8E2C25"]

FONT = "Inter, 'Segoe UI', Helvetica, Arial, sans-serif"

_tpl = go.layout.Template()
_tpl.layout = go.Layout(
    font=dict(family=FONT, size=13, color=C["ink"]),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=40, b=10),
    colorway=[C["green"], C["gold"], C["red"], "#3A9A6E", C["blue"], "#8FBFA3"],
    xaxis=dict(showgrid=False, zeroline=False, linecolor=C["line"], title_font_size=12),
    yaxis=dict(showgrid=True, gridcolor=C["line"], zeroline=False, title_font_size=12),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title=None, font_size=12),
    title=dict(font=dict(size=15, color=C["green_dark"]), x=0, xanchor="left"),
    hoverlabel=dict(bgcolor="white", font_size=12, font_family=FONT),
)
pio.templates["togo"] = _tpl
pio.templates.default = "togo"


# ---------------------------------------------------------------- formats
def fmt(n, dec: int = 0, suffix: str = "") -> str:
    if n is None or (isinstance(n, float) and n != n):
        return "—"
    return f"{n:,.{dec}f}".replace(",", " ").replace(".", ",") + suffix


# ---------------------------------------------------------------- CSS
CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] {{ font-family: {FONT}; }}
.block-container {{ padding-top: 1.3rem; padding-bottom: 2.5rem; max-width: 1280px; }}
section[data-testid="stSidebar"] {{ background: {C['green_dark']}; }}
section[data-testid="stSidebar"] * {{ color: #E6F0EA; }}
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"] {{ border-radius: 8px; margin: 1px 0; }}
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"]:hover {{ background: rgba(255,255,255,.08); }}
section[data-testid="stSidebar"] a[aria-current="page"] {{ background: rgba(74,222,128,.18); }}
section[data-testid="stSidebar"] a[aria-current="page"] span {{ color: {C['lime']}; font-weight: 600; }}
section[data-testid="stSidebar"] [data-testid="stSidebarNavSectionHeader"] {{ color: {C['lime']}; letter-spacing: .08em; font-size: .72rem; }}
section[data-testid="stSidebar"] label p {{ font-size: .82rem !important; color: #BFD6C9 !important; font-weight: 600; }}
h1 {{ font-weight: 800; letter-spacing: -.02em; color: {C['green_dark']}; font-size: 2.05rem; }}
h2, h3 {{ font-weight: 700; color: {C['green_dark']}; }}
.kicker {{ color: {C['muted']}; font-size: 1.02rem; margin: -.4rem 0 1.2rem 0; }}
.sect {{ color: {C['muted']}; font-size: .74rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; margin: 1.4rem 0 .1rem; }}
.sect-sub {{ color: {C['muted']}; font-size: .9rem; margin: 0 0 .7rem; }}
.kpi {{ background: {C['card']}; border: 1px solid {C['line']}; border-left: 3px solid {C['green']}; border-radius: 10px;
        padding: .75rem .9rem .6rem; height: 100%; }}
.kpi.red {{ border-left-color: {C['red']}; }}
.kpi.gold {{ border-left-color: {C['gold']}; }}
.kpi .lbl {{ color: {C['ink']}; font-size: .83rem; font-weight: 600; line-height: 1.25; }}
.kpi .val {{ font-size: 1.85rem; font-weight: 800; color: {C['green_dark']}; line-height: 1.1; margin: .2rem 0 .1rem; }}
.kpi.red .val {{ color: {C['red']}; }}
.kpi.gold .val {{ color: #A77A10; }}
.kpi .sub {{ color: {C['muted']}; font-size: .78rem; line-height: 1.3; }}
.kpi .src {{ color: #93A29B; font-size: .68rem; margin-top: .45rem; padding-top: .35rem; border-top: 1px dotted {C['line']}; }}
.insight {{ background: {C['green_light']}; border-left: 4px solid {C['green']}; border-radius: 8px; padding: .8rem 1rem; margin: .5rem 0 1.1rem; }}
.insight.red {{ background: {C['red_light']}; border-left-color: {C['red']}; }}
.insight.gold {{ background: #FBF3DD; border-left-color: {C['gold']}; }}
.reco {{ background: {C['card']}; border: 1px solid {C['line']}; border-radius: 12px; padding: .9rem 1.05rem; margin-bottom: .75rem; }}
.reco .n {{ display:inline-block; width:28px; height:28px; border-radius:50%; background:{C['green']}; color:#fff; text-align:center; line-height:28px; font-weight:700; margin-right:.55rem; }}
.reco .n.red {{ background: {C['red']}; }}
.reco .t {{ font-weight: 700; font-size: 1.03rem; color: {C['green_dark']}; }}
.reco .impact {{ font-size: 1.45rem; font-weight: 800; color: {C['red']}; }}
.reco .impact small {{ font-size: .78rem; color: {C['muted']}; font-weight: 500; }}
.reco p {{ margin: .35rem 0 0; color: {C['ink']}; font-size: .93rem; }}
.badge {{ display:inline-block; padding:.15rem .55rem; border-radius:999px; font-size:.7rem; font-weight:700; letter-spacing:.04em; }}
.badge.red {{ background:{C['red_light']}; color:{C['red']}; }}
.badge.green {{ background:{C['green_light']}; color:{C['green']}; }}
.badge.gold {{ background:#FBF3DD; color:#8A6510; }}
.src-line {{ color: {C['muted']}; font-size: .76rem; margin-top: -.5rem; }}
footer {{ visibility: hidden; }}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def header(title: str, kicker_text: str) -> None:
    st.markdown(f"# {title}")
    st.markdown(f"<div class='kicker'>{kicker_text}</div>", unsafe_allow_html=True)


def section(label: str, sub: str = "") -> None:
    st.markdown(f"<div class='sect'>{label}</div>" + (f"<div class='sect-sub'>{sub}</div>" if sub else ""),
                unsafe_allow_html=True)


def kpi_row(items: list[dict]) -> None:
    """items : {label, value, sub, source, tone in {'', 'red', 'gold'}}"""
    for col, it in zip(st.columns(len(items)), items):
        col.markdown(
            f"<div class='kpi {it.get('tone', '')}'>"
            f"<div class='lbl'>{it['label']}</div>"
            f"<div class='val'>{it['value']}</div>"
            f"<div class='sub'>{it.get('sub', '')}</div>"
            f"<div class='src'>{it.get('source', '')}</div></div>",
            unsafe_allow_html=True)


def insight(text: str, kind: str = "") -> None:
    st.markdown(f"<div class='insight {kind}'>{text}</div>", unsafe_allow_html=True)


def reco(n: int, title: str, impact: str, impact_label: str, body: str, tag: str, tag_kind: str, red: bool = False) -> None:
    st.markdown(
        f"""<div class='reco'><span class='n {'red' if red else ''}'>{n}</span><span class='t'>{title}</span>
<span class='badge {tag_kind}' style='float:right;margin-top:.3rem'>{tag}</span>
<div style='margin-top:.45rem'><span class='impact'>{impact} <small>{impact_label}</small></span></div>
<p>{body}</p></div>""", unsafe_allow_html=True)


def source(text: str) -> None:
    st.markdown(f"<div class='src-line'>Source : {text}</div>", unsafe_allow_html=True)


def plotly(fig: go.Figure, height: int = 380) -> None:
    fig.update_layout(height=height)
    st.plotly_chart(fig, use_container_width=True,
                    config={"displaylogo": False, "locale": "fr", "modeBarButtonsToRemove": ["lasso2d", "select2d"]})
