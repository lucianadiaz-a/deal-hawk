from __future__ import annotations

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import streamlit as st

from backend.db import db_conn, init_schema
from backend.services.alerts import evaluate_alerts
from backend.services.ingest import run_ingest_cycle
from backend.services.pricing import get_listing_price_summary, list_price_summaries
from backend.services.seed import reset_db, seed_from_json


def _fmt_money(cents: int | None) -> str:
    if cents is None:
        return "—"
    return f"${cents/100:.2f}"


def _fmt_pct(p: float | None) -> str:
    if p is None:
        return "—"
    return f"{p:.1f}%"


st.set_page_config(page_title="Deal Hawk — Baseline POC", layout="wide")
st.title("Deal Hawk — Baseline POC")

with st.sidebar:
    st.header("Controls")
    window_hours = st.number_input("Delta window (hours)", min_value=1, max_value=72, value=6, step=1)
    threshold_pct = st.number_input("Alert threshold (% drop)", min_value=1.0, max_value=90.0, value=10.0, step=1.0)
    st.divider()

    if st.button("Run ingest cycle", use_container_width=True):
        with db_conn() as conn:
            init_schema(conn)
            res = run_ingest_cycle(conn)
        st.success(f"Ingest complete. Snapshots written: {res.snapshots_written}")

    if st.button("Evaluate alerts", use_container_width=True):
        with db_conn() as conn:
            init_schema(conn)
            res = evaluate_alerts(conn, window_hours=int(window_hours), threshold_pct=float(threshold_pct))
        st.success(f"Evaluated {res.evaluated} listings. Triggered {res.triggered} alerts.")

    st.divider()
    st.header("Data")

    if st.button("Seed DB (idempotent)", use_container_width=True):
        with db_conn() as conn:
            init_schema(conn)
            seed_result = seed_from_json(conn, Path("data/seed_listings.json"))
        st.success(
            f"Seeded: {seed_result.products} products, "
            f"{seed_result.retailers} retailers, {seed_result.listings} listings."
        )

    reset_confirmed = st.checkbox("I understand this deletes demo data")
    if st.button("Reset DB (danger)", use_container_width=True, disabled=not reset_confirmed):
        with db_conn() as conn:
            reset_db(conn)
        st.success("Database reset complete. All data deleted.")

    if st.button("Bootstrap demo data", use_container_width=True):
        with db_conn() as conn:
            init_schema(conn)
            reset_db(conn)
            seed_result = seed_from_json(conn, Path("data/seed_listings.json"))
            
            # Run ingest cycle 3 times
            total_snapshots = 0
            for _ in range(3):
                res = run_ingest_cycle(conn)
                total_snapshots += res.snapshots_written
            
            # Evaluate alerts once
            alert_res = evaluate_alerts(conn, window_hours=int(window_hours), threshold_pct=float(threshold_pct))
        
        st.success(
            f"Bootstrap complete! "
            f"{seed_result.listings} listings, "
            f"{total_snapshots} snapshots, "
            f"{alert_res.triggered} alerts."
        )


tab_overview, tab_listing, tab_alerts = st.tabs(["Overview", "Listing detail", "Alert log"])

with tab_overview:
    with db_conn() as conn:
        init_schema(conn)
        summaries = list_price_summaries(conn, window_hours=int(window_hours), active_only=True)

    if not summaries:
        st.warning("⚠️ No listings found. Click **Bootstrap demo data** in the sidebar to get started.")
    else:
        rows = []
        for s in summaries:
            rows.append(
                {
                    "listing_id": s.listing_id,
                    "product": s.product_name,
                    "retailer": s.retailer_name,
                    "current": _fmt_money(s.current_price_cents),
                    "window_start": _fmt_money(s.window_start_price_cents),
                    "delta": _fmt_money(s.delta_cents),
                    "delta_pct": _fmt_pct(s.delta_pct),
                    "last_updated": s.current_captured_at or "—",
                }
            )

        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

