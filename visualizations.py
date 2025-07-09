# visualizations.py
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- Configuration ---
ANALYSIS_FILE = 'data/wildfire_rainfall_analysis.csv'
VISUALIZATIONS_DIR = 'visualizations'

def generate_visualizations(csv_path, output_dir):
    """Generates and saves visualizations for each county."""
    print("--- Generating Visualizations ---")

    try:
        df = pd.read_csv(csv_path)
        df['date'] = pd.to_datetime(df[['year', 'month']].assign(day=1))
    except FileNotFoundError:
        print(f"Error: Analysis file not found at '{csv_path}'. Please run the other scripts first.")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Set plot style
    sns.set_theme(style="whitegrid")

    # Convert date to string 'YYYY-MM' for stable plotting
    df['plot_date'] = df['date'].dt.strftime('%Y-%m')

    counties = sorted(df['county'].unique())
    for county in counties:
        print(f"Generating plot for {county} County...")
        county_df = df[df['county'] == county].sort_values('date').copy()

        if county_df.empty:
            continue

        county_dir = os.path.join(output_dir, county.replace(' ', '_'))
        if not os.path.exists(county_dir):
            os.makedirs(county_dir)

        # Set ticks to appear every 6 months for readability for all plots
        tick_positions = range(0, len(county_df['plot_date']), 6)
        tick_labels = [county_df['plot_date'].iloc[i] for i in tick_positions]

        # 1. Wildfire Acres Burned Over Time
        plt.figure(figsize=(18, 8))
        sns.lineplot(data=county_df, x='plot_date', y='acres_burned', color='firebrick', marker='o')
        plt.title(f'Total Acres Burned in {county} County (Monthly)', fontsize=16)
        plt.xlabel('Date')
        plt.ylabel('Acres Burned')
        plt.xticks(tick_positions, tick_labels, rotation=90)
        plt.tight_layout()
        plt.savefig(os.path.join(county_dir, 'acres_burned_monthly.png'))
        plt.close()

        # 2. Rainfall per Month
        plt.figure(figsize=(18, 8))
        ax = sns.barplot(data=county_df, x='plot_date', y='precip_in', color='royalblue')
        plt.title(f'Monthly Rainfall in {county} County', fontsize=16)
        plt.xlabel('Date')
        plt.ylabel('Precipitation (inches)')
        # Set ticks for every single month to show all dates
        ax.set_xticks(range(len(county_df['plot_date'])))
        ax.set_xticklabels(county_df['plot_date'], rotation=90, fontsize=8)
        plt.tight_layout()
        plt.savefig(os.path.join(county_dir, 'rainfall_monthly.png'))
        plt.close()

        # 3. Dual-Axis Plot: Acres Burned vs. Rainfall
        fig, ax1 = plt.subplots(figsize=(18, 8))
        sns.lineplot(data=county_df, x='plot_date', y='acres_burned', color='firebrick', ax=ax1, marker='o', label='Acres Burned')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Total Acres Burned', color='firebrick', fontsize=12)
        ax1.tick_params(axis='y', labelcolor='firebrick')
        ax1.set_xticks(tick_positions)
        ax1.set_xticklabels(tick_labels, rotation=90)

        ax2 = ax1.twinx()
        sns.lineplot(data=county_df, x='plot_date', y='precip_in', color='royalblue', marker='o', ax=ax2, label='Rainfall (in)', sort=False)
        ax2.set_ylabel('Precipitation (inches)', color='royalblue', fontsize=12)
        ax2.tick_params(axis='y', labelcolor='royalblue')
        ax2.set_ylim(bottom=0)

        plt.title(f'Acres Burned vs. Rainfall in {county} County', fontsize=16)
        fig.tight_layout()
        plt.savefig(os.path.join(county_dir, 'acres_vs_rainfall.png'))
        plt.close()

        # 4. Yearly Aggregated Plot
        yearly_df = county_df.groupby('year').agg(
            acres_burned=('acres_burned', 'sum'),
            precip_in=('precip_in', 'sum')
        ).reset_index()

        if not yearly_df.empty:
            fig, ax1 = plt.subplots(figsize=(18, 8))
            sns.lineplot(x=range(len(yearly_df)), y=yearly_df['acres_burned'], color='firebrick', ax=ax1, marker='o', label='Acres Burned')
            ax1.set_xlabel('Year')
            ax1.set_ylabel('Total Acres Burned', color='firebrick', fontsize=12)
            ax1.tick_params(axis='y', labelcolor='firebrick')
            ax1.set_xticks(range(len(yearly_df['year'])))
            ax1.set_xticklabels(yearly_df['year'], rotation=45)

            ax2 = ax1.twinx()
            # Plot line on the same axes, using the index for x to align with the bar plot
            sns.lineplot(x=range(len(yearly_df)), y=yearly_df['precip_in'], color='royalblue', marker='o', ax=ax2, label='Total Rainfall (in)')
            ax2.set_ylabel('Total Precipitation (inches)', color='royalblue', fontsize=12)
            ax2.tick_params(axis='y', labelcolor='royalblue')
            ax2.set_ylim(bottom=0)

            plt.title(f'Yearly Acres Burned vs. Rainfall in {county} County', fontsize=16)
            fig.tight_layout()
            plt.savefig(os.path.join(county_dir, 'yearly_analysis.png'))
            plt.close()

    print("\nVisualization generation complete.")
    print(f"Plots saved in '{output_dir}' directory.")

