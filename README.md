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
