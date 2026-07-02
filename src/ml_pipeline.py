import os
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
# Explicitly import the pipeline stages from our previous modules
from database_engine import fetch_raw_pipeline_data
from analytics_core import AnalyticsEngine

class HouseholdClusterPipeline:
    """
    Handles features scaling, training an Unsupervised K-Means model,
    and interpreting the resulting household personas.
    """
    def __init__(self, n_clusters=3, random_state=42):
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.model = KMeans(n_clusters=self.n_clusters, random_state=self.random_state, n_init=10)
        self.features = ['monthly_water_consumption_m3', 'monthly_waste_generation_kg', 'income_index']

    def train_pipeline(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Scales features to handle variance differences and assigns 
        each household to a discovered machine learning cluster.
        """
        print(f"[INFO] Initializing K-Means Pipeline with K={self.n_clusters} clusters...")
        processed_df = df.copy()
        
        # 1. Extract and Scale numerical features (crucial for distance-based models like K-Means)
        scaled_features = self.scaler.fit_transform(processed_df[self.features])
        
        # 2. Fit the Unsupervised Machine Learning Model
        processed_df['cluster_id'] = self.model.fit_predict(scaled_features)
        
        # 3. Map numerical clusters to professional operational personas
        processed_df['persona'] = processed_df['cluster_id'].apply(lambda x: f"Cluster Persona {x}")
        
        print("[SUCCESS] Machine learning model training and clustering complete.")
        return processed_df

    def generate_cluster_profiles(self, clustered_df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregates data by cluster ID to dynamically describe the statistical 
        identity of each discovered persona group.
        """
        print("[INFO] Computing profile matrices for discovered clusters...")
        
        # Calculate mean metrics per cluster to understand what they represent
        profiles = clustered_df.groupby('persona')[self.features + ['household_size']].mean()
        # Add household counts per cluster
        profiles['household_count'] = clustered_df.groupby('persona').size()
        
        return profiles.round(2)

if __name__ == "__main__":
    # Full end-to-end integration test (Stage 1 -> Stage 2 -> Stage 3)
    try:
        # Step 1: Extract from Database Engine
        raw_data = fetch_raw_pipeline_data()
        
        # Step 2: Clean and Impute using Analytics Core Engine
        analytics = AnalyticsEngine(raw_data)
        cleaned_data = analytics.clean_and_impute()
        
        # Step 3: Run Unsupervised Clustering Pipeline
        ml_pipeline = HouseholdClusterPipeline(n_clusters=3)
        clustered_df = ml_pipeline.train_pipeline(cleaned_data)
        profiles_matrix = ml_pipeline.generate_cluster_profiles(clustered_df)
        
        print("\n=== DISCOVERED HOUSEHOLD PERSONA PROFILES ===")
        print(profiles_matrix)
        print("=============================================")
        print("[SUCCESS] Stage 3 ML Pipeline executed cleanly.")
        
    except Exception as e:
        print(f"[ERROR] Integration failed: {e}")