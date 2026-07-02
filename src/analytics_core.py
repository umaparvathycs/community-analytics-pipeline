import os
import pandas as pd
from scipy import stats
# Explicitly import the data extraction function from Stage 1
from database_engine import fetch_raw_pipeline_data

class AnalyticsEngine:
    """
    Handles automated data cleaning, segment-specific median imputation,
    and rigorous statistical hypothesis testing.
    """
    def __init__(self, raw_df: pd.DataFrame):
        self.df = raw_df.copy()
        self.cleaned_df = None
        self.t_test_results = {}

    def clean_and_impute(self) -> pd.DataFrame:
        """
        Executes a segment-aware imputation pipeline. 
        Imputing by global medians introduces bias because Urban and Rural 
        consumption metrics follow completely different underlying distributions.
        """
        print("[INFO] Initiating automated data cleaning pipeline...")
        
        # Working copy
        processed_df = self.df.copy()
        
        target_columns = ['monthly_water_consumption_m3', 'monthly_waste_generation_kg']
        
        for column in target_columns:
            # Calculate segment-specific medians dynamically
            # This isolates the distinct profiles of Rural vs Urban households
            medians = processed_df.groupby('segment_name')[column].transform('median')
            
            # Fill missing values using the corresponding segment median
            processed_df[column] = processed_df[column].fillna(medians)
            
        self.cleaned_df = processed_df
        print("[SUCCESS] Missing values successfully imputed using segment-specific medians.")
        return self.cleaned_df

    def run_hypothesis_testing(self) -> dict:
        """
        Executes a Two-Sample Independent T-Test to mathematically validate 
        if resource/waste variations between segments are statistically significant.
        """
        if self.cleaned_df is None:
            raise ValueError("Pipeline Error: Cannot run hypothesis testing on uncleaned data.")
            
        print("[INFO] Running Two-Sample Independent T-Tests (SciPy)...")
        
        # Split the metrics array by segment populations
        urban_metrics = self.cleaned_df[self.cleaned_df['segment_name'] == 'Urban']
        rural_metrics = self.cleaned_df[self.cleaned_df['segment_name'] == 'Rural']
        
        metrics_to_test = {
            'water': ('monthly_water_consumption_m3', 'Water Consumption (m³)'),
            'waste': ('monthly_waste_generation_kg', 'Waste Generation (kg)')
        }
        
        for key, (col_name, display_name) in metrics_to_test.items():
            urban_sample = urban_metrics[col_name]
            rural_sample = rural_metrics[col_name]
            
            # Execute Welch's T-Test (equal_var=False) because variances between 
            # urban and rural consumption footprints are not assumed to be identical.
            t_stat, p_value = stats.ttest_ind(urban_sample, rural_sample, equal_var=False)
            
            self.t_test_results[key] = {
                'metric': display_name,
                't_statistic': float(t_stat),
                'p_value': float(p_value),
                'statistically_significant': bool(p_value < 0.05)
            }
            
            print(f" -> {display_name} | T-Stat: {t_stat:.4f} | P-Value: {p_value:.4e} | Significant: {p_value < 0.05}")
            
        return self.t_test_results

if __name__ == "__main__":
    # Self-contained integration test to verify Stage 1 and Stage 2 talk to each other
    # Ensure you run this from the project root directory or have 'data/' initialized
    try:
        raw_data = fetch_raw_pipeline_data()
        print(f"[INFO] Successfully fetched {len(raw_data)} rows from SQL database engine.")
        
        # Initialize and run pipeline
        engine = AnalyticsEngine(raw_data)
        cleaned_df = engine.clean_and_impute()
        results = engine.run_hypothesis_testing()
        
        print("\n[SUCCESS] Stage 2 Analytics Pipeline executed cleanly.")
    except ModuleNotFoundError:
        print("[ERROR] Run this script from the project root or configure your PYTHONPATH so 'src' matches.")