# app.py
# cleanAI — AI Efficiency & Carbon Insight Tool
# Streamlit dashboard entry point — v2.0
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

# ── Mobile-responsive CSS + headline card styles ──────────────────────────────
st.markdown("""
<style>
/* ── Mobile responsive layout ───────────────────────────────────────────── */
@media screen and (max-width: 768px) {
    /* Stack columns vertically */
    div[data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        min-width: calc(100% - 1rem) !important;
        flex: 1 1 100% !important;
    }
    /* Scale headings for mobile */
    h1 { font-size: 1.5rem !important; line-height: 1.2 !important; }
    h2 { font-size: 1.2rem !important; }
    h3 { font-size: 1.1rem !important; }
    /* Bigger metric values for screenshot readability */
    [data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
    }
    /* Tabs: shrink labels so they fit */
    button[data-baseweb="tab"] {
        font-size: 0.68rem !important;
        padding: 0.3rem 0.35rem !important;
    }
    /* Reduce side padding on mobile */
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
}

/* ── Headline callout cards ─────────────────────────────────────────────── */
.callout-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 0.75rem;
    margin-bottom: 1.25rem;
}
.callout-card {
    border-radius: 10px;
    padding: 1rem 1.25rem;
    line-height: 1.35;
}
.callout-card.green {
    background: rgba(46, 204, 113, 0.10);
    border-left: 5px solid #2ECC71;
}
.callout-card.red {
    background: rgba(231, 76, 60, 0.10);
    border-left: 5px solid #E74C3C;
}
.callout-card.blue {
    background: rgba(52, 152, 219, 0.10);
    border-left: 5px solid #3498DB;
}
.callout-card.amber {
    background: rgba(243, 156, 18, 0.10);
    border-left: 5px solid #F39C12;
}
.callout-stat {
    display: block;
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    margin-bottom: 0.2rem;
}
.callout-card.green  .callout-stat { color: #27AE60; }
.callout-card.red    .callout-stat { color: #C0392B; }
.callout-card.blue   .callout-stat { color: #2980B9; }
.callout-card.amber  .callout-stat { color: #D68910; }
.callout-label {
    font-size: 0.92rem;
    line-height: 1.4;
}

/* ── Section divider ────────────────────────────────────────────────────── */
.section-divider {
    border: none;
    border-top: 1px solid rgba(128,128,128,0.2);
    margin: 1.25rem 0;
}
</style>
""", unsafe_allow_html=True)

# ── Cache data so reruns are fast ─────────────────────────────────────────────
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

# ── Pre-compute headline stats (used in Tab 1) ────────────────────────────────
_by_region = agg["by_region"].set_index("region")
_us_carbon_g  = _by_region.loc["us-east", "carbon_g"] + _by_region.loc["us-west", "carbon_g"]
_eu_carbon_g  = _by_region.loc["eu",      "carbon_g"]
_asia_carbon_g = _by_region.loc["asia",   "carbon_g"]
_us_vs_eu_ratio   = _us_carbon_g  / _eu_carbon_g
_asia_vs_eu_ratio = _asia_carbon_g / _eu_carbon_g

_heavy_tail_pct     = insights["heavy_tail"]["pct_energy"]
_cache_pct          = insights["repetition_waste"]["pct_requests"]
_cache_cost_savings = insights["repetition_waste"]["cost_saveable_usd"]
_overuse_cost_waste = insights["model_overuse"]["cost_waste_usd"]
_overuse_count      = insights["model_overuse"]["count"]

