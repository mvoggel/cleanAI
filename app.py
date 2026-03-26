# app.py
# cleanAI — AI Efficiency & Carbon Insight Tool
# Streamlit dashboard entry point.
# All outputs are ESTIMATES.

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from data_generator import generate_dataset
from processing import compute_per_request, compute_aggregations
from insights import run_all_insights
from optimizer import run_all_scenarios
from meta_footprint import compute_meta_footprint

st.set_page_config(
    page_title="cleanAI",
    page_icon="🌿",
    layout="wide",
)

# ── Cache data so reruns are fast ──────────────────────────────────────────────
@st.cache_data
def load_data():
    raw = generate_dataset()
    df = compute_per_request(raw)
    return df

df = load_data()
agg = compute_aggregations(df)
insights = run_all_insights(df)
scenarios = run_all_scenarios(df)
meta = compute_meta_footprint()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.shields.io/badge/cleanAI-v1.0-brightgreen", use_container_width=False)
    st.markdown("## cleanAI")
    st.markdown("**AI Efficiency & Carbon Insight Tool**")
    st.markdown("---")
    st.markdown(f"**Dataset:** {agg['total_requests']:,} requests")
    st.markdown(f"**Period:** 90 days (simulated)")
    st.markdown("---")
    st.caption("All outputs are estimates. See assumptions.py for constants.")

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "🔍 Breakdown",
    "⚠️ Inefficiencies",
    "🔧 Optimization Scenarios",
    "🌱 Meta Footprint",
])

# ──────────────────────────────────────────────────────────────────────────────
# TAB 1 — Overview
# ──────────────────────────────────────────────────────────────────────────────
with tab1:
    st.title("cleanAI — AI Efficiency & Carbon Insight Tool")
    st.caption("All figures are estimates based on published energy benchmarks and simulated usage data.")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Requests", f"{agg['total_requests']:,}")
    col2.metric("Total Energy", f"{agg['total_energy_kWh']:.2f} kWh")
    col3.metric("Total Carbon (est.)", f"{agg['total_carbon_kg']:.2f} kg CO₂")
    col4.metric("Total Cost (est.)", f"${agg['total_cost_usd']:,.2f}")

    st.markdown("---")
    st.subheader("Energy Over Time")

    df_time = df.copy()
    df_time["date"] = df_time["timestamp"].dt.date
    daily = df_time.groupby("date")["energy_Wh"].sum().reset_index()
    daily.columns = ["date", "energy_Wh"]

    fig = px.area(
        daily, x="date", y="energy_Wh",
        labels={"date": "Date", "energy_Wh": "Energy (Wh)"},
        color_discrete_sequence=["#2ECC71"],
    )
    fig.update_layout(showlegend=False, margin=dict(t=10))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Summary Statistics")
    summary = pd.DataFrame({
        "Metric": [
            "Avg energy per request (Wh)",
            "Avg carbon per request (g CO₂)",
            "Avg cost per request (USD)",
            "Total energy (kWh)",
            "Total carbon (kg CO₂)",
            "Total estimated cost (USD)",
        ],
        "Value (estimate)": [
            f"{agg['avg_energy_Wh']:.4f}",
            f"{agg['avg_carbon_g']:.4f}",
            f"${agg['avg_cost_usd']:.5f}",
            f"{agg['total_energy_kWh']:.3f}",
            f"{agg['total_carbon_kg']:.3f}",
            f"${agg['total_cost_usd']:.2f}",
        ],
    })
    st.dataframe(summary, use_container_width=True, hide_index=True)

# ──────────────────────────────────────────────────────────────────────────────
# TAB 2 — Breakdown
# ──────────────────────────────────────────────────────────────────────────────
with tab2:
    st.title("Breakdown by Model, Region & Request Type")

    def breakdown_charts(group_df, group_col, label):
        st.subheader(f"By {label}")
        cols = st.columns(3)
        metrics = [
            ("energy_Wh", "Energy (Wh)", "#3498DB"),
            ("carbon_g", "Carbon (g CO₂)", "#E74C3C"),
            ("cost_usd", "Cost (USD)", "#F39C12"),
        ]
        for col, (field, title, color) in zip(cols, metrics):
            fig = px.bar(
                group_df.sort_values(field, ascending=False),
                x=group_col, y=field,
                labels={group_col: label, field: title},
                color_discrete_sequence=[color],
                title=title,
            )
            fig.update_layout(showlegend=False, margin=dict(t=30, b=10))
            col.plotly_chart(fig, use_container_width=True)

    breakdown_charts(agg["by_model"], "model", "Model")
    st.markdown("---")
    breakdown_charts(agg["by_region"], "region", "Region")
    st.markdown("---")
    breakdown_charts(agg["by_request_type"], "request_type", "Request Type")

