"""
AMM Public Display – Cloud Version (Supabase only, read-only)
Deployment: Streamlit Cloud. Secrets: SUPABASE_URL, SUPABASE_KEY
"""
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="AMM Live Rangliste",
    page_icon="🏆",
    layout="centered",
    initial_sidebar_state="collapsed",
)

from display_backend import (
    _sb, get_competitions, get_config, get_teams, get_athletes,
    get_scores, get_live_scores, APP_IDS, APP_SHORT, APP_NAMES,
)

try:
    from streamlit_autorefresh import st_autorefresh
    HAS_AUTOREFRESH = True
except ImportError:
    HAS_AUTOREFRESH = False

# ── Konstanten ─────────────────────────────────────────────────────────────────
RANK_COLORS = {1: "#FFD700", 2: "#C0C0C0", 3: "#CD7F32"}
RANK_MEDAL  = {1: "🥇", 2: "🥈", 3: "🥉"}
CATEGORIES  = ["EP", "P1", "P2", "P3"]

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
.rl-wrap { font-family:'Inter',sans-serif; max-width:720px; margin:0 auto; padding:0 4px; }
.rl-header { text-align:center; padding:1rem 0 0.6rem; }
.rl-header h1 { font-size:1.4rem; font-weight:700; margin:0; color:#0D4E73; }
.rl-header p  { font-size:0.82rem; color:#888; margin:2px 0 0; }

.team-card { background:#fff; border-radius:14px; margin-bottom:14px;
             box-shadow:0 2px 12px rgba(0,0,0,0.08); overflow:hidden; }
.team-header { display:flex; align-items:center; gap:12px;
               padding:12px 16px; border-bottom:1px solid #f0f0f0; }
.team-rank   { width:36px; height:36px; border-radius:50%; display:flex;
               align-items:center; justify-content:center;
               font-weight:700; font-size:1rem; flex-shrink:0; }
.team-name strong { font-size:0.95rem; font-weight:700; color:#0D4E73; display:block; }
.team-name span   { font-size:0.72rem; color:#888; }
.team-total       { font-size:1.25rem; font-weight:700; color:#0D4E73; text-align:right; }
.team-total small { font-size:0.62rem; color:#888; display:block; }

.app-chips { display:grid; grid-template-columns:repeat(3,1fr); gap:6px;
             padding:8px 12px; border-bottom:1px solid #f0f0f0; }
.app-chip  { background:#f7f8fc; border-radius:8px;
             padding:5px 3px; text-align:center; }
.app-chip.start { background:#D6EAF3; border:1.5px solid #2C7FA6; }
.app-chip .app-name { font-size:0.68rem; font-weight:600; color:#15608A; display:block; }
.app-chip .app-val  { font-size:0.85rem; font-weight:700; color:#0D4E73; }
.app-chip .app-rank { font-size:0.58rem; color:#999; }
.app-chip.no-score .app-val { color:#ccc; }

.turner-list { padding:4px 12px 10px; }
.turner-item { padding:5px 0; border-bottom:1px solid #f5f5f5; font-size:0.78rem; }
.turner-item:last-child { border-bottom:none; }
.turner-name { font-weight:500; color:#0D4E73; }
.turner-meta { font-size:0.68rem; color:#aaa; margin-bottom:2px; }
.turner-scores { display:flex; gap:3px; flex-wrap:wrap; }
.score-chip { font-size:0.68rem; padding:1px 5px; border-radius:4px;
              background:#D6EAF3; color:#2C7FA6; font-weight:500; }
.score-chip.struck { background:#f5f5f5; color:#bbb;
                     text-decoration:line-through; font-style:italic; }
.score-chip.hc     { background:#FFE0F0; color:#E6007E; }

.ind-card   { background:#fff; border-radius:12px; margin-bottom:8px;
              box-shadow:0 1px 8px rgba(0,0,0,0.07); overflow:hidden; }
.ind-header { display:flex; align-items:center; gap:10px; padding:10px 14px; }
.ind-rank   { width:30px; height:30px; border-radius:50%; display:flex;
              align-items:center; justify-content:center;
              font-weight:700; font-size:0.82rem; flex-shrink:0; }
.ind-name strong { font-size:0.9rem; font-weight:600; color:#0D4E73; }
.ind-name small  { font-size:0.68rem; color:#888; }
.ind-total  { font-size:1.05rem; font-weight:700; color:#0D4E73; }
.ind-scores { display:flex; gap:4px; padding:0 14px 10px; flex-wrap:wrap; }

.app-card       { background:#fff; border-radius:12px; margin-bottom:12px;
                  box-shadow:0 2px 8px rgba(0,0,0,0.07); overflow:hidden; }
.app-card-title { padding:10px 16px; background:#0D4E73; color:#fff;
                  font-size:0.88rem; font-weight:700; }
.app-row        { display:flex; align-items:center; padding:8px 16px;
                  border-bottom:1px solid #f5f5f5; gap:8px; }
.app-row:last-child { border-bottom:none; }
.app-row-rank   { width:22px; font-size:0.78rem; font-weight:700; color:#888; }
.app-row-name   { flex:1; font-size:0.82rem; font-weight:500; color:#0D4E73; }
.app-row-meta   { font-size:0.68rem; color:#aaa; }
.app-row-score  { font-size:0.95rem; font-weight:700; color:#0D4E73; }

/* Live-Ticker */
.ticker-card { background:#fff; border-radius:12px; margin-bottom:10px;
               box-shadow:0 1px 8px rgba(0,0,0,0.07);
               display:flex; align-items:center; padding:10px 14px; gap:12px; }
.ticker-num  { width:26px; height:26px; border-radius:50%; background:#D6EAF3;
               display:flex; align-items:center; justify-content:center;
               font-size:0.72rem; font-weight:700; color:#2C7FA6; flex-shrink:0; }
.ticker-body { flex:1; }
.ticker-body strong { font-size:0.88rem; color:#0D4E73; display:block; }
.ticker-body small  { font-size:0.7rem; color:#888; }
.ticker-score { text-align:right; }
.ticker-score .app  { font-size:0.7rem; color:#888; }
.ticker-score .note { font-size:1.05rem; font-weight:700; color:#0D4E73; }
.ticker-score .time { font-size:0.62rem; color:#aaa; display:block; }

/* Live-Badge */
.live-badge { display:inline-flex; align-items:center; gap:6px;
              background:#FFE0F0; color:#E6007E; border-radius:20px;
              padding:3px 10px; font-size:0.75rem; font-weight:700;
              margin-bottom:10px; }
.live-dot { width:8px; height:8px; border-radius:50%; background:#E6007E;
            animation:pulse 1.2s infinite; }
@keyframes pulse {
  0%,100% { opacity:1; transform:scale(1); }
  50%      { opacity:0.4; transform:scale(1.3); }
}

.no-data { text-align:center; padding:32px; color:#bbb; font-size:0.88rem; }
.stand   { text-align:center; font-size:0.7rem; color:#bbb; margin-top:10px; padding-bottom:20px; }
</style>
"""


# ── Score-Berechnung ───────────────────────────────────────────────────────────

def _calc_e(e_vals, num_e):
    """E_avg: bei 3+ Noten höchste/niedrigste streichen, Rest mitteln."""
    vals = [v for v in e_vals if v is not None][:num_e]
    if not vals:
        return None
    if len(vals) >= 3:
        return (sum(vals) - max(vals) - min(vals)) / (len(vals) - 2)
    return sum(vals) / len(vals)


def _final(s):
    return s.get("final_score") if s else None


def _enrich_scores(scores, num_e):
    """Berechnet e_wert und final_score in-place. NIE 10-E verwenden."""
    for s in scores:
        e = _calc_e([s.get(f"e{i}") for i in range(1, 6)], num_e)
        s["e_wert"] = round(e, 3) if e is not None else None
        d   = s.get("d_score") or 0
        pen = s.get("penalty") or 0
        bon = s.get("bonus") or 0
        s["final_score"] = round(d + e - pen + bon, 3) if (
            s.get("d_score") is not None and e is not None
        ) else None
        s["hors_concours"] = False


# ── Supabase Realtime ──────────────────────────────────────────────────────────

def _setup_realtime(cid):
    """Realtime-Kanal auf scores-Tabelle; setzt scores_updated=True bei Änderung."""
    key = f"rt_channel_{cid}"
    if key in st.session_state:
        return
    try:
        sb = _sb()

        def _handle(payload):
            st.session_state["scores_updated"] = True

        channel = sb.channel(f"scores_{cid}")
        channel.on_postgres_changes(
            event="*",
            schema="public",
            table="scores",
            callback=_handle,
        ).subscribe()
        st.session_state[key] = channel
    except Exception:
        pass  # Fallback: st_autorefresh läuft immer


# ── Hilfs-Filter ───────────────────────────────────────────────────────────────

def _matches(text, search):
    if not search:
        return True
    return search in str(text).lower()


def _ath_matches(ath, search):
    if not search:
        return True
    return any(
        _matches(ath.get(f, ""), search)
        for f in ["first_name", "last_name", "club", "team_abbr", "team_name"]
    )


def _team_matches(team, team_athletes, search):
    if not search:
        return True
    if _matches(team.get("name", ""), search):
        return True
    if _matches(team.get("abbreviation", ""), search):
        return True
    return any(_ath_matches(a, search) for a in team_athletes)


# ── Tab: Teams ─────────────────────────────────────────────────────────────────

def _calc_teams(teams, athletes, score_lookup, counting, score_mode="summe"):
    team_results = []
    for team in teams:
        start_app    = team.get("start_apparatus", 1)
        team_athletes = [a for a in athletes if a["team_id"] == team["id"]]
        app_data = {}

        for app_id in APP_IDS:
            scored = [
                a for a in team_athletes
                if _final(score_lookup.get((a["id"], app_id))) is not None
            ]
            scored.sort(
                key=lambda a: score_lookup[(a["id"], app_id)]["final_score"],
                reverse=True,
            )
            counting_ids = {id(a) for a in scored[:counting]}
            rows = [
                {
                    "ath":    a,
                    "score":  score_lookup.get((a["id"], app_id)),
                    "counts": id(a) in counting_ids,
                }
                for a in team_athletes
                if score_lookup.get((a["id"], app_id)) is not None
            ]
            vals = [r["score"]["final_score"] for r in rows if r["counts"] and r["score"]]
            if vals:
                team_total = (
                    round(sum(vals) / len(vals), 3)
                    if score_mode == "durchschnitt"
                    else round(sum(vals), 3)
                )
            else:
                team_total = None
            app_data[app_id] = {
                "rows":      rows,
                "team_total": team_total,
                "is_start":  app_id == start_app,
            }

        app_totals  = [d["team_total"] for d in app_data.values() if d["team_total"] is not None]
        grand_total = round(sum(app_totals), 3) if app_totals else None
        team_results.append({
            "team":        team,
            "app_data":    app_data,
            "grand_total": grand_total,
            "athletes":    team_athletes,
        })

    team_results.sort(
        key=lambda x: x["grand_total"] if x["grand_total"] is not None else -999,
        reverse=True,
    )
    rank = 1
    for i, tr in enumerate(team_results):
        if tr["grand_total"] is None:
            tr["rank"] = "–"
        elif (
            i > 0
            and tr["grand_total"] == team_results[i - 1]["grand_total"]
            and team_results[i - 1]["grand_total"] is not None
        ):
            tr["rank"] = team_results[i - 1]["rank"]
            rank += 1
        else:
            tr["rank"] = str(rank)
            rank += 1

    for app_id in APP_IDS:
        ranked_apps = sorted(
            [(tr, tr["app_data"][app_id]["team_total"]) for tr in team_results
             if tr["app_data"][app_id]["team_total"] is not None],
            key=lambda x: x[1],
            reverse=True,
        )
        for ri, (tr, _) in enumerate(ranked_apps):
            tr["app_data"][app_id]["apparatus_rank"] = ri + 1

    return team_results


def _show_team_ranking(teams, athletes, score_lookup, cfg, counting, search):
    score_mode   = cfg.get("team_score_mode", "summe")
    team_results = _calc_teams(teams, athletes, score_lookup, counting, score_mode)
    if not team_results:
        st.markdown("<div class='rl-wrap no-data'>Noch keine Daten.</div>",
                    unsafe_allow_html=True)
        return

    html  = "<div class='rl-wrap'>"
    shown = 0
    for tr in team_results:
        if not _team_matches(tr["team"], tr["athletes"], search):
            continue
        shown += 1
        team  = tr["team"]
        rank  = tr["rank"]
        grand = tr["grand_total"]
        rk_int   = int(rank) if str(rank).isdigit() else 0
        medal    = RANK_MEDAL.get(rk_int, "")
        rank_bg  = RANK_COLORS.get(rk_int, "#D6EAF3") if rk_int else "#f0f0f0"
        rank_col = "#fff" if 0 < rk_int <= 3 else "#0D4E73"

        html += "<div class='team-card'>"
        html += f"""
        <div class='team-header'>
          <div class='team-rank' style='background:{rank_bg};color:{rank_col};'>
            {medal if medal else rank}
          </div>
          <div class='team-name' style='flex:1'>
            <strong>{team['name']}</strong>
            <span>{team.get('abbreviation','')} · Abt. {team.get('abteilung',1)}</span>
          </div>
          <div class='team-total'>
            {f"{grand:.3f}" if grand is not None else "–"}
            <small>Gesamttotal</small>
          </div>
        </div>"""

        html += "<div class='app-chips'>"
        for app_id in APP_IDS:
            data  = tr["app_data"][app_id]
            t     = data.get("team_total")
            r_app = data.get("apparatus_rank", "")
            cls   = "app-chip" + (" start" if data["is_start"] else "") + ("" if t else " no-score")
            u     = "border-bottom:2px solid #2C7FA6;" if data["is_start"] else ""
            html += f"""
            <div class='{cls}'>
              <span class='app-name' style='{u}'>{APP_SHORT[app_id]}</span>
              <span class='app-val'>{f"{t:.3f}" if t is not None else "–"}</span>
              <span class='app-rank'>{f"#{r_app}" if r_app else ""}</span>
            </div>"""
        html += "</div>"

        athletes_map = {}
        for app_id, data in tr["app_data"].items():
            for row in data["rows"]:
                aid = row["ath"]["id"]
                if aid not in athletes_map:
                    athletes_map[aid] = {"ath": row["ath"], "scores": {}}
                athletes_map[aid]["scores"][app_id] = row

        sorted_aths = sorted(
            athletes_map.values(),
            key=lambda x: x["ath"].get("last_name", ""),
        )

        html += "<div class='turner-list'>"
        for entry in sorted_aths:
            ath  = entry["ath"]
            meta = " · ".join(filter(None, [
                str(ath.get("year_of_birth", "")),
                ath.get("category", ""),
                ath.get("club", ""),
            ]))
            chips = ""
            for app_id in APP_IDS:
                row = entry["scores"].get(app_id)
                if not row:
                    continue
                s = row.get("score")
                if s and _final(s) is not None:
                    val = _final(s)
                    if not row.get("counts"):
                        chips += f"<span class='score-chip struck'>{APP_SHORT[app_id]} {val:.3f}</span>"
                    else:
                        chips += f"<span class='score-chip'>{APP_SHORT[app_id]} {val:.3f}</span>"
            html += f"""
            <div class='turner-item'>
              <div class='turner-name'>{ath['first_name']} {ath['last_name']}</div>
              <div class='turner-meta'>{meta}</div>
              <div class='turner-scores'>{chips}</div>
            </div>"""
        html += "</div></div>"

    if shown == 0:
        html += "<div class='no-data'>Keine Resultate für diese Suche.</div>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


# ── Tab: Einzel ────────────────────────────────────────────────────────────────

def _show_individual(athletes, score_lookup, search):
    cat_filter = st.multiselect("Kategorie filtern", CATEGORIES, default=[], key="ind_cat")

    rows = []
    for ath in athletes:
        if cat_filter and ath.get("category") not in cat_filter:
            continue
        if not _ath_matches(ath, search):
            continue
        total, has_any = 0.0, False
        app_scores = {}
        for app_id in APP_IDS:
            s = score_lookup.get((ath["id"], app_id))
            if s and _final(s) is not None:
                app_scores[app_id] = _final(s)
                total += _final(s)
                has_any = True
            else:
                app_scores[app_id] = None
        rows.append({
            "ath":        ath,
            "app_scores": app_scores,
            "total":      round(total, 3) if has_any else None,
        })

    rows.sort(key=lambda x: x["total"] if x["total"] is not None else -999, reverse=True)
    rank = 1
    for i, r in enumerate(rows):
        if r["total"] is None:
            r["rank"] = "–"
        elif i > 0 and r["total"] == rows[i - 1]["total"]:
            r["rank"] = rows[i - 1]["rank"]
        else:
            r["rank"] = str(rank)
        rank += 1

    html = "<div class='rl-wrap'>"
    for r in rows:
        ath      = r["ath"]
        rk       = r["rank"]
        total    = r["total"]
        rk_int   = int(rk) if str(rk).isdigit() else 0
        rank_bg  = RANK_COLORS.get(rk_int, "#D6EAF3") if rk_int else "#f0f0f0"
        rank_col = "#fff" if 0 < rk_int <= 3 else "#0D4E73"
        medal    = RANK_MEDAL.get(rk_int, "")
        meta     = " · ".join(filter(None, [
            str(ath.get("year_of_birth", "")),
            ath.get("category", ""),
            ath.get("club", ""),
            ath.get("team_abbr", ""),
        ]))
        chips = ""
        for app_id in APP_IDS:
            s = score_lookup.get((ath["id"], app_id))
            if s and s.get("final_score") is not None:
                d   = s.get("d_score") or 0
                e   = s.get("e_wert") or 0
                pen = s.get("penalty") or 0
                bon = s.get("bonus") or 0
                fin = s["final_score"]
                detail = f"D:{d:.1f} E:{e:.3f}"
                if pen: detail += f" Pen:{pen:.3f}"
                if bon: detail += f" Bon:{bon:.3f}"
                chips += f"""
                <details style='margin-bottom:3px;'>
                  <summary style='list-style:none;cursor:pointer;display:flex;align-items:center;gap:6px;'>
                    <span class='score-chip' style='cursor:pointer;'>{APP_SHORT[app_id]} {fin:.3f} ▾</span>
                  </summary>
                  <div style='font-size:0.68rem;color:#15608A;padding:2px 4px;background:#D6EAF3;
                              border-radius:4px;margin-top:2px;'>{detail}</div>
                </details>"""

        html += f"""
        <div class='ind-card'>
          <div class='ind-header'>
            <div class='ind-rank' style='background:{rank_bg};color:{rank_col};'>
              {medal if medal else rk}
            </div>
            <div class='ind-name' style='flex:1'>
              <strong>{ath['first_name']} {ath['last_name']}</strong><br>
              <small>{meta}</small>
            </div>
            <div class='ind-total'>{f"{total:.3f}" if total is not None else "–"}</div>
          </div>
          <div class='ind-scores'>{chips}</div>
        </div>"""

    if not rows:
        html += "<div class='no-data'>Keine Turner für diese Auswahl.</div>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


# ── Tab: Gerät ─────────────────────────────────────────────────────────────────

def _show_per_apparatus(all_scores, search):
    app_options = {APP_NAMES[a]: a for a in APP_IDS}
    sel_name    = st.selectbox("Gerät auswählen", list(app_options.keys()), key="app_sel")
    app_id      = app_options[sel_name]
    cat_filter  = st.multiselect("Kategorie filtern", CATEGORIES, default=[], key="app_cat")

    scored = [s for s in all_scores if s["apparatus_id"] == app_id and _final(s) is not None]
    if cat_filter:
        scored = [s for s in scored if s.get("category") in cat_filter]
    if search:
        scored = [
            s for s in scored
            if any(_matches(s.get(f, ""), search)
                   for f in ["first_name", "last_name", "team_abbr", "team_name", "category"])
        ]

    if not scored:
        st.markdown("<div class='rl-wrap no-data'>Noch keine Noten für dieses Gerät.</div>",
                    unsafe_allow_html=True)
        return

    scored.sort(key=lambda x: _final(x), reverse=True)
    rank = 1
    for i, s in enumerate(scored):
        if i > 0 and _final(s) == _final(scored[i - 1]):
            s["rank"] = scored[i - 1]["rank"]
        else:
            s["rank"] = rank
        rank += 1

    html = f"<div class='rl-wrap'><div class='app-card'>"
    html += f"<div class='app-card-title'>{APP_NAMES[app_id]}</div>"
    for s in scored:
        rk     = s["rank"]
        rk_int = rk if isinstance(rk, int) else 0
        medal  = RANK_MEDAL.get(rk_int, "")
        meta   = " · ".join(filter(None, [s.get("category", ""), s.get("team_abbr", "")]))
        d      = s.get("d_score") or 0
        e      = s.get("e_wert") or 0
        pen    = s.get("penalty") or 0
        bon    = s.get("bonus") or 0
        detail = f"D:{d:.1f} E:{e:.3f}"
        if pen: detail += f" P:{pen:.1f}"
        if bon: detail += f" B:{bon:.1f}"
        html += f"""
        <div class='app-row'>
          <div class='app-row-rank'>{medal if medal else rk}</div>
          <div style='flex:1'>
            <div class='app-row-name'>{s.get('first_name','')} {s.get('last_name','')}</div>
            <div class='app-row-meta'>{meta} · <span style='color:#15608A;font-size:0.65rem;'>{detail}</span></div>
          </div>
          <div class='app-row-score'>{f"{_final(s):.3f}"}</div>
        </div>"""
    html += "</div></div>"
    st.markdown(html, unsafe_allow_html=True)


# ── Tab: Live ──────────────────────────────────────────────────────────────────

def _show_live(cid, num_e):
    st.markdown(
        "<div class='live-badge'><div class='live-dot'></div>LIVE</div>",
        unsafe_allow_html=True,
    )

    live = get_live_scores(cid, limit=10)
    _enrich_scores(live, num_e)

    scored = [s for s in live if _final(s) is not None and s.get("updated_at")]
    if not scored:
        st.markdown("<div class='rl-wrap no-data'>Noch keine Noten gespeichert.</div>",
                    unsafe_allow_html=True)
        return

    html = "<div class='rl-wrap'>"
    for i, s in enumerate(scored):
        ts_raw = s.get("updated_at", "")
        try:
            ts = pd.Timestamp(ts_raw).strftime("%H:%M")
        except Exception:
            ts = ts_raw[:16] if ts_raw else "–"

        cat   = s.get("category", "")
        team  = s.get("team_abbr", "")
        meta  = " · ".join(filter(None, [cat, team]))
        app_n = APP_SHORT.get(s.get("apparatus_id"), "?")
        fin   = _final(s)
        d     = s.get("d_score") or 0
        e     = s.get("e_wert") or 0
        pen   = s.get("penalty") or 0
        bon   = s.get("bonus") or 0

        detail_items = [("D", f"{d:.1f}"), ("E", f"{e:.3f}")]
        if pen: detail_items.append(("Pen", f"{pen:.1f}"))
        if bon: detail_items.append(("Bon", f"{bon:.1f}"))

        detail_chips = "".join(
            f"<span style='background:#D6EAF3;color:#2C7FA6;border-radius:4px;"
            f"padding:2px 6px;font-size:0.72rem;font-weight:500;'>{k}: {v}</span>"
            for k, v in detail_items
        )

        html += f"""
        <div class='ticker-card' style='flex-direction:column;align-items:stretch;gap:6px;'>
          <div style='display:flex;align-items:center;gap:12px;'>
            <div class='ticker-num'>{i+1}</div>
            <div class='ticker-body' style='flex:1;'>
              <strong>{s.get('first_name','')} {s.get('last_name','')}</strong>
              <small>{meta}</small>
            </div>
            <div class='ticker-score'>
              <span class='app'>{app_n}</span>
              <div class='note'>{f"{fin:.3f}"}</div>
              <span class='time'>{ts}</span>
            </div>
          </div>
          <div style='display:flex;gap:5px;flex-wrap:wrap;padding-left:38px;'>
            {detail_chips}
            <span style='background:#0D4E73;color:#fff;border-radius:4px;
                         padding:2px 6px;font-size:0.72rem;font-weight:700;'>
              End: {fin:.3f}
            </span>
          </div>
        </div>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Haupt-Script
# ══════════════════════════════════════════════════════════════════════════════

# Realtime-Flag prüfen und sofort rerun
if st.session_state.get("scores_updated"):
    st.session_state["scores_updated"] = False
    st.rerun()

# Wettkampf-Auswahl
comps = get_competitions()
if not comps:
    st.warning("⏳ Noch keine Wettkampfdaten verfügbar.")
    st.stop()

comp_opts = {
    f"{c['name']} – {c.get('location', '')} {c.get('date', '')}".strip(" –"): c["id"]
    for c in comps
}
selected_comp = st.selectbox(
    "Wettkampf", list(comp_opts.keys()), label_visibility="collapsed"
)
cid = comp_opts[selected_comp]

# Daten laden
cfg       = get_config(cid)
num_e     = int(cfg.get("num_e_scores", 3))
counting  = int(cfg.get("counting_scores", 5))
comp_mode = cfg.get("comp_mode", "team")

all_scores = get_scores(cid)
teams      = get_teams(cid)
athletes   = get_athletes(cid)

# Athleten mit Team-Info anreichern (für Suche und Anzeige)
_teams_by_id = {t["id"]: t for t in teams}
for _a in athletes:
    _t = _teams_by_id.get(_a.get("team_id"), {})
    _a["team_abbr"] = _t.get("abbreviation", "")
    _a["team_name"] = _t.get("name", "")

_enrich_scores(all_scores, num_e)
score_lookup = {(s["athlete_id"], s["apparatus_id"]): s for s in all_scores}

# CSS + Header
st.markdown(CSS, unsafe_allow_html=True)

event_name = cfg.get("event_name", "Wettkampf")
location   = cfg.get("event_location", "")
date       = cfg.get("event_date", "")
sep        = " · " if location and date else ""
st.markdown(f"""
<div class='rl-wrap'>
  <div class='rl-header'>
    <h1>{event_name}</h1>
    <p>{location}{sep}{date}</p>
  </div>
</div>""", unsafe_allow_html=True)

search = st.text_input(
    "🔍 Suchen (Name, Vorname, Verein, Team...)", "",
    placeholder="z.B. Muster, STV Rain, Aargau...",
    key="rl_search",
).strip().lower()

# Tab-Navigation
if comp_mode == "einzel":
    nav_items = [("🤸 Einzel", "Einzel"), ("📊 Gerät", "Gerät"), ("⚡ Live", "Live")]
else:
    nav_items = [("🏆 Teams", "Teams"), ("🤸 Einzel", "Einzel"),
                 ("📊 Gerät", "Gerät"), ("⚡ Live", "Live")]

if "rl_view" not in st.session_state:
    st.session_state.rl_view = "Einzel" if comp_mode == "einzel" else "Teams"

cols = st.columns(len(nav_items) + 1)
for i, (label, key) in enumerate(nav_items):
    if cols[i].button(
        label, use_container_width=True,
        type="primary" if st.session_state.rl_view == key else "secondary",
    ):
        st.session_state.rl_view = key
        st.rerun()
if cols[-1].button("🔄 Refresh", use_container_width=True):
    st.rerun()

view = st.session_state.rl_view

# Autorefresh + Realtime nur im Live-Tab
if view == "Live":
    _setup_realtime(cid)
    if HAS_AUTOREFRESH:
        st_autorefresh(interval=5000, key="live_autorefresh")

# View dispatchen
if view == "Teams" and comp_mode != "einzel":
    _show_team_ranking(teams, athletes, score_lookup, cfg, counting, search)
elif view == "Einzel":
    _show_individual(athletes, score_lookup, search)
elif view == "Gerät":
    _show_per_apparatus(all_scores, search)
elif view == "Live":
    _show_live(cid, num_e)

now = pd.Timestamp.now().strftime("%H:%M:%S")
st.markdown(f"<div class='stand'>Stand: {now}</div>", unsafe_allow_html=True)
