# map_wildfireData_to_rainfallData.py
import os
import pandas as pd

# --- Configuration ---
STATION_METADATA_CSV = 'data/CDEC Web ApplicationActive Real-Time Reporting Stations.csv'
RAW_RAINFALL_DIR = 'data/raw_rainfall'
WILDFIRE_MONTHLY_CSV = 'data/wildfire_monthly.csv'
RAINFALL_MONTHLY_CSV = 'data/rainfall_monthly.csv' # Final processed rainfall data
FINAL_ANALYSIS_CSV = 'data/wildfire_rainfall_analysis.csv' # Final merged data

def merge_datasets(wildfire_path, rainfall_path, output_path):
    """Merges the processed wildfire and rainfall data."""
    print("--- Merging Wildfire and Rainfall Data ---")
    try:
        wildfire_df = pd.read_csv(wildfire_path)
        rainfall_df = pd.read_csv(rainfall_path)

        # Ensure county names are standardized for merging
        wildfire_df['county'] = wildfire_df['county'].str.strip().str.title()
        rainfall_df['county'] = rainfall_df['county'].str.strip().str.title()

        # Ensure both dataframes have unique entries for county-year-month before merging
        wildfire_agg = wildfire_df.groupby(['county', 'year', 'month']).agg({
            'incident_count': 'sum',
            'acres_burned': 'sum'
        }).reset_index()

        rainfall_agg = rainfall_df.groupby(['county', 'year', 'month']).agg({
            'precip_in': 'sum'
        }).reset_index()

        # Use an outer join to keep all records from both datasets
        merged_df = pd.merge(wildfire_agg, rainfall_agg, on=['county', 'year', 'month'], how='outer')

        # Fill missing values with 0, as an outer join will create NaNs
        merged_df['incident_count'] = merged_df['incident_count'].fillna(0).astype(int)
        merged_df['acres_burned'] = merged_df['acres_burned'].fillna(0)
        merged_df['precip_in'] = merged_df['precip_in'].fillna(0)

        print(f"Saving final merged analysis file to {output_path}...")
        merged_df.to_csv(output_path, index=False)
        print("Datasets merged successfully.")
    except Exception as e:
        print(f"Error merging datasets: {e}")

if __name__ == "__main__":
    # The rainfall data is now processed by process_rainfall_data.py.
    # This script now only handles the merging.
    merge_datasets(
        wildfire_path=WILDFIRE_MONTHLY_CSV,
        rainfall_path=RAINFALL_MONTHLY_CSV,
        output_path=FINAL_ANALYSIS_CSV
    )

    print("\nData mapping complete.")
