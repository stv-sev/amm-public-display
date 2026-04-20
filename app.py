"""
AMM Public Display – Live Rangliste (Supabase only, read-only)
Deployment: Streamlit Cloud
Secrets: SUPABASE_URL, SUPABASE_KEY
"""
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="AMM Live Rangliste",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Auto-refresh every 10 seconds
st_autorefresh(interval=10_000, key="live_refresh")

from display_backend import get_competitions, get_data_for_comp
from display_views import show_gesamtrangliste, show_geraet, show_team

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 1rem; }
    h1 { font-size: 2rem; }
    .stTabs [data-baseweb="tab"] { font-size: 1.1rem; padding: 0.5rem 1.5rem; }
</style>
""", unsafe_allow_html=True)

# ── Competition selector ──────────────────────────────────────────────────────
comps = get_competitions()
if not comps:
    st.warning("⏳ Noch keine Wettkampfdaten verfügbar.")
    st.stop()

comp_opts = {f"{c['name']} – {c.get('location','')} {c.get('date','')}".strip(" –"): c["id"]
             for c in comps}
cid = comp_opts[st.selectbox("Wettkampf", list(comp_opts.keys()),
                              label_visibility="collapsed")]

data = get_data_for_comp(cid)
if not data:
    st.info("⏳ Noch keine Noten vorhanden.")
    st.stop()

comp = next(c for c in comps if c["id"] == cid)
st.markdown(f"# 🏆 {comp['name']}")
if comp.get("location") or comp.get("date"):
    st.caption(f"📍 {comp.get('location','')}   📅 {comp.get('date','')}")

mode = data["cfg"].get("comp_mode", "team")

# ── Tabs ──────────────────────────────────────────────────────────────────────
if mode == "team":
    tab_ges, tab_geraet, tab_team = st.tabs(["🤸 Gesamtrangliste", "🔩 Gerät", "🏅 Team"])
    with tab_ges:    show_gesamtrangliste(data)
    with tab_geraet: show_geraet(data)
    with tab_team:   show_team(data)
else:
    tab_ges, tab_geraet = st.tabs(["🤸 Gesamtrangliste", "🔩 Gerät"])
    with tab_ges:    show_gesamtrangliste(data)
    with tab_geraet: show_geraet(data)

# ── Footer ────────────────────────────────────────────────────────────────────
import datetime
st.markdown("---")
st.caption(f"🔄 Letzte Aktualisierung: {datetime.datetime.now().strftime('%H:%M:%S')}  |  "
           f"Auto-Refresh alle 10 Sekunden")
