# app.py
# cleanAI — AI Efficiency & Carbon Insight Tool
# Streamlit dashboard entry point — v2.1
# All outputs are ESTIMATES based on published benchmarks and simulated usage.

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

# ── CSS: mobile responsive + card styles ──────────────────────────────────────
st.markdown("""
<style>
/* ── Mobile responsive layout ───────────────────────────────────────────── */
@media screen and (max-width: 768px) {
    div[data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; }
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        min-width: calc(100% - 1rem) !important;
        flex: 1 1 100% !important;
    }
    h1 { font-size: 1.4rem !important; line-height: 1.2 !important; }
    h2 { font-size: 1.15rem !important; }
    h3 { font-size: 1.05rem !important; }
    [data-testid="stMetricValue"] { font-size: 1.5rem !important; }
    [data-testid="stMetricLabel"] { font-size: 0.82rem !important; }
    button[data-baseweb="tab"] { font-size: 0.65rem !important; padding: 0.25rem 0.3rem !important; }
    .block-container { padding-left: 0.75rem !important; padding-right: 0.75rem !important; }
}

/* ── Purpose banner ─────────────────────────────────────────────────────── */
.purpose-banner {
    background: linear-gradient(135deg, rgba(46,204,113,0.12) 0%, rgba(52,152,219,0.12) 100%);
    border: 1px solid rgba(46,204,113,0.3);
    border-radius: 10px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 1.25rem;
    line-height: 1.6;
}
.purpose-banner strong { color: #27AE60; }

/* ── Headline callout cards ─────────────────────────────────────────────── */
.callout-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 0.75rem;
    margin-bottom: 1.25rem;
}
.callout-card {
    border-radius: 10px;
    padding: 1rem 1.2rem;
    line-height: 1.35;
}
.callout-card.red    { background: rgba(231,76,60,0.10);   border-left: 5px solid #E74C3C; }
.callout-card.amber  { background: rgba(243,156,18,0.10);  border-left: 5px solid #F39C12; }
.callout-card.blue   { background: rgba(52,152,219,0.10);  border-left: 5px solid #3498DB; }
.callout-card.green  { background: rgba(46,204,113,0.10);  border-left: 5px solid #2ECC71; }
.callout-stat { display: block; font-size: 2rem; font-weight: 800; letter-spacing: -0.5px; margin-bottom: 0.2rem; }
.callout-card.red   .callout-stat { color: #C0392B; }
.callout-card.amber .callout-stat { color: #D68910; }
.callout-card.blue  .callout-stat { color: #2980B9; }
.callout-card.green .callout-stat { color: #27AE60; }
.callout-label { font-size: 0.9rem; line-height: 1.4; }

/* ── Real-world comparison cards ────────────────────────────────────────── */
.compare-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 0.65rem;
    margin: 0.75rem 0 1.25rem 0;
}
.compare-card {
    background: rgba(128,128,128,0.06);
    border: 1px solid rgba(128,128,128,0.15);
    border-radius: 8px;
    padding: 0.85rem 1rem;
    text-align: center;
    line-height: 1.3;
}
.compare-icon  { font-size: 1.8rem; display: block; margin-bottom: 0.3rem; }
.compare-num   { font-size: 1.4rem; font-weight: 700; display: block; }
.compare-label { font-size: 0.78rem; opacity: 0.75; display: block; margin-top: 0.15rem; }

/* ── Assumption row styling ─────────────────────────────────────────────── */
.assumption-note {
    background: rgba(52,152,219,0.07);
    border-left: 4px solid #3498DB;
    border-radius: 6px;
    padding: 0.75rem 1rem;
    margin: 0.5rem 0 1rem 0;
    font-size: 0.9rem;
    line-height: 1.5;
}

/* ── Section divider ────────────────────────────────────────────────────── */
.section-divider { border: none; border-top: 1px solid rgba(128,128,128,0.18); margin: 1.25rem 0; }
</style>
""", unsafe_allow_html=True)

# ── Load + cache data ─────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    raw = generate_dataset()
    df  = compute_per_request(raw)
    return df

df        = load_data()
agg       = compute_aggregations(df)
insights  = run_all_insights(df)
scenarios = run_all_scenarios(df)
meta      = compute_meta_footprint()