REGIONS = {
    'Bay Area': ['Alameda', 'Contra Costa', 'Marin', 'Napa', 'San Francisco', 'San Mateo', 'Santa Clara', 'Solano', 'Sonoma', 'Santa Cruz'],
    'Central Coast': ['Monterey', 'San Benito', 'San Luis Obispo', 'Santa Barbara'],
    'Central Valley': ['Fresno', 'Kern', 'Kings', 'Madera', 'Mariposa', 'Merced', 'Sacramento', 'San Joaquin', 'Stanislaus', 'Sutter', 'Tulare', 'Yolo', 'Yuba', 'Placer', 'El Dorado', 'Tuolumne'],
    'Northern California': ['Del Norte', 'Humboldt', 'Lassen', 'Mendocino', 'Modoc', 'Shasta', 'Siskiyou', 'Tehama', 'Trinity', 'Lake', 'Nevada', 'Sierra', 'Plumas'],
    'Southern California': ['Imperial', 'Inyo', 'Los Angeles', 'Mono', 'Orange', 'Riverside', 'San Bernardino', 'San Diego', 'Ventura']
}

def generate_regional_visualizations(input_path, regions_map):
    """Generates regional summary plots for wildfire and rainfall data."""
    print("\n--- Generating Regional Visualizations ---")
    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        print(f"Error: Analysis file not found at {input_path}")
        return

    # Map each county to its region
    county_to_region = {county: region for region, counties in regions_map.items() for county in counties}
    df['region'] = df['county'].map(county_to_region)
    df.dropna(subset=['region'], inplace=True) # Drop counties not in our defined regions

    # Aggregate data by region, year, and month
    regional_summary = df.groupby(['region', 'year', 'month']).agg(
        acres_burned=('acres_burned', 'sum'),
        precip_in=('precip_in', 'mean') # Use mean for regional rainfall
    ).reset_index()

    # Prepare for plotting
    regional_summary['plot_date'] = regional_summary['year'].astype(str) + '-' + regional_summary['month'].astype(str).str.zfill(2)
    regional_summary.sort_values('plot_date', inplace=True)

    output_dir = 'visualizations/regional_analysis'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for region, region_df in regional_summary.groupby('region'):
        print(f"Generating plot for {region}...")
        
        tick_positions = range(0, len(region_df['plot_date']), 6)
        tick_labels = [region_df['plot_date'].iloc[i] for i in tick_positions]

        fig, ax1 = plt.subplots(figsize=(18, 8))
        sns.lineplot(data=region_df, x='plot_date', y='acres_burned', color='firebrick', ax=ax1, marker='o', label='Acres Burned')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Total Acres Burned', color='firebrick', fontsize=12)
        ax1.tick_params(axis='y', labelcolor='firebrick')
        ax1.set_xticks(tick_positions)
        ax1.set_xticklabels(tick_labels, rotation=90)

        ax2 = ax1.twinx()
        sns.lineplot(data=region_df, x='plot_date', y='precip_in', color='royalblue', marker='o', ax=ax2, label='Avg. Rainfall (in)', sort=False)
        ax2.set_ylabel('Average Precipitation (inches)', color='royalblue', fontsize=12)
        ax2.tick_params(axis='y', labelcolor='royalblue')
        ax2.set_ylim(bottom=0)

        plt.title(f'Acres Burned vs. Rainfall in {region}', fontsize=16)
        fig.tight_layout()
        plt.savefig(os.path.join(output_dir, f'{region.replace(" ", "_")}_analysis.png'))
        plt.close()

    print("\nRegional visualization generation complete.")

    # --- Generate Yearly Regional Analysis ---
    print("\n--- Generating Yearly Regional Analysis ---")
    # Map counties to regions
    county_to_region = {county: region for region, counties in regions_map.items() for county in counties}
    df['region'] = df['county'].map(county_to_region)
    df.dropna(subset=['region'], inplace=True)

    # Aggregate data by region and year
    regional_yearly_summary = df.groupby(['region', 'year']).agg(
        acres_burned=('acres_burned', 'sum'),
        precip_in=('precip_in', 'sum')
    ).reset_index()

    for region in sorted(regional_yearly_summary['region'].unique()):
        print(f"Generating yearly analysis for {region}...")
        region_df = regional_yearly_summary[regional_yearly_summary['region'] == region].sort_values('year')
        
        if region_df.empty:
            continue

        region_dir = os.path.join(VISUALIZATIONS_DIR, 'regional_analysis')
        if not os.path.exists(region_dir):
            os.makedirs(region_dir)

        fig, ax1 = plt.subplots(figsize=(18, 8))
        sns.lineplot(x=range(len(region_df)), y=region_df['acres_burned'], color='firebrick', ax=ax1, marker='o', label='Acres Burned')
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Total Acres Burned', color='firebrick', fontsize=12)
        ax1.tick_params(axis='y', labelcolor='firebrick')
        ax1.set_xticks(range(len(region_df['year'])))
        ax1.set_xticklabels(region_df['year'], rotation=45)

        ax2 = ax1.twinx()
        sns.lineplot(x=range(len(region_df)), y=region_df['precip_in'], color='royalblue', marker='o', ax=ax2, label='Total Rainfall (in)')
        ax2.set_ylabel('Total Precipitation (inches)', color='royalblue', fontsize=12)
        ax2.tick_params(axis='y', labelcolor='royalblue')
        ax2.set_ylim(bottom=0)

        plt.title(f'Yearly Acres Burned vs. Rainfall in {region}', fontsize=16)
        fig.tight_layout()
        plt.savefig(os.path.join(region_dir, f'{region.replace(" ", "_")}_yearly_analysis.png'))
        plt.close()

    print("Yearly regional analysis generation complete.")

