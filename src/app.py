import os
import sys
import streamlit as pd
import streamlit as st
import pandas as pd

# Add the 'src' directory to the path so Streamlit can locate our modules smoothly
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from database_engine import fetch_raw_pipeline_data, initialize_database, seed_database
from analytics_core import AnalyticsEngine
from ml_pipeline import HouseholdClusterPipeline

# --- STREAMLIT PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Regional Resource & Community Metrics Pipeline",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Regional Resource & Community Metrics Pipeline")
st.markdown("""
An end-to-end, production-grade Data Engineering & Data Science pipeline. 
This application pulls live data from a normalized relational **SQLite Database**, routes it through a **Pandas cleaning layer**, executes automated **SciPy hypothesis testing**, and runs **Scikit-Learn unsupervised clustering** interactively.
""")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🛠️ Pipeline Configurations")

# Database Controls
st.sidebar.subheader("1. Database Storage Layer")
if st.sidebar.button("Re-initialize & Seed Database"):
    initialize_database()
    seed_database(num_households=250)
    st.sidebar.success("Database regenerated with fresh distributions!")

# ML Parameters
st.sidebar.subheader("2. Machine Learning Tuning")
k_clusters = st.sidebar.slider("Select K Clusters (Personas)", min_value=2, max_value=5, value=3, step=1)

# --- EXECUTE PIPELINE CORES ---
@st.cache_data(ttl=60)
def run_backend_pipeline():
    """Fetches raw data from SQLite and passes it through the cleaning engine."""
    raw_df = fetch_raw_pipeline_data()
    analytics = AnalyticsEngine(raw_df)
    cleaned_df = analytics.clean_and_impute()
    t_test_results = analytics.run_hypothesis_testing()
    return raw_df, cleaned_df, t_test_results

try:
    # 1 & 2: Pull and Process Layers
    raw_df, cleaned_df, t_test_results = run_backend_pipeline()
    
    # 3: Run ML Layer using the interactive slider input
    ml_pipeline = HouseholdClusterPipeline(n_clusters=k_clusters)
    clustered_df = ml_pipeline.train_pipeline(cleaned_df)
    persona_profiles = ml_pipeline.generate_cluster_profiles(clustered_df)

    # --- MAIN UI TABS DISPLAY ---
    tab1, tab2, tab3, tab4 = st.tabs([
        "🗄️ Relational Database (Stage 1)", 
        "🧪 Statistical Analytics (Stage 2)", 
        "🤖 Unsupervised ML (Stage 3)",
        "📋 Portfolio Summary"
    ])

    with tab1:
        st.header("Database Inspection Workspace")
        st.markdown("Direct read from `households` table via strict relational SQL inner joins.")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            st.metric("Total Records Injected", len(raw_df))
            st.metric("Rural Segment Count", len(raw_df[raw_df['segment_name'] == 'Rural']))
            st.metric("Urban Segment Count", len(raw_df[raw_df['segment_name'] == 'Urban']))
        with col2:
            st.subheader("Raw SQL Query Extraction Data Frame")
            st.dataframe(raw_df, use_container_width=True)

    with tab2:
        st.header("Automated Cleaning & Hypothesis Testing")
        st.markdown("""
        **Data Hygiene:** Missing values inside resource arrays were automatically imputed using *Segment-Aware Medians* to protect against urban/rural distribution mixing bias.
        """)
        
        st.subheader("Cleaned Dataset (Ready for ML)")
        st.dataframe(cleaned_df, use_container_width=True)
        
        st.markdown("---")
        st.subheader("Welch's Two-Sample Independent T-Test Results")
        st.markdown("Testing whether resource utilization distributions differ fundamentally across populations ($p < 0.05$).")
        
        for metric, data in t_test_results.items():
            card_col, desc_col = st.columns([1, 2])
            with card_col:
                status = "✅ Significant" if data['statistically_significant'] else "❌ Not Significant"
                st.markdown(f"### {data['metric']}")
                st.code(f"P-Value: {data['p_value']:.4e}\nT-Statistic: {data['t_statistic']:.4f}\nStatus: {status}")
            with desc_col:
                if data['statistically_significant']:
                    st.success(f"The structural variance in **{data['metric']}** between Urban and Rural community profiles is mathematically proven to be valid. Reject $H_0$.")
                else:
                    st.warning(f"We failed to reject the null hypothesis for **{data['metric']}**. Variance across segments could be random.")

    with tab3:
        st.header("Scikit-Learn K-Means Unsupervised Persona Discovery")
        st.markdown(f"The model scaled down spatial variance via `StandardScaler` and identified **{k_clusters}** separate household personas across the data coordinates.")
        
        st.subheader("Generated Persona Profile Coordinates")
        st.dataframe(persona_profiles, use_container_width=True)
        
        st.markdown("---")
        st.subheader("Clustered Household Log Matrix")
        st.dataframe(clustered_df[['household_id', 'segment_name', 'household_size', 'persona', 'cluster_id']], use_container_width=True)

    with tab4:
        st.header("Project Production Architecture Highlights")
        st.markdown("""
        ### Key Technical Components Met:
        * **Modularity:** Separate source modules handle database layers, business metrics, and modeling logic cleanly.
        * **Robust Cleaning Strategy:** Avoided naive global averages; used grouped medians to retain true data topology.
        * **Inferential Validation:** Utilized rigorous statistical parameters ($p$-values) to prove signal existences before downstream modeling.
        * **Distance-Preserving ML:** Applied feature standardizations to ensure K-Means coordinates cluster without spatial magnitude bias.
        """)
        st.balloons()

except Exception as global_err:
    st.error(f"Initialization Guard: Make sure you run Stage 1 and Stage 2 first to generate database footprints. Error details: {global_err}")