# ── Pre-compute headline stats ────────────────────────────────────────────────
_by_region          = agg["by_region"].set_index("region")
_us_carbon_g        = _by_region.loc["us-east","carbon_g"] + _by_region.loc["us-west","carbon_g"]
_eu_carbon_g        = _by_region.loc["eu","carbon_g"]
_asia_carbon_g      = _by_region.loc["asia","carbon_g"]
_us_vs_eu_ratio     = _us_carbon_g / _eu_carbon_g
_heavy_tail_pct     = insights["heavy_tail"]["pct_energy"]
_cache_pct          = insights["repetition_waste"]["pct_requests"]
_cache_cost_savings = insights["repetition_waste"]["cost_saveable_usd"]
_overuse_count      = insights["model_overuse"]["count"]
_overuse_cost_waste = insights["model_overuse"]["cost_waste_usd"]
_downgrade_cost_pct = scenarios["model_downgrade"]["savings"]["saved_cost_usd_pct"]
_downgrade_carbon_pct = scenarios["model_downgrade"]["savings"]["saved_carbon_g_pct"]

# ── Real-world equivalents ────────────────────────────────────────────────────
# Reference constants (all well-cited averages)
_PHONE_Wh       = 12.5   # Wh for a full smartphone charge (typical ~3,000 mAh @ 3.7V)
_NETFLIX_Wh_hr  = 150.0  # Wh per hour of HD streaming (IEA / Carbon Trust estimates)
_KETTLE_Wh      = 90.0   # Wh to boil a full kettle (~1.5L, 3kW for 2 min)
_LED_W          = 10.0   # Watts for a standard LED bulb
_CAR_gCO2_km    = 170.0  # gCO2/km — UK/EU average petrol car (SMMT 2023)
_TREE_kgCO2_yr  = 21.8   # kg CO2 absorbed per tree per year (US Forest Service)
_FLIGHT_kgCO2   = 90.0   # kg CO2 per passenger for a 1hr domestic flight (BEIS 2023)

_E  = agg["total_energy_kWh"]       # total kWh
_C  = agg["total_carbon_kg"]        # total kg CO2
_Ep = agg["avg_energy_Wh"]          # avg Wh per request
_Cp = agg["avg_carbon_g"] / 1000    # avg kg CO2 per request

_phone_charges   = _E * 1000 / _PHONE_Wh
_netflix_hours   = _E * 1000 / _NETFLIX_Wh_hr
_kettle_boils    = _E * 1000 / _KETTLE_Wh
_led_hours       = _E * 1000 / _LED_W
_car_km          = _C * 1000 / _CAR_gCO2_km
_tree_days       = (_C / _TREE_kgCO2_yr) * 365