def generate_yearly_scatter_plots(input_path, output_dir):
    """Generates a scatter plot of rainfall vs. acres burned for each year."""
    print("\n--- Generating Yearly Scatter Plots ---")
    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        print(f"Error: Analysis file not found at {input_path}")
        return

    # Aggregate data by year and county
    yearly_summary = df.groupby(['year', 'county']).agg(
        acres_burned=('acres_burned', 'sum'),
        precip_in=('precip_in', 'sum')
    ).reset_index()

    scatter_output_dir = os.path.join(output_dir, 'yearly_scatter_plots')
    if not os.path.exists(scatter_output_dir):
        os.makedirs(scatter_output_dir)

    for year in sorted(yearly_summary['year'].unique()):
        print(f"Generating scatter plot for {year}...")
        # Create an explicit copy to avoid SettingWithCopyWarning
        year_df = yearly_summary[yearly_summary['year'] == year].copy()

        plt.figure(figsize=(16, 10))
        
        # Add a small constant to avoid issues with log(0)
        year_df['precip_in'] = year_df['precip_in'] + 1
        year_df['acres_burned'] = year_df['acres_burned'] + 1

        sns.scatterplot(data=year_df, x='precip_in', y='acres_burned', hue='county', s=100, legend=False)

        # Annotate points with county names
        for i, row in year_df.iterrows():
            plt.text(row['precip_in'], row['acres_burned'], row['county'], fontsize=9, ha='right')

        plt.xscale('log')
        plt.yscale('log')

        plt.title(f'Total Rainfall vs. Acres Burned by County in {year} (Log Scale)', fontsize=16)
        plt.xlabel('Total Annual Rainfall (inches) - Log Scale')
        plt.ylabel('Total Annual Acres Burned - Log Scale')
        plt.grid(True, which="both", ls="--")
        plt.tight_layout()
        plt.savefig(os.path.join(scatter_output_dir, f'scatter_{year}.png'))
        plt.close()
    
    print(f"Scatter plots saved to {scatter_output_dir}")

if __name__ == "__main__":
    generate_visualizations(ANALYSIS_FILE, VISUALIZATIONS_DIR)
    generate_regional_visualizations(ANALYSIS_FILE, REGIONS)
    generate_yearly_scatter_plots(ANALYSIS_FILE, VISUALIZATIONS_DIR)
