# geo_visualization.py
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# --- Configuration ---
ANALYSIS_FILE = 'data/wildfire_rainfall_analysis.csv'
COUNTY_BOUNDARIES_SHP = 'data/California_County_Boundaries_8408091426384550881/cnty19_1.shp'

def create_geo_visualization(analysis_path, shapefile_path):
    """Creates an interactive geographical map of wildfire and rainfall data."""
    print("--- Loading Data for Geo-Visualization ---")
    
    # Load the datasets
    try:
        df = pd.read_csv(analysis_path)
        gdf_counties = gpd.read_file(shapefile_path)
    except FileNotFoundError as e:
        print(f"Error: A required file was not found. {e}")
        return

    # --- Data Preprocessing ---
    # Create a date for sorting and selection
    df['date'] = pd.to_datetime(df[['year', 'month']].assign(day=1))
    df = df.sort_values('date')

    # Standardize county names for merging
    # The analysis file has title-cased county names, e.g., 'Los Angeles'
    # The shapefile's 'COUNTY_NAM' column needs to be formatted to match.
    gdf_counties['county'] = gdf_counties['COUNTY_NAM'].str.title()

    # Merge the analysis data with the geospatial data
    merged_gdf = gdf_counties.merge(df, on='county', how='left')

    # Fill NaNs for counties with no incident/rainfall data in a given month
    merged_gdf[['acres_burned', 'precip_in']] = merged_gdf[['acres_burned', 'precip_in']].fillna(0)

    print("Data loaded and merged successfully.")

    # --- Interactive Plot Setup ---
    fig, ax = plt.subplots(1, 1, figsize=(15, 15))
    plt.subplots_adjust(bottom=0.2)

    # Get unique dates for the slider
    unique_dates = df['date'].unique()
    date_map = {i: date for i, date in enumerate(unique_dates)}

    # Initial plot (for the first date)
    initial_date_index = 0
    initial_date = date_map[initial_date_index]
    data_for_date = merged_gdf[merged_gdf['date'] == initial_date]
    
    # Calculate representative points for placing bars
    merged_gdf['rep_point'] = merged_gdf['geometry'].representative_point()
    # Store current axes limits
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    # Plot the base map
    gdf_counties.plot(ax=ax, color='lightgray', edgecolor='black')
    ax.set_title(f"Wildfire and Rainfall Data for {pd.to_datetime(initial_date).strftime('%Y-%m')}")
    ax.set_axis_off()

    # --- Slider Widget ---
    ax_slider = plt.axes([0.2, 0.1, 0.65, 0.03], facecolor='lightgoldenrodyellow')
    slider = Slider(
        ax=ax_slider,
        label='Date',
        valmin=0,
        valmax=len(unique_dates) - 1,
        valinit=initial_date_index,
        valstep=1
    )

    def update(val):
        # Get the selected date from the slider's value
        date_index = int(slider.val)
        selected_date = date_map[date_index]
        
        # Filter data for the selected date
        data_for_date = merged_gdf[merged_gdf['date'] == selected_date]
        
        # Clear the previous plot content (bars and text)
        ax.clear()

        # Redraw the base map
        gdf_counties.plot(ax=ax, color='lightgray', edgecolor='black')
        ax.set_title(f"Wildfire and Rainfall Data for {pd.to_datetime(selected_date).strftime('%Y-%m')}")
        ax.set_axis_off()

        # Normalize data for the selected month for better visualization
        max_acres = data_for_date['acres_burned'].max()
        max_precip = data_for_date['precip_in'].max()

        # Add bars for each county
        for idx, row in data_for_date.iterrows():
            point = row.rep_point
            acres_val = row.acres_burned
            precip_val = row.precip_in

            # Normalize values for bar height (0 to 1)
            norm_acres = acres_val / max_acres if max_acres > 0 else 0
            norm_precip = precip_val / max_precip if max_precip > 0 else 0

            # Define inset axes position and size
            # This requires converting data coordinates to figure coordinates
            disp_point = ax.transData.transform((point.x, point.y))
            fig_point = fig.transFigure.inverted().transform(disp_point)
            
            bar_width = 0.01
            bar_height_scale = 0.05
            ax_inset = fig.add_axes([fig_point[0] - bar_width, fig_point[1], bar_width * 2, bar_height_scale])
            
            # Plot bars
            ax_inset.bar(0, norm_acres, color='firebrick', width=0.8)
            ax_inset.bar(1, norm_precip, color='royalblue', width=0.8)
            
            # Style inset plot
            ax_inset.set_xlim(-0.5, 1.5)
            ax_inset.set_ylim(0, 1)
            ax_inset.set_xticks([])
            ax_inset.set_yticks([])
            ax_inset.axis('off')

        fig.canvas.draw_idle()

    # Update slider labels to show dates
    def format_date(val):
        date_index = int(val)
        return pd.to_datetime(date_map[date_index]).strftime('%Y-%m')
    
    slider.valtext.set_text(format_date(initial_date_index))
    slider.on_changed(lambda val: slider.valtext.set_text(format_date(val)))
    slider.on_changed(update)

    plt.show()

if __name__ == "__main__":
    create_geo_visualization(ANALYSIS_FILE, COUNTY_BOUNDARIES_SHP)