# Savings potential in real-world terms (using model downgrade as example)
_saved_carbon_kg = scenarios["model_downgrade"]["savings"]["saved_carbon_g"] / 1000
_saved_car_km    = _saved_carbon_kg * 1000 / _CAR_gCO2_km
_saved_tree_days = (_saved_carbon_kg / _TREE_kgCO2_yr) * 365

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌿 cleanAI")
    st.markdown("**AI Efficiency & Carbon Insight Tool**")
    st.caption("v2.1")
    st.markdown("---")
    st.markdown(f"📦 **Dataset:** {agg['total_requests']:,} requests")
    st.markdown(f"📅 **Period:** 90 days (simulated)")
    st.markdown(f"⚡ **Total energy:** {agg['total_energy_kWh']:.2f} kWh")
    st.markdown(f"🌍 **Total carbon:** {agg['total_carbon_kg']:.2f} kg CO₂")
    st.markdown(f"💰 **Total cost:** ${agg['total_cost_usd']:.2f}")
    st.markdown("---")
    st.caption(
        "All outputs are **estimates** based on published energy benchmarks "
        "and modelled AI usage patterns. See the Assumptions tab for full methodology."
    )

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Overview",
    "🔍 Breakdown",
    "⚠️ Inefficiencies",
    "🔧 Scenarios",
    "🌱 Meta Footprint",
    "📐 Assumptions",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — Overview
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    st.title("🌿 cleanAI — AI Carbon & Efficiency Tracker")

    # ── Purpose banner ────────────────────────────────────────────────────────
    st.markdown("""
<div class="purpose-banner">
<strong>What is this, and why does it matter?</strong><br>
Most organisations track their cloud bill down to the cent.
Almost none can tell you the carbon footprint of a single AI API call — let alone 7,500 of them.
<strong>cleanAI exists to change that.</strong>
It makes AI energy consumption visible, quantifies where the waste is,
and models the concrete steps you could take to reduce it —
without changing a single line of business logic.
The insight: <em>the same inefficiencies that drive your carbon footprint up are also driving your cost up.</em>
Fix one, and you fix both.
</div>
""", unsafe_allow_html=True)

    # ── Headline callouts ─────────────────────────────────────────────────────
    st.markdown("### 📣 Key Findings")
    st.markdown(f"""
<div class="callout-grid">
  <div class="callout-card red">
    <span class="callout-stat">{_us_vs_eu_ratio:.1f}×</span>
    <span class="callout-label">more AI carbon emitted in the US than the EU — same model, same output, vastly different footprint depending on where the server sits.</span>
  </div>
  <div class="callout-card amber">
    <span class="callout-stat">{_heavy_tail_pct:.0f}%</span>
    <span class="callout-label">of all AI energy is consumed by just the top 10% of requests. A small number of heavy, expensive calls drive the vast majority of the footprint.</span>
  </div>
  <div class="callout-card blue">
    <span class="callout-stat">{_overuse_count:,}</span>
    <span class="callout-label">requests used a large model (GPT-4 / Claude) for a task under 500 tokens — wasting <strong>${_overuse_cost_waste:.2f}</strong> that a smaller model would have handled identically.</span>
  </div>
  <div class="callout-card green">
    <span class="callout-stat">{_downgrade_cost_pct:.0f}%</span>
    <span class="callout-label">cost reduction available just by routing 30% of large-model calls to a smaller model. No retraining. No quality loss. Immediate impact.</span>
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # ── KPI cards ─────────────────────────────────────────────────────────────
    st.markdown("### 📊 Dataset at a Glance")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Requests",      f"{agg['total_requests']:,}")
    col2.metric("Total Energy",        f"{agg['total_energy_kWh']:.2f} kWh")
    col3.metric("Total Carbon (est.)", f"{agg['total_carbon_kg']:.2f} kg CO₂")
    col4.metric("Total Cost (est.)",   f"${agg['total_cost_usd']:,.2f}")

    # ── Real-world comparisons ────────────────────────────────────────────────
    st.markdown("#### What does that actually mean?")
    st.markdown(f"""
<div class="compare-grid">
  <div class="compare-card">
    <span class="compare-icon">📱</span>
    <span class="compare-num">{_phone_charges:,.0f}</span>
    <span class="compare-label">smartphone full charges</span>
  </div>
  <div class="compare-card">
    <span class="compare-icon">🎬</span>
    <span class="compare-num">{_netflix_hours:,.0f}</span>
    <span class="compare-label">hours of HD video streaming</span>
  </div>
  <div class="compare-card">
    <span class="compare-icon">☕</span>
    <span class="compare-num">{_kettle_boils:,.0f}</span>
    <span class="compare-label">full kettle boils</span>
  </div>
  <div class="compare-card">
    <span class="compare-icon">🚗</span>
    <span class="compare-num">{_car_km:,.1f} km</span>
    <span class="compare-label">driven in a petrol car</span>
  </div>
  <div class="compare-card">
    <span class="compare-icon">🌳</span>
    <span class="compare-num">{_tree_days:,.0f} days</span>
    <span class="compare-label">of a tree absorbing CO₂ to offset this</span>
  </div>
  <div class="compare-card">
    <span class="compare-icon">💡</span>
    <span class="compare-num">{_led_hours:,.0f} hrs</span>
    <span class="compare-label">of a 10W LED bulb running</span>
  </div>
</div>
""", unsafe_allow_html=True)

    st.caption(
        "📌 *Per single request:* avg **{:.4f} Wh** energy · avg **{:.4f} g CO₂** · avg **${:.5f}** cost. "
        "Tiny individually — but at scale, the numbers above tell the real story.".format(
            agg['avg_energy_Wh'], agg['avg_carbon_g'], agg['avg_cost_usd']
        )
    )

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # ── Optimisation upside in real-world terms ───────────────────────────────
    st.markdown("### 🎯 The Opportunity — In Terms You Can Picture")
    oc1, oc2, oc3 = st.columns(3)
    oc1.metric(
        "Just routing 30% of GPT-4 calls to a smaller model saves…",
        f"{_saved_car_km:.1f} km",
        "equivalent car journey eliminated",
    )
    oc2.metric(
        "Same optimisation — CO₂ saved",
        f"{_saved_carbon_kg*1000:.1f} g CO₂",
        f"≈ {_saved_tree_days:.0f} days of a tree's work",
    )
    oc3.metric(
        "Cost saved (same scenario)",
        f"${scenarios['model_downgrade']['savings']['saved_cost_usd']:.2f}",
        f"{_downgrade_cost_pct:.1f}% reduction",
    )
    st.caption(
        "These numbers are per 90-day / 7,500-request window. "
        "Multiply by your real request volume to see your organisation's actual opportunity."
    )

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # ── Energy over time ──────────────────────────────────────────────────────
    st.subheader("⚡ Energy Over Time")
    df_time       = df.copy()
    df_time["date"] = df_time["timestamp"].dt.date
    daily         = df_time.groupby("date")["energy_Wh"].sum().reset_index()
    daily.columns = ["date", "energy_Wh"]
    fig = px.area(daily, x="date", y="energy_Wh",
                  labels={"date": "Date", "energy_Wh": "Energy (Wh)"},
                  color_discrete_sequence=["#2ECC71"])
    fig.update_layout(showlegend=False, margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

    # ── Per-request summary table ─────────────────────────────────────────────
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
        "run a classification, trigger an agent — that's one request. "
        "Some are quick (a few hundred tokens, a fraction of a Wh). "
        "Others — long conversations, document analysis, agent loops — "
        "can use 50–100× more energy than the average. That gap is exactly what cleanAI is designed to surface."
    )

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — Breakdown
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.title("🔍 Breakdown by Model, Region & Request Type")
    st.markdown(
        "**To what end:** Understanding *where* your AI footprint comes from "
        "is the prerequisite for reducing it. These charts show which models, which geographies, "
        "and which use-cases are responsible for the majority of energy, carbon, and cost. "
        "That's where to focus first."
    )

    def breakdown_charts(group_df, group_col, label):
        st.subheader(f"By {label}")
        metrics = [
            ("energy_Wh", "Energy (Wh)",    "#3498DB"),
            ("carbon_g",  "Carbon (g CO₂)", "#E74C3C"),
            ("cost_usd",  "Cost (USD)",      "#F39C12"),
        ]
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

    breakdown_charts(agg["by_model"], "model", "Model")
    st.caption(
        "🤖 *Model choice is your biggest single lever.* GPT-4 uses 5× more energy per 1,000 tokens "
        "than a small model — yet a huge proportion of tasks (classification, short answers, "
        "formatting) don't need that power. Matching model to task is the fastest win."
    )
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    breakdown_charts(agg["by_region"], "region", "Region")
    st.caption(
        "🌍 *Why does region matter?* The carbon intensity of electricity varies massively by grid. "
        "The same AI computation run in the EU (~250 gCO₂/kWh) emits ~38% less CO₂ than in the US East "
        "(~400 gCO₂/kWh), and ~50% less than Asia (~500 gCO₂/kWh). "
        "Same model. Same output. Completely different footprint. "
        "Region-aware routing is a zero-code, zero-effort carbon reduction."
    )
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    breakdown_charts(agg["by_request_type"], "request_type", "Request Type")
    st.caption(
        "💡 *What are these request types?* "
        "**Chat** = conversational back-and-forth messages. "
        "**Classification** = quick category or yes/no decisions. "
        "**Embedding** = converting text to vectors for search or similarity matching. "
        "**Agent-loop** = AI calling tools or itself repeatedly to complete a multi-step task "
        "— by far the heaviest, since each step is a separate request."
    )

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — Inefficiencies
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.title("⚠️ Inefficiency Detection")
    st.markdown(
        "**To what end:** These five detectors identify patterns of *avoidable* waste — "
        "cases where the same AI output could have been produced with less energy and lower cost, "
        "simply by making smarter engineering choices. None of these require changing the AI model "
        "or the end-user experience. They're pure infrastructure and prompt hygiene wins."
    )

    # 8A — Token Inefficiency
    ti = insights["token_inefficiency"]
    st.subheader("8A — Token Inefficiency")
    c1, c2, c3 = st.columns(3)
    c1.metric("Flagged Requests",  f"{ti['count']:,}")
    c2.metric("% of All Requests", f"{ti['pct_requests']:.1f}%")
    c3.metric("% of Total Energy", f"{ti['pct_energy']:.1f}%")
    st.caption(
        f"Threshold: >{ti['threshold']:,.0f} tokens (2× the median of {ti['median_tokens']:,.0f}). "
        "These requests are likely bloated with excessive system prompts, full conversation history, "
        "or redundant context that isn't needed for the task. "
        "Trimming these alone could materially reduce your energy footprint."
    )
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # 8B — Model Overuse
    mo = insights["model_overuse"]
    st.subheader("8B — Model Overuse (Large Model, Tiny Task)")
    c1, c2, c3 = st.columns(3)
    c1.metric("Flagged Requests",    f"{mo['count']:,}")
    c2.metric("% of All Requests",   f"{mo['pct_requests']:.1f}%")
    c3.metric("Energy Waste (est.)", f"{mo['energy_waste_Wh']:.1f} Wh")
    st.metric("Cost Waste vs. small-model (est.)", f"${mo['cost_waste_usd']:.2f}")
    st.caption(
        f"These {mo['count']:,} requests sent fewer than 500 tokens to GPT-4 or Claude — "
        "models designed for complex reasoning. A lightweight model (GPT-3.5, Haiku, Mistral 7B) "
        "would have produced an identical result at a fraction of the energy and cost. "
        "This is the AI equivalent of hiring a specialist surgeon to put on a plaster."
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
    c1.metric("Duplicate Requests (est.)", f"{rw['count']:,}")
    c2.metric("% of All Requests",         f"{rw['pct_requests']:.1f}%")
    c3.metric("Energy Saveable (est.)",    f"{rw['energy_saveable_Wh']:.1f} Wh")
    st.metric("Cost Saveable via Caching (est.)", f"${rw['cost_saveable_usd']:.2f}")
    st.caption(
        "Requests with the same model, request type, and approximate token count, "
        "sent within a 1-hour window. A semantic cache layer (e.g. Redis + embedding similarity) "
        "would return the cached result instantly — zero compute, zero energy, zero cost. "
        "In production systems with real user traffic, this number is typically far higher."
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
    fig.add_vline(x=ht["threshold_Wh"], line_dash="dash", line_color="red",
                  annotation_text="Top 10% threshold")
    fig.update_layout(margin=dict(t=30, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        f"💡 *What does 'heavy tail' mean?* In any large-scale system, usage follows a power-law distribution: "
        f"most requests are small and cheap, but a long tail of large requests — "
        f"agent loops, document analysis, lengthy conversations — "
        f"consume disproportionate resources. "
        f"Here, the top 10% of requests account for {ht['pct_energy']:.0f}% of all energy. "
        "Identifying and optimising just those requests would have more impact than optimising "
        "the other 90% combined."
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
    _rs_car_km = rs['savings_g'] / 1000 / _CAR_gCO2_km * 1000
    st.caption(
        f"Equivalent to eliminating **{_rs_car_km:.1f} km** of petrol car driving. "
        "Asia data centres currently run on a carbon-intensive grid (~500 gCO₂/kWh). "
        "Routing those workloads through EU infrastructure (~250 gCO₂/kWh) would halve their footprint — "
        "same model, same output, half the climate impact. "
        "Many cloud providers (AWS, GCP, Azure) now offer region-aware routing as a first-class feature."
    )

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — Optimization Scenarios
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    st.title("🔧 Optimization Scenarios — Before vs. After")
    st.markdown(
        "**To what end:** It's one thing to know you have a carbon problem. "
        "It's another to know *what to do about it* and *how much it helps*. "
        "These three scenarios model the most actionable levers available to any engineering team — "
        "no new models, no new infrastructure contracts, no changes to the user experience. "
        "Pure configuration and routing decisions that can be made in a sprint."
    )
    st.caption("All savings are estimates. Scenarios are independent — do not add them together.")

    def scenario_card(label, data, note="", insight=""):
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
        if insight:
            st.caption(insight)

    sc = scenarios
    scenario_card(
        "Scenario 1 — Model Downgrade (30% of GPT-4 → small-model)",
        sc["model_downgrade"],
        note=f"Affects {sc['model_downgrade']['n_affected']:,} requests. "
             "Targets calls where a smaller model produces identical output.",
        insight=(
            f"In real-world terms: saving {_saved_car_km:.1f} km of petrol car emissions "
            f"and ${sc['model_downgrade']['savings']['saved_cost_usd']:.2f} — "
            "from a single routing rule change."
        ),
    )
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    scenario_card(
        "Scenario 2 — Token Reduction (25% prompt optimisation)",
        sc["token_reduction"],
        note="Applies across all requests. Achieved by tightening system prompts, "
             "removing boilerplate context, and using concise instructions.",
        insight=(
            "Token reduction is purely a prompt engineering discipline — "
            "no model changes, no infrastructure changes. "
            "A well-optimised system prompt is almost always shorter AND more effective."
        ),
    )
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    scenario_card(
        "Scenario 3 — Caching (remove all duplicate requests)",
        sc["caching"],
        note=f"{sc['caching']['dupes_removed']:,} duplicate requests removed. "
             "A response cache returns stored answers for repeated queries — "
             "zero compute, zero energy, immediate response.",
        insight=(
            "Caching is the only optimisation here that also *improves* the user experience: "
            "cached responses are returned in milliseconds, not seconds."
        ),
    )

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.subheader("📊 Comparison — % Saved per Scenario")
    chart_data = pd.DataFrame({
        "Scenario":         ["Model Downgrade", "Token Reduction", "Caching"],
        "Energy Saved (%)": [sc["model_downgrade"]["savings"]["saved_energy_Wh_pct"],
                             sc["token_reduction"]["savings"]["saved_energy_Wh_pct"],
                             sc["caching"]["savings"]["saved_energy_Wh_pct"]],
        "Carbon Saved (%)": [sc["model_downgrade"]["savings"]["saved_carbon_g_pct"],
                             sc["token_reduction"]["savings"]["saved_carbon_g_pct"],
                             sc["caching"]["savings"]["saved_carbon_g_pct"]],
        "Cost Saved (%)":   [sc["model_downgrade"]["savings"]["saved_cost_usd_pct"],
                             sc["token_reduction"]["savings"]["saved_cost_usd_pct"],
                             sc["caching"]["savings"]["saved_cost_usd_pct"]],
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
    st.markdown(
        "**To what end:** If we're going to ask others to measure and reduce their AI footprint, "
        "we should be willing to measure our own. This tab estimates the carbon emitted "
        "during the development of cleanAI itself — using the same methodology as the rest of the tool. "
        "It's an act of transparency, and a small proof that the tool isn't exempt from its own standard."
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Dev AI Interactions",          f"{meta['interactions']}")
    c2.metric("Total Energy Used (est.)",     f"{meta['total_energy_Wh']:.0f} Wh  ({meta['total_energy_kWh']:.3f} kWh)")
    c3.metric("Total Carbon Emitted (est.)",  f"{meta['total_carbon_g']:.1f} g CO₂  ({meta['total_carbon_kg']:.3f} kg)")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.subheader("Context")
    c1, c2 = st.columns(2)
    c1.metric("Equivalent driving distance (est.)", f"{meta['km_driven_equiv']:.1f} km")
    c2.metric("Equivalent smartphone charges (est.)", f"{meta['phone_charges_equiv']:.0f} charges")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.subheader("Methodology")
    st.markdown(f"""
| Assumption | Value | Rationale |
|---|---|---|
| Energy per AI interaction | {meta['energy_per_interaction_Wh']} Wh | Midpoint of published 2–10 Wh range for large LLM inference |
| Development interactions | {meta['interactions']} | Midpoint of estimated 100–300 dev sessions |
| Build region | {meta['build_region']} | Location where development occurred |
| Carbon intensity | {meta['carbon_intensity_gCO2_kWh']} gCO₂/kWh | US East grid average (EPA eGRID 2023) |

All values are estimates. See the Assumptions tab for full source references.
    """)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 6 — Assumptions & Methodology
# ─────────────────────────────────────────────────────────────────────────────
with tab6:
    st.title("📐 Assumptions & Methodology")
    st.markdown(
        "**To what end:** Every number in this tool is derived from a chain of assumptions. "
        "This tab makes that chain fully explicit — so you can evaluate the methodology yourself, "
        "challenge the numbers, or swap in your own constants. "
        "Transparency here isn't a disclaimer. It's the point."
    )

    # ── Why simulate? ─────────────────────────────────────────────────────────
    st.subheader("Why use simulated data?")
    st.markdown("""
<div class="assumption-note">
We don't have access to anyone's API logs — and you shouldn't hand them over to a third party anyway.
Instead, cleanAI uses a <strong>statistically realistic synthetic dataset</strong> built from published benchmarks.

From a data science perspective, this is a well-established and defensible approach:
the <em>distribution shapes</em> are calibrated to real-world AI usage patterns (log-normal token counts,
power-law energy tails, realistic model mix), even though the individual records are synthetic.
The purpose isn't to describe one company's specific usage — it's to demonstrate the
<strong>class of problems</strong> that exists in AI usage at scale, and the
<strong>magnitude of the opportunity</strong> if those problems are addressed.

Think of it like a crash test dummy: the dummy isn't a real person,
but the physics it reveals are completely real.
</div>
""", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**What's realistic in the simulation:**")
        st.markdown("""
- Log-normal token distributions (matches observed LLM usage skew)
- ~5% extreme outliers (long agent loops / document analysis)
- ~15% near-duplicate requests (realistic for chatbots with repeated queries)
- Weighted model and region distributions (reflects typical enterprise mix)
- 90-day window, 7,500 requests (mid-size team / 3 months of moderate AI usage)
""")
    with col_b:
        st.markdown("**What's deliberately simplified:**")
        st.markdown("""
- Energy rates are per-model averages, not per-inference measurements
- Latency and batching effects not modelled
- No prompt caching credit (some providers cache system prompts)
- Carbon grid data uses regional averages, not real-time marginal intensity
- Cost uses published list prices, not negotiated enterprise rates
""")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # ── Energy rates ──────────────────────────────────────────────────────────
    st.subheader("⚡ Energy Rates — per 1,000 Tokens (Wh)")
    energy_df = pd.DataFrame([
        {"Model": "GPT-4",       "Wh / 1k tokens": 0.5,  "Basis": "Patterson et al. (2021); IEA AI report (2024); cross-referenced with Luccioni et al. (2023)"},
        {"Model": "Claude",      "Wh / 1k tokens": 0.4,  "Basis": "Estimated from comparable transformer architecture; Anthropic efficiency disclosures"},
        {"Model": "GPT-3.5",     "Wh / 1k tokens": 0.2,  "Basis": "Published estimates ~4–5× more efficient than GPT-4 class models"},
        {"Model": "Small-model", "Wh / 1k tokens": 0.1,  "Basis": "7B–13B parameter models (Mistral, Llama); Touvron et al. (2023)"},
    ])
    st.dataframe(energy_df, use_container_width=True, hide_index=True)
    st.caption(
        "⚠️ These are estimates. Actual energy consumption varies significantly with batch size, "
        "hardware generation, quantisation, and provider infrastructure efficiency. "
        "No model provider currently publishes per-inference energy figures publicly."
    )

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # ── Carbon intensity ──────────────────────────────────────────────────────
    st.subheader("🌍 Carbon Intensity — by Region (gCO₂/kWh)")
    carbon_df = pd.DataFrame([
        {"Region": "US East",    "gCO₂/kWh": 400, "Source": "EPA eGRID 2023 — US East Interconnection average"},
        {"Region": "US West",    "gCO₂/kWh": 300, "Source": "EPA eGRID 2023 — WECC average (includes California hydro/solar)"},
        {"Region": "EU",         "gCO₂/kWh": 250, "Source": "European Environment Agency (EEA) 2023 — EU27 grid average"},
        {"Region": "Asia",       "gCO₂/kWh": 500, "Source": "IEA 2023 — weighted average for major Asia-Pacific data centre markets (China, Singapore, Japan)"},
    ])
    st.dataframe(carbon_df, use_container_width=True, hide_index=True)
    st.caption(
        "These are annual average intensities. Real-time marginal carbon intensity "
        "(as used by tools like Electricity Maps) can vary 2–3× intraday. "
        "Using averages slightly underestimates the benefit of time-shifting workloads."
    )

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # ── Cost rates ────────────────────────────────────────────────────────────
    st.subheader("💰 Cost Rates — per 1,000 Tokens (USD)")
    cost_df = pd.DataFrame([
        {"Model": "GPT-4",       "$/1k tokens": "$0.030", "Source": "OpenAI list price (blended input/output, GPT-4 Turbo, 2024)"},
        {"Model": "Claude",      "$/1k tokens": "$0.015", "Source": "Anthropic list price (Claude 3 Sonnet, blended, 2024)"},
        {"Model": "GPT-3.5",     "$/1k tokens": "$0.002", "Source": "OpenAI list price (GPT-3.5-Turbo, 2024)"},
        {"Model": "Small-model", "$/1k tokens": "$0.001", "Source": "Estimated from Mistral/Llama-class hosted API pricing (Together AI, Groq, 2024)"},
    ])
    st.dataframe(cost_df, use_container_width=True, hide_index=True)
    st.caption("List prices only. Enterprise agreements, volume discounts, and prompt caching credits not modelled.")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # ── Real-world reference points ───────────────────────────────────────────
    st.subheader("🔄 Real-World Comparison References")
    rw_df = pd.DataFrame([
        {"Analogy": "📱 Smartphone charge",  "Value": "12.5 Wh",       "Source": "Typical 3,000 mAh battery at 3.7V; USB-C charging efficiency ~90%"},
        {"Analogy": "🎬 HD video streaming", "Value": "150 Wh/hour",   "Source": "IEA 'The carbon footprint of streaming video' (2020); Carbon Trust (2021)"},
        {"Analogy": "☕ Boiling a kettle",   "Value": "90 Wh / boil",  "Source": "1.5L @ 3kW for ~2 minutes; standard UK/EU electric kettle"},
        {"Analogy": "💡 10W LED bulb",       "Value": "10 W",          "Source": "Standard LED equivalent to 60W incandescent"},
        {"Analogy": "🚗 Petrol car CO₂",     "Value": "170 gCO₂/km",  "Source": "SMMT UK new car fleet average 2023; BEIS conversion factors"},
        {"Analogy": "🌳 Tree absorption",    "Value": "21.8 kg CO₂/yr","Source": "US Forest Service (2023); assumes average broadleaf temperate tree"},
    ])
    st.dataframe(rw_df, use_container_width=True, hide_index=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # ── Dataset generation ────────────────────────────────────────────────────
    st.subheader("🎲 Simulation Methodology")
    st.markdown("""
| Parameter | Value | Rationale |
|---|---|---|
| Total requests | 7,500 | Representative of a mid-size team over a quarter |
| Time span | 90 days | Standard reporting quarter |
| Random seed | 42 | Fixed for full reproducibility |
| Token distribution | Log-normal (μ=6.5, σ=1.0) | Matches observed LLM token usage skew |
| Outlier injection | ~5% at 10,000–15,000 tokens | Models agent loops and document analysis |
| Near-duplicate rate | ~15% within 1-hour window | Models chatbots with repeated user queries |
| Model mix | GPT-4 35%, GPT-3.5 30%, Claude 25%, Small 10% | Reflects typical 2024 enterprise API usage |
| Region mix | US-East 40%, US-West 25%, EU 20%, Asia 15% | Approximate AWS/GCP/Azure workload distribution |

All constants defined in `assumptions.py`. To use real data, export your API usage logs
as a CSV and replace `data_generator.py` with a CSV loader — the rest of the pipeline
works unchanged.
""")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.caption(
        "cleanAI is an open methodology. If you believe any assumption is materially wrong, "
        "every constant lives in `assumptions.py` and can be updated in minutes. "
        "The goal is a framework for thinking about AI efficiency — not a claim of measurement precision."
    )
