# process_wildfire_data.py
import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# --- Configuration ---
WILDFIRE_INCIDENTS_CSV = 'data/CALFireMapDataAll.csv'
COUNTY_BOUNDARIES_SHP = 'data/California_County_Boundaries_8408091426384550881/cnty19_1.shp'
WILDFIRE_OUTPUT_CSV = 'data/wildfire_monthly.csv'

def process_wildfire_data(incidents_csv_path, counties_shapefile_path, output_csv_path):
    """Processes raw wildfire data to produce a monthly summary by county."""
    print("--- Processing Wildfire Data ---")
    print(f"Reading wildfire data from {incidents_csv_path}...")
    
    try:
        df = pd.read_csv(incidents_csv_path, encoding='latin1', low_memory=False)
    except FileNotFoundError:
        print(f"Error: Input file not found at {incidents_csv_path}")
        return

    # Standardize column names
    df.columns = [col.strip().lower() for col in df.columns]

    # Ensure required columns are present
    required_cols = ['incident_county', 'incident_dateonly_created', 'incident_acres_burned']
    if not all(col in df.columns for col in required_cols):
        print(f"Error: Missing one or more required columns: {required_cols}")
        return

    # Convert acres burned to numeric, coercing errors to NaN
    df['incident_acres_burned'] = pd.to_numeric(df['incident_acres_burned'], errors='coerce')
    df.dropna(subset=['incident_acres_burned', 'incident_county'], inplace=True)

    # Handle multi-county incidents by creating a row for each county
    df['incident_county'] = df['incident_county'].str.split(',')
    df = df.explode('incident_county')
    df['incident_county'] = df['incident_county'].str.strip()

    # Convert date column to datetime objects
    df['incident_dateonly_created'] = pd.to_datetime(df['incident_dateonly_created'], errors='coerce')
    df.dropna(subset=['incident_dateonly_created'], inplace=True)

    # Extract year and month
    df['year'] = df['incident_dateonly_created'].dt.year
    df['month'] = df['incident_dateonly_created'].dt.month

    # Clean county names
    df['county'] = df['incident_county'].str.strip().str.title()

    monthly_summary = df.groupby(['county', 'year', 'month']).agg(
        incident_count=('incident_name', 'count'),
        acres_burned=('incident_acres_burned', 'sum')
    ).reset_index()

    print(f"Saving aggregated wildfire data to {output_csv_path}...")
    monthly_summary.to_csv(output_csv_path, index=False)
    print("Wildfire data processing complete.")

if __name__ == "__main__":
    process_wildfire_data(
        incidents_csv_path=WILDFIRE_INCIDENTS_CSV,
        counties_shapefile_path=COUNTY_BOUNDARIES_SHP,
        output_csv_path=WILDFIRE_OUTPUT_CSV
    )
