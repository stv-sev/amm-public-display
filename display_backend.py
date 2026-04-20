"""
display_backend.py – Liest ausschliesslich von Supabase (read-only)
Keine SQLite-Abhängigkeit.
"""
import streamlit as st

APP_IDS   = [1, 2, 3, 4, 5, 6]
APP_NAMES = {1:"Boden", 2:"Pferd", 3:"Ringe", 4:"Sprung", 5:"Barren", 6:"Reck"}
APP_SHORT = {1:"Bo",    2:"Pf",    3:"Ri",    4:"Sp",     5:"Ba",    6:"Re"}


@st.cache_resource
def _sb():
    from supabase import create_client
    url = st.secrets.get("SUPABASE_URL", "")
    key = st.secrets.get("SUPABASE_KEY", "")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL und SUPABASE_KEY müssen in secrets.toml konfiguriert sein.")
    return create_client(url, key)


@st.cache_data(ttl=8)  # Cache 8s (refresh every 10s)
def get_competitions():
    try:
        r = _sb().table("competitions").select("*").order("id", desc=True).execute()
        return r.data
    except Exception:
        return []


@st.cache_data(ttl=8)
def get_data_for_comp(cid: int) -> dict | None:
    """Fetch all data for one competition and compute scores."""
    try:
        sb = _sb()
        cfg_rows = sb.table("config").select("*").eq("competition_id", cid).execute().data
        cfg      = {r["key"]: r["value"] for r in cfg_rows}
        num_e    = int(cfg.get("num_e_scores", 3))

        athletes = sb.table("athletes").select("*").eq("competition_id", cid).execute().data
        teams    = sb.table("teams").select("*").eq("competition_id", cid).execute().data
        scores   = sb.table("scores").select("*").eq("competition_id", cid).execute().data

        if not athletes or not scores:
            return None

        team_map = {t["id"]: t for t in teams}
        ath_map  = {a["id"]: a for a in athletes}

        # Compute final scores
        score_lookup = {}  # aid -> {app_id -> {d,e,p,b,final}}
        for s in scores:
            aid, app = s["athlete_id"], s["apparatus_id"]
            d  = s.get("d_score") or 0
            p  = s.get("penalty") or 0
            b  = s.get("bonus")   or 0
            ev = [s.get(f"e{i}") for i in range(1, 6) if s.get(f"e{i}") is not None][:num_e]
            if ev:
                e_avg = (sum(ev)-max(ev)-min(ev))/(len(ev)-2) if len(ev) >= 3 else sum(ev)/len(ev)
            else:
                e_avg = 0
            final = round(d + e_avg - p + b, 3) if (d or e_avg) else None
            score_lookup.setdefault(aid, {})[app] = {
                "d": d, "e": round(e_avg, 3), "p": p, "b": b, "final": final
            }

        # Athlete totals
        ath_totals = {
            a["id"]: round(
                sum(v["final"] for v in score_lookup.get(a["id"], {}).values()
                    if v["final"] is not None), 3)
            for a in athletes
        }

        return {
            "cfg":          cfg,
            "athletes":     athletes,
            "teams":        teams,
            "team_map":     team_map,
            "ath_map":      ath_map,
            "score_lookup": score_lookup,
            "ath_totals":   ath_totals,
            "num_e":        num_e,
        }
    except Exception as e:
        st.error(f"Datenbankfehler: {e}")
        return None