_model_downgrade_cost_pct = scenarios["model_downgrade"]["savings"]["saved_cost_usd_pct"]
_token_reduction_energy_pct = scenarios["token_reduction"]["savings"]["saved_energy_Wh_pct"]

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌿 cleanAI")
    st.markdown("**AI Efficiency & Carbon Insight Tool**")
    st.caption("v2.0")
    st.markdown("---")
    st.markdown(f"📦 **Dataset:** {agg['total_requests']:,} requests")
    st.markdown(f"📅 **Period:** 90 days (simulated)")
    st.markdown(f"⚡ **Total energy:** {agg['total_energy_kWh']:.2f} kWh")
    st.markdown(f"🌍 **Total carbon:** {agg['total_carbon_kg']:.2f} kg CO₂")
    st.markdown("---")
    st.caption(
        "All outputs are **estimates** based on published energy benchmarks "
        "and modelled AI usage patterns. See `assumptions.py` for all constants."
    )

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "🔍 Breakdown",
    "⚠️ Inefficiencies",
    "🔧 Scenarios",
    "🌱 Meta Footprint",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — Overview
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    st.title("🌿 cleanAI — AI Carbon & Efficiency Tracker")
    st.caption(
        "Modelled from 7,500 simulated AI requests across 90 days, "
        "using published energy benchmarks (see assumptions.py). All figures are estimates."
    )

    # ── Headline callout cards ────────────────────────────────────────────────
    st.markdown("### 📣 Key Findings at a Glance")

    st.markdown(f"""
<div class="callout-grid">

  <div class="callout-card red">
    <span class="callout-stat">{_us_vs_eu_ratio:.1f}×</span>
    <span class="callout-label">more AI carbon emitted in the US than the EU —
    server location is one of the biggest levers companies aren't pulling.</span>
  </div>

  <div class="callout-card amber">
    <span class="callout-stat">{_heavy_tail_pct:.0f}%</span>
    <span class="callout-label">of all AI energy is consumed by just the top 10% of requests.
    A small number of heavy, expensive calls drive most of the footprint.</span>
  </div>

  <div class="callout-card blue">
    <span class="callout-stat">{_cache_pct:.0f}%</span>
    <span class="callout-label">of requests are near-duplicates. A simple caching layer
    could eliminate <strong>${_cache_cost_savings:.2f}</strong> in unnecessary AI spend — for free.</span>
  </div>

  <div class="callout-card green">
    <span class="callout-stat">{_model_downgrade_cost_pct:.0f}%</span>
    <span class="callout-label">cost reduction achievable by routing just 30% of large-model calls
    to a smaller model — with no loss in output quality for simple tasks.</span>
  </div>

</div>
""", unsafe_allow_html=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # ── KPI cards ─────────────────────────────────────────────────────────────
    st.markdown("### 📊 Dataset Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Requests",      f"{agg['total_requests']:,}")
    col2.metric("Total Energy",        f"{agg['total_energy_kWh']:.2f} kWh")
    col3.metric("Total Carbon (est.)", f"{agg['total_carbon_kg']:.2f} kg CO₂")
    col4.metric("Total Cost (est.)",   f"${agg['total_cost_usd']:,.2f}")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # ── Energy over time ──────────────────────────────────────────────────────
    st.subheader("⚡ Energy Over Time")

    df_time = df.copy()
    df_time["date"] = df_time["timestamp"].dt.date
    daily = df_time.groupby("date")["energy_Wh"].sum().reset_index()
    daily.columns = ["date", "energy_Wh"]

    fig = px.area(
        daily, x="date", y="energy_Wh",
        labels={"date": "Date", "energy_Wh": "Energy (Wh)"},
        color_discrete_sequence=["#2ECC71"],
    )
    fig.update_layout(showlegend=False, margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

    # ── Summary stats ─────────────────────────────────────────────────────────
    st.subheader("📋 Per-Request Summary")
    summary = pd.DataFrame({
        "Metric": [
            "Avg energy per request",
            "Avg carbon per request",
            "Avg cost per request",
            "Total energy",
            "Total carbon",
            "Total estimated cost",
        ],
        "Value (estimate)": [
            f"{agg['avg_energy_Wh']:.4f} Wh",
            f"{agg['avg_carbon_g']:.4f} g CO₂",
            f"${agg['avg_cost_usd']:.5f}",
            f"{agg['total_energy_kWh']:.3f} kWh",
            f"{agg['total_carbon_kg']:.3f} kg CO₂",
            f"${agg['total_cost_usd']:.2f}",
        ],
    })
    st.dataframe(summary, use_container_width=True, hide_index=True)

    st.caption(
        "💡 *What is a 'request'?* Every time you send a message to an AI — ask a question, "
        "run a classification, trigger an agent — that's one request. Some are quick and cheap; "
        "others (like long conversations or complex agent chains) can use 50–100× more energy."
    )

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — Breakdown
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.title("🔍 Breakdown by Model, Region & Request Type")

    def breakdown_charts(group_df, group_col, label):
        st.subheader(f"By {label}")
        metrics = [
            ("energy_Wh", "Energy (Wh)",  "#3498DB"),
            ("carbon_g",  "Carbon (g CO₂)", "#E74C3C"),
            ("cost_usd",  "Cost (USD)",    "#F39C12"),
        ]
        # Render each chart — CSS stacks them on mobile, 3-col on desktop
        cols = st.columns(3)
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

    breakdown_charts(agg["by_model"],        "model",        "Model")
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # Regional context note
    breakdown_charts(agg["by_region"],       "region",       "Region")
    st.caption(
        "🌍 *Why does region matter?* The carbon intensity of electricity varies massively by country. "
        "The same AI computation run in the EU emits ~38% less CO₂ than in the US, "
        "and ~50% less than in Asia — purely because of the energy mix powering the data centres."
    )
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    breakdown_charts(agg["by_request_type"], "request_type", "Request Type")
    st.caption(
        "💡 *What are these request types?* **Chat** = conversational messages. "
        "**Classification** = quick yes/no or category decisions. "
        "**Embedding** = converting text into numbers for search/similarity. "
        "**Agent-loop** = AI calling tools or itself repeatedly — by far the heaviest."
    )

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — Inefficiencies
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.title("⚠️ Inefficiency Detection")
    st.caption("Estimates based on simulated usage patterns and assumption constants.")

    # 8A — Token Inefficiency
    ti = insights["token_inefficiency"]
    st.subheader("8A — Token Inefficiency")
    c1, c2, c3 = st.columns(3)
    c1.metric("Flagged Requests",    f"{ti['count']:,}")
    c2.metric("% of All Requests",   f"{ti['pct_requests']:.1f}%")
    c3.metric("% of Total Energy",   f"{ti['pct_energy']:.1f}%")
    st.caption(
        f"Threshold: >{ti['threshold']:,.0f} tokens (2× median of {ti['median_tokens']:,.0f}). "
        "These requests are likely bloated with unnecessary context or system prompt repetition."
    )

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # 8B — Model Overuse
    mo = insights["model_overuse"]
    st.subheader("8B — Model Overuse (Large Model, Tiny Task)")
    c1, c2, c3 = st.columns(3)
    c1.metric("Flagged Requests",     f"{mo['count']:,}")
    c2.metric("% of All Requests",    f"{mo['pct_requests']:.1f}%")
    c3.metric("Energy Waste (est.)",  f"{mo['energy_waste_Wh']:.1f} Wh")
    st.metric("Cost Waste vs. small-model (est.)", f"${mo['cost_waste_usd']:.2f}")
    st.caption(
        f"These {mo['count']:,} requests used GPT-4 or Claude for tasks under 500 tokens — "
        "a small, fast model would have done the same job at a fraction of the cost and carbon."
    )
    with st.expander("Sample flagged requests"):
        st.dataframe(
            mo["flagged_df"][["request_id","timestamp","model","total_tokens","energy_Wh","cost_usd"]]
            .head(20),
            use_container_width=True, hide_index=True
        )

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # 8C — Repetition Waste
    rw = insights["repetition_waste"]
    st.subheader("8C — Repetition Waste (Caching Opportunity)")
    c1, c2, c3 = st.columns(3)
    c1.metric("Duplicate Requests (est.)",  f"{rw['count']:,}")
    c2.metric("% of All Requests",          f"{rw['pct_requests']:.1f}%")
    c3.metric("Energy Saveable (est.)",     f"{rw['energy_saveable_Wh']:.1f} Wh")
    st.metric("Cost Saveable via Caching (est.)", f"${rw['cost_saveable_usd']:.2f}")
    st.caption(
        "Near-duplicate requests sent within a 1-hour window to the same model for the same task type. "
        "A response cache would serve these instantly — zero compute, zero carbon, zero cost."
    )

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # 8D — Heavy Tail
    ht = insights["heavy_tail"]
    st.subheader("8D — Heavy Tail Analysis")
    c1, c2 = st.columns(2)
    c1.metric("Top 10% of requests consume",  f"{ht['pct_energy']:.1f}% of total energy")
    c2.metric("Heavy tail threshold",          f"{ht['threshold_Wh']:.2f} Wh / request")

    fig = px.histogram(
        df, x="energy_Wh", nbins=80,
        labels={"energy_Wh": "Energy per request (Wh)", "count": "Requests"},
        color_discrete_sequence=["#9B59B6"],
        title="Energy Distribution — Heavy Tail Visible",
    )
    fig.add_vline(
        x=ht["threshold_Wh"], line_dash="dash", line_color="red",
        annotation_text="Top 10% threshold"
    )
    fig.update_layout(margin=dict(t=30, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "💡 *What does 'heavy tail' mean?* Most requests are small and cheap. But a long tail of "
        "large requests — long conversations, complex agent chains, chunky documents — use "
        f"disproportionate energy. Just {ht['pct_energy']:.0f}% of energy comes from 10% of calls."
    )

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # 8E — Regional Shift
    rs = insights["regional_shift"]
    st.subheader("8E — Regional Shift Opportunity")
    c1, c2, c3 = st.columns(3)
    c1.metric("Asia Requests",               f"{rs['asia_requests']:,}")
    c2.metric("Current Carbon (Asia, est.)", f"{rs['current_carbon_g']:.1f} g CO₂")
    c3.metric("Optimised Carbon (EU, est.)", f"{rs['optimized_carbon_g']:.1f} g CO₂")
    st.metric(
        "Potential Saving: Asia → EU (est.)",
        f"{rs['savings_g']:.1f} g CO₂  ({rs['savings_pct_of_total']:.1f}% of total footprint)"
    )
    st.caption(
        "Asia data centres currently run on a high-carbon grid (~500 gCO₂/kWh). "
        "Routing those workloads through EU infrastructure (~250 gCO₂/kWh) would halve their carbon — "
        "same model, same output, half the footprint."
    )

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — Optimization Scenarios
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    st.title("🔧 Optimization Scenarios — Before vs. After")
    st.caption("All savings are estimates. Scenarios are independent — do not add them together.")

    def scenario_card(label, data, note=""):
        st.subheader(label)
        if note:
            st.caption(note)
        before = data["before"]
        after  = data["after"]
        sav    = data["savings"]

        comparison = pd.DataFrame({
            "Metric":  ["Energy (Wh)",     "Carbon (g CO₂)",     "Cost (USD)"],
            "Before":  [f"{before['energy_Wh']:.1f}", f"{before['carbon_g']:.1f}", f"${before['cost_usd']:.2f}"],
            "After":   [f"{after['energy_Wh']:.1f}",  f"{after['carbon_g']:.1f}",  f"${after['cost_usd']:.2f}"],
            "Saved":   [
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
        f"Affects {sc['model_downgrade']['n_affected']:,} requests. "
        "No change in output quality for simple classification and short-form tasks.",
    )
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    scenario_card(
        "Scenario 2 — Token Reduction (25% prompt optimisation)",
        sc["token_reduction"],
        "Applies across all requests. Achieved by tightening system prompts, "
        "removing boilerplate context, and using concise instructions.",
    )
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    scenario_card(
        "Scenario 3 — Caching (remove all duplicate requests)",
        sc["caching"],
        f"{sc['caching']['dupes_removed']:,} duplicate requests removed. "
        "Caching is zero-cost infrastructure — it pays back immediately.",
    )

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.subheader("📊 Comparison — % Saved per Scenario")

    chart_data = pd.DataFrame({
        "Scenario":        ["Model Downgrade", "Token Reduction", "Caching"],
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
            "Cost Saved (%)":   "#F39C12",
        },
    )
    fig.update_layout(margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 5 — Meta Footprint
# ─────────────────────────────────────────────────────────────────────────────
with tab5:
    st.title("🌱 Meta Footprint — Carbon Cost of Building cleanAI")
    st.caption(
        "This module estimates the carbon emitted during the development of this tool itself. "
        "Transparency about our own footprint is part of the integrity of cleanAI."
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Dev AI Interactions",       f"{meta['interactions']}")
    c2.metric("Total Energy Used (est.)",  f"{meta['total_energy_Wh']:.0f} Wh  ({meta['total_energy_kWh']:.3f} kWh)")
    c3.metric("Total Carbon Emitted (est.)", f"{meta['total_carbon_g']:.1f} g CO₂  ({meta['total_carbon_kg']:.3f} kg)")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.subheader("Context")
    c1, c2 = st.columns(2)
    c1.metric("Equivalent driving distance (est.)", f"{meta['km_driven_equiv']:.1f} km")
    c2.metric("Equivalent smartphone charges (est.)", f"{meta['phone_charges_equiv']:.0f} charges")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
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