# ──────────────────────────────────────────────────────────────────────────────
# TAB 3 — Inefficiencies
# ──────────────────────────────────────────────────────────────────────────────
with tab3:
    st.title("Inefficiency Detection")
    st.caption("Estimates based on simulated usage patterns and assumption constants.")

    # 8A Token Inefficiency
    ti = insights["token_inefficiency"]
    st.subheader("8A — Token Inefficiency")
    c1, c2, c3 = st.columns(3)
    c1.metric("Flagged Requests", f"{ti['count']:,}")
    c2.metric("% of All Requests", f"{ti['pct_requests']:.1f}%")
    c3.metric("% of Total Energy", f"{ti['pct_energy']:.1f}%")
    st.caption(f"Threshold: >{ti['threshold']:,.0f} tokens (2× median of {ti['median_tokens']:,.0f})")

    st.markdown("---")

    # 8B Model Overuse
    mo = insights["model_overuse"]
    st.subheader("8B — Model Overuse (Large Model, Small Task)")
    c1, c2, c3 = st.columns(3)
    c1.metric("Flagged Requests", f"{mo['count']:,}")
    c2.metric("% of All Requests", f"{mo['pct_requests']:.1f}%")
    c3.metric("Energy Waste (est.)", f"{mo['energy_waste_Wh']:.1f} Wh")
    st.metric("Cost Waste vs. small-model (est.)", f"${mo['cost_waste_usd']:.2f}")
    with st.expander("Sample flagged requests"):
        st.dataframe(
            mo["flagged_df"][["request_id","timestamp","model","total_tokens","energy_Wh","cost_usd"]]
            .head(20),
            use_container_width=True, hide_index=True
        )

    st.markdown("---")

    # 8C Repetition Waste
    rw = insights["repetition_waste"]
    st.subheader("8C — Repetition Waste (Caching Opportunity)")
    c1, c2, c3 = st.columns(3)
    c1.metric("Duplicate Requests (est.)", f"{rw['count']:,}")
    c2.metric("% of All Requests", f"{rw['pct_requests']:.1f}%")
    c3.metric("Energy Saveable (est.)", f"{rw['energy_saveable_Wh']:.1f} Wh")
    st.metric("Cost Saveable via Caching (est.)", f"${rw['cost_saveable_usd']:.2f}")

    st.markdown("---")

    # 8D Heavy Tail
    ht = insights["heavy_tail"]
    st.subheader("8D — Heavy Tail Analysis")
    c1, c2 = st.columns(2)
    c1.metric("Top 10% requests account for", f"{ht['pct_energy']:.1f}% of total energy")
    c2.metric("Heavy tail threshold", f"{ht['threshold_Wh']:.2f} Wh / request")

    fig = px.histogram(
        df, x="energy_Wh", nbins=80,
        labels={"energy_Wh": "Energy per request (Wh)", "count": "Requests"},
        color_discrete_sequence=["#9B59B6"],
        title="Energy Distribution — Heavy Tail Visible",
    )
    fig.add_vline(x=ht["threshold_Wh"], line_dash="dash", line_color="red",
                  annotation_text="Top 10% threshold")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # 8E Regional Shift
    rs = insights["regional_shift"]
    st.subheader("8E — Regional Shift Opportunity")
    c1, c2, c3 = st.columns(3)
    c1.metric("Asia Requests", f"{rs['asia_requests']:,}")
    c2.metric("Current Carbon (Asia, est.)", f"{rs['current_carbon_g']:.1f} g CO₂")
    c3.metric("Optimised Carbon (EU, est.)", f"{rs['optimized_carbon_g']:.1f} g CO₂")
    st.metric(
        "Potential Saving by Shifting Asia → EU (est.)",
        f"{rs['savings_g']:.1f} g CO₂  ({rs['savings_pct_of_total']:.1f}% of total)"
    )

