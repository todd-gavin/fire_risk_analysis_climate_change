# California Wildfire and Rainfall Analysis

This project analyzes historical wildfire and rainfall data in California to identify potential correlations. It produces two main datasets:

1.  `wildfire_monthly.csv`: A monthly summary of wildfire incidents and acres burned per county.
2.  `rainfall_monthly.csv`: A monthly summary of total precipitation per county.

## Setup

### 1. Dependencies

This project requires Python 3.8+ and several packages. Install them using the provided `requirements.txt` file:

```bash
pip install -r requirements.txt
```

*Note: `geopandas` can sometimes be tricky to install. If you encounter issues, it is often easier to install it using `conda`.*

### 2. Data Acquisition

You need to download two datasets and place them in the specified locations within this project folder.

**a. Wildfire Data:**

*   **Source:** The user has provided this data in the file `CALFireMapDataAll.csv`.
*   **Action:** Ensure this file is in the root directory of the project.
*   **Placement:** The script expects this file to be at the root level.
    *   Expected path: `CALFireMapDataAll.csv`

**b. County Boundaries:**

*   **Source:** [California County Boundaries](https://gis.data.ca.gov/datasets/CALFIRE-Forestry::california-county-boundaries/about)
*   **Action:** Click the "Download" button and choose the "Shapefile" option.
*   **Placement:** Unzip the downloaded file. Place the resulting folder (e.g., `California_County_Boundaries`) inside the `data` folder.
    *   The script will look for the `.shp` file within this folder.
    *   Expected path to the shapefile: `data/California_County_Boundaries/California_County_Boundaries.shp`

## How to Run

1.  **Verify Paths:** Open `data_processor.py` and ensure the `WILDFIRE_INCIDENTS_CSV` and `COUNTY_BOUNDARIES_SHP` variables at the bottom of the script point to the correct file locations you set up in the previous step.

2.  **Execute Script:** Run the script from your terminal:

    ```bash
    python data_processor.py
    ```

The script will then process the data, downloading rainfall information and generating the two output CSV files in the project's root directory.
