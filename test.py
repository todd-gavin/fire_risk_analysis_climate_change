import pandas as pd

def generate_yearly_summary(input_path):
    """
    Reads the raw monthly wildfire data and prints a summary of total incidents per year.
    """
    try:
        df = pd.read_csv(input_path, encoding='latin1', low_memory=False)
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_path}")
        return

    # Drop rows where the date is missing to avoid errors
    df.dropna(subset=['incident_dateonly_created'], inplace=True)

    # Convert date column to datetime objects, coercing errors to NaT
    df['incident_dateonly_created'] = pd.to_datetime(df['incident_dateonly_created'], errors='coerce')
    
    # Drop rows where date conversion failed
    df.dropna(subset=['incident_dateonly_created'], inplace=True)

    # Extract year from the date
    df['year'] = df['incident_dateonly_created'].dt.year

    # Group by year and count the number of incidents
    yearly_summary = df.groupby('year').size().reset_index(name='total_incidents')
    
    # Sort by year
    yearly_summary = yearly_summary.sort_values('year')

    print("Yearly Wildfire Incident Summary (from raw data):")
    # Using to_string() to ensure the full DataFrame is printed
    print(yearly_summary.to_string(index=False))

if __name__ == "__main__":
    generate_yearly_summary('data/CALFireMapDataAll.csv')