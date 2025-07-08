import pandas as pd
import requests
import os

def fetch_cpi_data(series_id='CPIAUCSL', start_date='1990-01-01'):
    """
    Fetches Consumer Price Index (CPI) data from the FRED API.
    For simplicity, initially, we'll use a direct CSV download URL.
    A FRED API key would be needed for more flexible API calls.

    Args:
        series_id (str): The FRED series ID for CPI. Default is 'CPIAUCSL' (CPI for All Urban Consumers: All Items in U.S. City Average).
        start_date (str): The start date for the data in 'YYYY-MM-DD' format.

    Returns:
        pandas.DataFrame: A DataFrame containing the CPI data, or None if an error occurs.
    """
    # Direct download URL for CPIAUCSL from FRED
    # This URL provides the data as a CSV
    url = f"https://fred.stlouisfed.org/series/{series_id}/downloaddata/{series_id}.csv"
    print(f"Attempting to download CPI data from: {url}")

    try:
        # Use pandas to read the CSV directly from the URL
        # The 'DATE' column will be parsed as datetime objects
        df = pd.read_csv(url, index_col='DATE', parse_dates=True)
        df.columns = ['CPI'] # Rename the value column for clarity
        df = df[df.index >= start_date] # Filter by start date
        print(f"Successfully fetched CPI data. First 5 rows:\n{df.head()}")
        print(f"Last 5 rows:\n{df.tail()}")
        return df
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from FRED URL: {e}")
        return None
    except pd.errors.EmptyDataError:
        print("Error: The downloaded file is empty or malformed.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def main():
    print("Starting data fetching process...")
    cpi_df = fetch_cpi_data()

    if cpi_df is not None:
        # Save the data to a CSV file in a 'data' subfolder
        data_folder = 'data'
        os.makedirs(data_folder, exist_ok=True) # Create 'data' folder if it doesn't exist
        cpi_file_path = os.path.join(data_folder, 'cpi_data.csv')
        cpi_df.to_csv(cpi_file_path)
        print(f"CPI data saved to {cpi_file_path}")
    else:
        print("Failed to fetch CPI data.")

if __name__ == "__main__":
    main()