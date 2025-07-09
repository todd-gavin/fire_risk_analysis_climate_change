# process_rainfall_data.py
import os
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import StringIO

# --- Configuration ---
STATION_METADATA_CSV = 'data/station_data.csv'
RAINFALL_MONTHLY_CSV = 'data/rainfall_monthly.csv'
TARGET_WATER_YEARS = range(2010, 2024)  # For water years 2010 through 2023
STATION_METADATA_OUTPUT_CSV = os.path.join('data', 'CDEC_station_metadata.csv')
RAW_RAINFALL_DIR = os.path.join('data', 'raw_rainfall')

def scrape_yearly_rainfall_data(year, output_dir):
    """Scrapes rainfall data for a single water year from CDEC."""
    url = f"https://cdec.water.ca.gov/reportapp/javareports?name=PRECIPMON.{year}"
    print(f"Scraping data for water year {year}...")

    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the table directly by its ID, as suggested.
        data_table = soup.find('table', id='data')
        
        if not data_table:
            raise ValueError(f"Could not find table with id='data' for year {year}.")

        html_string = str(data_table)
        # Read table without assuming a header row.
        data_df = pd.read_html(StringIO(html_string))[0]

        # The table structure is inconsistent. We will impose our own header
        # and skip the first row which contains the site's messy headers.
        data_df = data_df[1:]
        data_df.columns = [
            'station_id', 'station_name', 'oct', 'nov', 'dec', 'jan', 'feb', 
            'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep'
        ]

        # Drop summary rows and invalid data
        data_df.dropna(subset=['station_id'], inplace=True)
        data_df = data_df[~data_df['station_id'].str.contains('STATION', na=False)]
        data_df = data_df[~data_df['station_id'].str.contains('NUMBER OF STATIONS', na=False)]

        output_path = os.path.join(output_dir, f'rainfall_raw_{year}.csv')
        data_df.to_csv(output_path, index=False)
        print(f"  -> Saved to {output_path}")
        time.sleep(1)
        return True
    except Exception as e:
        print(f"Error processing year {year}: {e}")
        return False

