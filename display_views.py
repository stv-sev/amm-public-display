"""
display_views.py – Rankingansichten für Public Display
"""
import streamlit as st
import pandas as pd

APP_IDS   = [1, 2, 3, 4, 5, 6]
APP_NAMES = {1:"Boden", 2:"Pferd", 3:"Ringe", 4:"Sprung", 5:"Barren", 6:"Reck"}
APP_SHORT = {1:"Bo",    2:"Pf",    3:"Ri",    4:"Sp",     5:"Ba",    6:"Re"}
MEDAL     = {1:"🥇", 2:"🥈", 3:"🥉"}


# ── Gesamtrangliste ───────────────────────────────────────────────────────────

def show_gesamtrangliste(data):
    athletes     = data["athletes"]
    score_lookup = data["score_lookup"]
    ath_totals   = data["ath_totals"]

    ranked = sorted(
        [a for a in athletes if ath_totals.get(a["id"], 0) > 0],
        key=lambda a: -ath_totals[a["id"]]
    )
    if not ranked:
        st.info("⏳ Noch keine Noten.")
        return

    rows = []
    for rank, a in enumerate(ranked, 1):
        aid = a["id"]
        sc  = score_lookup.get(aid, {})
        row = {
            "Rg":    MEDAL.get(rank, f"{rank}."),
            "Name":  f"{a['last_name']} {a['first_name']}",
            "Jg":    str(a.get("year_of_birth", "")),
        }
        for app in APP_IDS:
            v = sc.get(app, {}).get("final")
            row[APP_SHORT[app]] = f"{v:.3f}" if v else "–"
        row["Total"] = f"{ath_totals[aid]:.3f}"
        rows.append(row)

    df = pd.DataFrame(rows)
    st.dataframe(
        df, hide_index=True, use_container_width=True,
        column_config={
            "Rg":    st.column_config.TextColumn(width="small"),
            "Name":  st.column_config.TextColumn(width="medium"),
            "Jg":    st.column_config.TextColumn(width="small"),
            "Total": st.column_config.TextColumn(width="small"),
            **{APP_SHORT[app]: st.column_config.TextColumn(width="small")
               for app in APP_IDS}
        }
    )


# ── Gerät-Rangliste ───────────────────────────────────────────────────────────

def show_geraet(data):
    ath_map      = data["ath_map"]
    score_lookup = data["score_lookup"]

    # Tabs per apparatus
    tabs = st.tabs([APP_NAMES[app] for app in APP_IDS])
    for tab, app_id in zip(tabs, APP_IDS):
        with tab:
            entries = []
            for aid, apps in score_lookup.items():
                sc = apps.get(app_id, {})
                if sc.get("final") is None:
                    continue
                a = ath_map.get(aid, {})
                entries.append({
                    "final": sc["final"],
                    "d": sc["d"], "e": sc["e"], "p": sc["p"], "b": sc["b"],
                    "name": f"{a.get('last_name','')} {a.get('first_name','')}",
                    "jg":   str(a.get("year_of_birth", "")),
                })
            entries.sort(key=lambda x: -x["final"])

            if not entries:
                st.info("⏳ Noch keine Noten.")
                continue

            rows = []
            for rank, e in enumerate(entries, 1):
                rows.append({
                    "Rg":      MEDAL.get(rank, f"{rank}."),
                    "Name":    e["name"],
                    "Jg":      e["jg"],
                    "D":       f"{e['d']:.1f}",
                    "E":       f"{e['e']:.2f}",
                    "P":       f"{e['p']:.1f}" if e["p"] else "",
                    "B":       f"{e['b']:.1f}" if e["b"] else "",
                    "Endnote": f"{e['final']:.3f}",
                })

            st.dataframe(
                pd.DataFrame(rows), hide_index=True, use_container_width=True,
                column_config={
                    "Rg":      st.column_config.TextColumn(width="small"),
                    "Name":    st.column_config.TextColumn(width="medium"),
                    "Jg":      st.column_config.TextColumn(width="small"),
                    "D":       st.column_config.TextColumn(width="small"),
                    "E":       st.column_config.TextColumn(width="small"),
                    "P":       st.column_config.TextColumn(width="small"),
                    "B":       st.column_config.TextColumn(width="small"),
                    "Endnote": st.column_config.TextColumn(width="small"),
                }
            )


# ── Team-Rangliste ────────────────────────────────────────────────────────────

def show_team(data):
    athletes     = data["athletes"]
    teams        = data["teams"]
    score_lookup = data["score_lookup"]
    ath_totals   = data["ath_totals"]
    cfg          = data["cfg"]

    counting  = int(cfg.get("counting_scores", 5))
    max_st    = int(cfg.get("max_starters", 8))

    if not teams:
        st.info("Keine Teams erfasst.")
        return

    team_results = []
    for t in teams:
        t_aths     = [a for a in athletes if a.get("team_id") == t["id"]]
        app_totals = {}
        for app in APP_IDS:
            entries = sorted(
                [(a, score_lookup.get(a["id"],{}).get(app,{}).get("final"))
                 for a in t_aths
                 if score_lookup.get(a["id"],{}).get(app,{}).get("final") is not None],
                key=lambda x: -x[1]
            )
            zaehlend  = entries[:max_st][:counting]
            app_totals[app] = round(sum(e[1] for e in zaehlend), 3)
        team_results.append({
            "team":       t,
            "t_aths":     t_aths,
            "total":      round(sum(app_totals.values()), 3),
            "app_totals": app_totals,
        })
    team_results.sort(key=lambda x: -x["total"])

    # Team overview table
    rows = []
    for rank, tr in enumerate(team_results, 1):
        row = {
            "Rg":    MEDAL.get(rank, f"{rank}."),
            "Team":  tr["team"]["name"],
            "Total": f"{tr['total']:.3f}",
        }
        for app in APP_IDS:
            v = tr["app_totals"].get(app, 0)
            row[APP_SHORT[app]] = f"{v:.3f}" if v else "–"
        rows.append(row)

    st.dataframe(
        pd.DataFrame(rows), hide_index=True, use_container_width=True,
        column_config={
            "Rg":    st.column_config.TextColumn(width="small"),
            "Team":  st.column_config.TextColumn(width="medium"),
            "Total": st.column_config.TextColumn(width="small"),
            **{APP_SHORT[app]: st.column_config.TextColumn(width="small")
               for app in APP_IDS}
        }
    )

    # Team detail expanders
    st.markdown("---")
    for rank, tr in enumerate(team_results, 1):
        medal = MEDAL.get(rank, f"{rank}.")
        with st.expander(f"{medal} **{tr['team']['name']}** — {tr['total']:.3f}",
                         expanded=(rank == 1)):
            rows = []
            for a in sorted(tr["t_aths"], key=lambda x: -ath_totals.get(x["id"], 0)):
                aid = a["id"]
                sc  = score_lookup.get(aid, {})
                row = {
                    "Name":  f"{a['last_name']} {a['first_name']}",
                    "Jg":    str(a.get("year_of_birth", "")),
                    "Total": f"{ath_totals.get(aid, 0):.3f}",
                }
                for app in APP_IDS:
                    v = sc.get(app, {}).get("final")
                    row[APP_SHORT[app]] = f"{v:.3f}" if v else "–"
                rows.append(row)
            st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