# ──────────────────────────────────────────────────────────────────────────────
# TAB 4 — Optimization Scenarios
# ──────────────────────────────────────────────────────────────────────────────
with tab4:
    st.title("Optimization Scenarios — Before vs. After")
    st.caption("All savings are estimates. Scenarios are independent; do not add them.")

    def scenario_card(label, data, note=""):
        st.subheader(label)
        if note:
            st.caption(note)
        before = data["before"]
        after = data["after"]
        sav = data["savings"]

        comparison = pd.DataFrame({
            "Metric": ["Energy (Wh)", "Carbon (g CO₂)", "Cost (USD)"],
            "Before": [
                f"{before['energy_Wh']:.1f}",
                f"{before['carbon_g']:.1f}",
                f"${before['cost_usd']:.2f}",
            ],
            "After": [
                f"{after['energy_Wh']:.1f}",
                f"{after['carbon_g']:.1f}",
                f"${after['cost_usd']:.2f}",
            ],
            "Saved": [
                f"{sav['saved_energy_Wh']:.1f} ({sav['saved_energy_Wh_pct']:.1f}%)",
                f"{sav['saved_carbon_g']:.1f} ({sav['saved_carbon_g_pct']:.1f}%)",
                f"${sav['saved_cost_usd']:.2f} ({sav['saved_cost_usd_pct']:.1f}%)",
            ],
        })
        st.dataframe(comparison, use_container_width=True, hide_index=True)

    sc = scenarios
    scenario_card(
        "Scenario 1 — Model Downgrade (30% of GPT-4 → small-model)",
        sc["model_downgrade"],
        f"Affects {sc['model_downgrade']['n_affected']:,} requests.",
    )
    st.markdown("---")
    scenario_card(
        "Scenario 2 — Token Reduction (25% prompt optimisation)",
        sc["token_reduction"],
        "Applies across all requests.",
    )
    st.markdown("---")
    scenario_card(
        "Scenario 3 — Caching (remove all duplicate requests)",
        sc["caching"],
        f"{sc['caching']['dupes_removed']:,} duplicate requests removed.",
    )

    st.markdown("---")
    st.subheader("Comparison Chart — % Energy Saved per Scenario")
    chart_data = pd.DataFrame({
        "Scenario": ["Model Downgrade", "Token Reduction", "Caching"],
        "Energy Saved (%)": [
            sc["model_downgrade"]["savings"]["saved_energy_Wh_pct"],
            sc["token_reduction"]["savings"]["saved_energy_Wh_pct"],
            sc["caching"]["savings"]["saved_energy_Wh_pct"],
        ],
        "Carbon Saved (%)": [
            sc["model_downgrade"]["savings"]["saved_carbon_g_pct"],
            sc["token_reduction"]["savings"]["saved_carbon_g_pct"],
            sc["caching"]["savings"]["saved_carbon_g_pct"],
        ],
        "Cost Saved (%)": [
            sc["model_downgrade"]["savings"]["saved_cost_usd_pct"],
            sc["token_reduction"]["savings"]["saved_cost_usd_pct"],
            sc["caching"]["savings"]["saved_cost_usd_pct"],
        ],
    })
    fig = px.bar(
        chart_data.melt(id_vars="Scenario", var_name="Metric", value_name="% Saved"),
        x="Scenario", y="% Saved", color="Metric", barmode="group",
        color_discrete_map={
            "Energy Saved (%)": "#3498DB",
            "Carbon Saved (%)": "#2ECC71",
            "Cost Saved (%)": "#F39C12",
        },
    )
    fig.update_layout(margin=dict(t=10))
    st.plotly_chart(fig, use_container_width=True)

# ──────────────────────────────────────────────────────────────────────────────
# TAB 5 — Meta Footprint
# ──────────────────────────────────────────────────────────────────────────────
with tab5:
    st.title("Meta Footprint — Carbon Cost of Building cleanAI")
    st.caption(
        "This module estimates the carbon emitted during the development of this tool itself. "
        "Transparency about our own footprint is part of the integrity of cleanAI."
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Dev AI Interactions", f"{meta['interactions']}")
    c2.metric("Total Energy Used (est.)", f"{meta['total_energy_Wh']:.0f} Wh  ({meta['total_energy_kWh']:.3f} kWh)")
    c3.metric("Total Carbon Emitted (est.)", f"{meta['total_carbon_g']:.1f} g CO₂  ({meta['total_carbon_kg']:.3f} kg)")

    st.markdown("---")
    st.subheader("Context")
    c1, c2 = st.columns(2)
    c1.metric("Equivalent driving distance (est.)", f"{meta['km_driven_equiv']:.1f} km")
    c2.metric("Equivalent smartphone charges (est.)", f"{meta['phone_charges_equiv']:.0f} charges")

    st.markdown("---")
    st.subheader("Methodology")
    st.markdown(f"""
| Assumption | Value |
|---|---|
| Energy per AI interaction | {meta['energy_per_interaction_Wh']} Wh (midpoint of 2–10 Wh range) |
| Development interactions | {meta['interactions']} (midpoint of 100–300 range) |
| Build region | {meta['build_region']} |
| Carbon intensity | {meta['carbon_intensity_gCO2_kWh']} gCO₂/kWh |

All values are estimates. See `assumptions.py` for all constants.
    """)