def process_and_aggregate_rainfall(metadata_path, raw_data_dir, output_path):
    """Processes raw scraped rainfall data and aggregates it by county, year, and month."""
    print("--- Processing and Aggregating Rainfall Data ---")

    try:
        stations_df = pd.read_csv(metadata_path)
        # Normalize column names to be more robust
        stations_df.columns = [str(col).strip().replace(' ', '_').lower().replace('(feet)', '').replace('"','') for col in stations_df.columns]

        # Handle different possible column names for station ID and county
        if 'id' in stations_df.columns and 'county' in stations_df.columns:
            stations_df.rename(columns={'id': 'station_id'}, inplace=True)
        elif 'name' in stations_df.columns and 'county_name' in stations_df.columns:
            stations_df.rename(columns={'name': 'station_id', 'county_name': 'county'}, inplace=True)
        else:
            raise KeyError("Could not find required station ID and county columns in station metadata file.")

        if 'station_id' not in stations_df.columns:
            raise KeyError("Column 'station_id' not found after renaming.")

        station_county_map = stations_df.set_index('station_id')['county'].to_dict()
    except Exception as e:
        print(f"Error reading station metadata file '{metadata_path}': {e}")
        return

    all_monthly_data = []
    month_map = {
        'oct': 10, 'nov': 11, 'dec': 12, 'jan': 1, 'feb': 2, 'mar': 3,
        'apr': 4, 'may': 5, 'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9
    }

    for filename in os.listdir(raw_data_dir):
        if filename.startswith('rainfall_raw_') and filename.endswith('.csv'):
            water_year = int(filename.split('_')[-1].replace('.csv', ''))
            filepath = os.path.join(raw_data_dir, filename)
            df = pd.read_csv(filepath)

            month_cols = [col for col in df.columns if col in month_map]
            # Keep station_name through the melt process
            df_long = df.melt(id_vars=['station_id', 'station_name'], value_vars=month_cols, 
                              var_name='month_str', value_name='precip_in')
            
            df_long['precip_in'] = pd.to_numeric(df_long['precip_in'], errors='coerce')
            df_long.dropna(subset=['precip_in'], inplace=True)

            df_long['month'] = df_long['month_str'].map(month_map)
            df_long['year'] = df_long.apply(
                lambda row: water_year - 1 if row['month'] >= 10 else water_year,
                axis=1
            )
            all_monthly_data.append(df_long[['station_id', 'station_name', 'year', 'month', 'precip_in']])

    if not all_monthly_data:
        print("No raw rainfall data found to process.")
        return

    final_df = pd.concat(all_monthly_data, ignore_index=True)

    # First, map counties using the metadata file.
    final_df['county'] = final_df['station_id'].map(station_county_map)

    # For unmapped stations, try to infer county from station_name.
    unmapped = final_df['county'].isnull()
    if unmapped.any():
        print(f"Found {unmapped.sum()} station entries not in metadata. Attempting to infer county from station name...")
        # Create a list of California counties for matching
        ca_counties = [
            'Alameda', 'Alpine', 'Amador', 'Butte', 'Calaveras', 'Colusa', 'Contra Costa', 'Del Norte',
            'El Dorado', 'Fresno', 'Glenn', 'Humboldt', 'Imperial', 'Inyo', 'Kern', 'Kings', 'Lake',
            'Lassen', 'Los Angeles', 'Madera', 'Marin', 'Mariposa', 'Mendocino', 'Merced', 'Modoc',
            'Mono', 'Monterey', 'Napa', 'Nevada', 'Orange', 'Placer', 'Plumas', 'Riverside',
            'Sacramento', 'San Benito', 'San Bernardino', 'San Diego', 'San Francisco', 'San Joaquin',
            'San Luis Obispo', 'San Mateo', 'Santa Barbara', 'Santa Clara', 'Santa Cruz', 'Shasta',
            'Sierra', 'Siskiyou', 'Solano', 'Sonoma', 'Stanislaus', 'Sutter', 'Tehama', 'Trinity',
            'Tulare', 'Tuolumne', 'Ventura', 'Yolo', 'Yuba'
        ]
        # Normalize for case-insensitive matching
        county_pattern = '|'.join([f'(?i){county}' for county in ca_counties])
        inferred_county = final_df.loc[unmapped, 'station_name'].str.extract(f'({county_pattern})', expand=False)
        final_df.loc[unmapped, 'county'] = inferred_county.str.title()

    # Any remaining unmapped stations are assigned to 'Unknown' county.
    final_df['county'].fillna('Unknown', inplace=True)

    # Aggregate data, including the 'Unknown' county if it exists.
    aggregated_df = final_df.groupby(['county', 'year', 'month'])['precip_in'].sum().reset_index()
    aggregated_df['precip_in'] = aggregated_df['precip_in'].round(2)
    
    print(f"Saving aggregated rainfall data to {output_path}...")
    aggregated_df.to_csv(output_path, index=False)
    print("Rainfall data processing complete.")

if __name__ == "__main__":
    # 1. Scrape raw data
    raw_rainfall_dir = os.path.join('data', 'raw_rainfall')
    os.makedirs(raw_rainfall_dir, exist_ok=True)
    print("--- Scraping Yearly Rainfall Data ---")
    current_year = pd.Timestamp.now().year
    for year in range(2010, current_year + 1):
        scrape_yearly_rainfall_data(year, raw_rainfall_dir)
    print("\nRaw rainfall data scraping complete.")

    print("\n")

    # 2. Process and aggregate the raw data
    process_and_aggregate_rainfall(
        metadata_path=STATION_METADATA_CSV,
        raw_data_dir=raw_rainfall_dir,
        output_path=RAINFALL_MONTHLY_CSV
    )