with tab_listing:
    with db_conn() as conn:
        init_schema(conn)
        ids = conn.execute(
            """
            SELECT l.id AS listing_id, p.name AS product, r.name AS retailer
            FROM listings l
            JOIN products p ON p.id = l.product_id
            JOIN retailers r ON r.id = l.retailer_id
            WHERE l.active = 1
            ORDER BY l.id
            """
        ).fetchall()

    options = {f"{int(r['listing_id'])} — {r['product']} @ {r['retailer']}": int(r["listing_id"]) for r in ids}
    if not options:
        st.warning("⚠️ No listings found. Click **Bootstrap demo data** in the sidebar to get started.")
    else:
        label = st.selectbox("Select listing", list(options.keys()))
        listing_id = options[label]

        with db_conn() as conn:
            init_schema(conn)
            s = get_listing_price_summary(conn, listing_id, window_hours=int(window_hours))
            snaps = conn.execute(
                """
                SELECT price_cents, currency, captured_at
                FROM price_snapshots
                WHERE listing_id = ?
                ORDER BY captured_at DESC, id DESC
                LIMIT 200
                """,
                (listing_id,),
            ).fetchall()

            events = conn.execute(
                """
                SELECT rule_name, threshold_pct, prev_price_cents, new_price_cents, triggered_at, message_preview
                FROM alert_events
                WHERE listing_id = ?
                ORDER BY triggered_at DESC, id DESC
                LIMIT 50
                """,
                (listing_id,),
            ).fetchall()

        st.subheader(f"{s.product_name} @ {s.retailer_name}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Current", _fmt_money(s.current_price_cents))
        c2.metric(f"Delta (last {int(window_hours)}h)", _fmt_money(s.delta_cents))
        c3.metric("Delta %", _fmt_pct(s.delta_pct))

        st.markdown("### Price snapshots")
        snap_rows = [{"captured_at": r["captured_at"], "price": _fmt_money(int(r["price_cents"]))} for r in snaps]
        st.dataframe(pd.DataFrame(snap_rows), use_container_width=True, hide_index=True)

        st.markdown("### Alert events")
        if not events:
            st.caption("No alerts yet for this listing.")
        else:
            ev_rows = []
            for e in events:
                ev_rows.append(
                    {
                        "triggered_at": e["triggered_at"],
                        "rule": e["rule_name"],
                        "threshold": f"{float(e['threshold_pct']):.1f}%",
                        "from": _fmt_money(int(e["prev_price_cents"])),
                        "to": _fmt_money(int(e["new_price_cents"])),
                        "preview": e["message_preview"],
                    }
                )
            st.dataframe(pd.DataFrame(ev_rows), use_container_width=True, hide_index=True)

with tab_alerts:
    with db_conn() as conn:
        init_schema(conn)
        rows = conn.execute(
            """
            SELECT
                ae.triggered_at,
                p.name AS product,
                r.name AS retailer,
                ae.rule_name,
                ae.threshold_pct,
                ae.prev_price_cents,
                ae.new_price_cents,
                ae.message_preview
            FROM alert_events ae
            JOIN listings l ON l.id = ae.listing_id
            JOIN products p ON p.id = l.product_id
            JOIN retailers r ON r.id = l.retailer_id
            ORDER BY ae.triggered_at DESC, ae.id DESC
            LIMIT 200
            """
        ).fetchall()

    if not rows:
        st.info("No alerts yet. Run ingest a few times, then click “Evaluate alerts”.")
    else:
        out = []
        for r in rows:
            out.append(
                {
                    "triggered_at": r["triggered_at"],
                    "product": r["product"],
                    "retailer": r["retailer"],
                    "rule": r["rule_name"],
                    "threshold": f"{float(r['threshold_pct']):.1f}%",
                    "from": _fmt_money(int(r["prev_price_cents"])),
                    "to": _fmt_money(int(r["new_price_cents"])),
                    "preview": r["message_preview"],
                }
            )
        st.dataframe(pd.DataFrame(out), use_container_width=True, hide_index=True)
