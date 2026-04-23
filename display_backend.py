"""
display_backend.py – Supabase-only Datenzugriff (read-only, kein SQLite)
Deployment: Streamlit Cloud. Secrets: SUPABASE_URL, SUPABASE_KEY
"""
import streamlit as st

APP_IDS   = [1, 2, 3, 4, 5, 6]
APP_NAMES = {1:"Boden", 2:"Pferd", 3:"Ringe", 4:"Sprung", 5:"Barren", 6:"Reck"}
APP_SHORT = {1:"Bo",    2:"Pf",    3:"Ri",    4:"Sp",     5:"Ba",    6:"Re"}


@st.cache_resource
def _sb():
    from supabase import create_client
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


@st.cache_data(ttl=5)
def get_competitions():
    try:
        return _sb().table("competitions").select("*").order("id", desc=True).execute().data
    except Exception:
        return []


@st.cache_data(ttl=5)
def get_config(cid):
    try:
        rows = _sb().table("config").select("key,value").eq("competition_id", cid).execute().data
        return {r["key"]: r["value"] for r in rows}
    except Exception:
        return {}


@st.cache_data(ttl=5)
def get_teams(cid):
    try:
        return _sb().table("teams").select("*").eq("competition_id", cid).execute().data
    except Exception:
        return []


@st.cache_data(ttl=5)
def get_athletes(cid):
    try:
        return _sb().table("athletes").select("*").eq("competition_id", cid).execute().data
    except Exception:
        return []


@st.cache_data(ttl=5)
def get_scores(cid):
    """Scores mit Athleten- und Team-Infos angereichert (für Teams/Einzel/Gerät-Tab)."""
    try:
        sb = _sb()
        scores   = sb.table("scores").select("*").eq("competition_id", cid).execute().data
        athletes = (sb.table("athletes")
                      .select("id,first_name,last_name,club,team_id,category,year_of_birth")
                      .eq("competition_id", cid).execute().data)
        teams    = (sb.table("teams")
                      .select("id,name,abbreviation")
                      .eq("competition_id", cid).execute().data)
        _enrich(scores, athletes, teams)
        return scores
    except Exception:
        return []


@st.cache_data(ttl=30)
def get_start_positions(cid: int):
    try:
        sb = _sb()
        r = sb.table("start_positions").select("*").eq("competition_id", cid).execute()
        return r.data
    except Exception:
        return []


@st.cache_data(ttl=30)
def get_schedule(cid: int):
    try:
        sb = _sb()
        r = sb.table("schedule").select("*").eq("competition_id", cid).order("id").execute()
        return r.data
    except Exception:
        return []


def get_live_scores(cid, limit=20):
    """Letzte Noten – kein Cache, direkt von Supabase (für Live-Tab)."""
    try:
        sb = _sb()
        scores   = (sb.table("scores").select("*")
                      .eq("competition_id", cid)
                      .order("updated_at", desc=True)
                      .limit(limit).execute().data)
        athletes = (sb.table("athletes")
                      .select("id,first_name,last_name,club,team_id,category")
                      .eq("competition_id", cid).execute().data)
        teams    = (sb.table("teams")
                      .select("id,name,abbreviation")
                      .eq("competition_id", cid).execute().data)
        _enrich(scores, athletes, teams)
        return scores
    except Exception:
        return []


def _enrich(scores, athletes, teams):
    ath_map  = {a["id"]: a for a in athletes}
    team_map = {t["id"]: t for t in teams}
    for s in scores:
        a = ath_map.get(s["athlete_id"], {})
        t = team_map.get(a.get("team_id"), {})
        s["first_name"]    = a.get("first_name", "")
        s["last_name"]     = a.get("last_name", "")
        s["club"]          = a.get("club", "")
        s["category"]      = a.get("category", "")
        s["year_of_birth"] = a.get("year_of_birth", "")
        s["team_abbr"]     = t.get("abbreviation", "")
        s["team_name"]     = t.get("name", "")
