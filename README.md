# Localized Regional Resource & Community Metrics Pipeline

**Live Demo:** [community-analytics-pipeline.streamlit.app](https://community-analytics-pipeline.streamlit.app/)

---

## What This Project Does

This pipeline analyzes **household water consumption (m³)** and **monthly waste generation (kg)** across rural and urban communities. It's built for municipal planners and policy researchers who need an automated way to:

- Ingest raw survey data
- Clean missing values without introducing bias
- Statistically validate urban vs. rural differences
- Cluster households into behavioral personas
- Explore everything through an interactive dashboard

---

## Architecture Overview

The code is split into four independent, testable stages:

| Stage | Component | What It Does |
|-------|-----------|--------------|
| 1 | **Database (SQLite)** | Normalized schema with proper relationships. Includes a script to generate synthetic household data from scratch. |
| 2 | **Analytics (Pandas + SciPy)** | Pulls data, fills missing values using segment-specific medians (rural/urban separately), and runs a Welch's t-test to check if consumption differences are statistically significant. |
| 3 | **ML (Scikit-learn)** | Standardizes features with `StandardScaler`, then applies K-Means clustering to discover household personas. |
| 4 | **UI (Streamlit)** | Interactive dashboard where you can reseed the database, view data tables, and adjust the number of clusters on the fly. |

---

## Data Generation (Synthetic, but Realistic)

Instead of shipping a static CSV, the project generates its own data to mimic real-world survey responses:

| Group | Household Size | Income Index | Water (avg) | Waste (avg) |
|-------|---------------|--------------|-------------|-------------|
| Urban | 1–5 | ~0.65 | ~18.5 m³ | ~45 kg |
| Rural | 2–8 | ~0.40 | ~12.0 m³ | ~28 kg |

**Deliberately added noise to test the pipeline:**
- ~8–10% missing values (to validate imputation logic)
- ~4% extreme outliers (3× normal usage) to simulate commercial or industrial anomalies

---

## Repository Structure
community-analytics-pipeline/
├── src/
│   ├── database_engine.py   # Schema + data generator
│   ├── analytics_core.py    # Cleaning, imputation, t-test
│   ├── ml_pipeline.py       # Scaling + K-Means
│   └── app.py               # Streamlit dashboard
├── data/                    # Created automatically on first run (gitignored)
├── requirements.txt
└── README.md


> **Note:** The `data/` folder isn't in the GitHub repo. It's generated locally when you run the app or seed script. The `.db` file is excluded via `.gitignore` to keep the repo lightweight and avoid committing binary files.

---

## Key Insights from the Pipeline

With the default seeded data, here's what you'll see:

### Statistical Validation (Welch's t-test)
- The test consistently returns **p < 0.05**, meaning urban vs. rural consumption differences are real, not random.
- This matters because it confirms that the ML model is clustering *actual* behavioral patterns, not noise.

### Household Personas (K-Means, K=3)
The algorithm finds three distinct groups:

- **Persona 0 – Low-usage / Eco-conscious** – Mostly rural, low water and waste.  
- **Persona 1 – High-volume outliers** – The 4% anomaly group. Extreme consumption that warrants priority audits.  
- **Persona 2 – Standard urban baseline** – Mid-to-high income, dense-area households with predictable usage.

---

## Engineering Choices Worth Mentioning

- **Modular design** – `app.py` only handles presentation. All logic lives in separate, testable modules.
- **Defensive schema** – The database resets cleanly on each seed, with proper foreign key constraints (`ON DELETE RESTRICT ON UPDATE CASCADE`).
- **Cached performance** – Streamlit's `@st.cache_data` prevents the app from re-running expensive queries on every UI interaction.

---

## If This Were Scaled to Production

- Replace SQLite with **BigQuery** or **Snowflake** for massive datasets.  
- Orchestrate with **Airflow** or **Prefect** to schedule daily updates.  
- Containerize with **Docker** and deploy on **Kubernetes** for auto-scaling.

---

## Tech Stack

- Python 3.9+  
- SQLite3  
- Pandas, NumPy  
- SciPy (t-test)  
- Scikit-learn (StandardScaler, K-Means)  
- Streamlit (dashboard)

---

## Getting Started

```bash
# Clone the repo
git clone https://github.com/yourusername/community-analytics-pipeline.git
cd community-analytics-pipeline

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run src/app.py
```
