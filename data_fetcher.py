import pandas as pd
import requests
import os

def fetch_cpi_data(series_id='CPIAUCSL', start_date='1990-01-01'):
    """
    Fetches Consumer Price Index (CPI) data from the FRED API.
    Uses a direct CSV download URL for simplicity.

    Args:
        series_id (str): The FRED series ID for CPI. Default is 'CPIAUCSL' (CPI for All Urban Consumers: All Items in U.S. City Average).
        start_date (str): The start date for the data in 'YYYY-MM-DD' format.

    Returns:
        pandas.DataFrame: A DataFrame containing the CPI data, or None if an error occurs.
    """
    url = f"https://fred.stlouisfed.org/series/{series_id}/downloaddata/{series_id}.csv"
    print(f"Attempting to download CPI data from: {url}")

    try:
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
        print("Error: The downloaded CPI file is empty or malformed.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while fetching CPI data: {e}")
        return None

def fetch_wage_data(series_id='AHETPI', start_date='1990-01-01'):
    """
    Fetches Average Hourly Earnings data from the FRED API.
    Uses a direct CSV download URL for simplicity.

    Args:
        series_id (str): The FRED series ID for Average Hourly Earnings. Default is 'AHETPI' (Average Hourly Earnings of All Employees, Total Private).
        start_date (str): The start date for the data in 'YYYY-MM-DD' format.

    Returns:
        pandas.DataFrame: A DataFrame containing the wage data, or None if an error occurs.
    """
    url = f"https://fred.stlouisfed.org/series/{series_id}/downloaddata/{series_id}.csv"
    print(f"Attempting to download Wage data from: {url}")

    try:
        df = pd.read_csv(url, index_col='DATE', parse_dates=True)
        df.columns = ['Wage'] # Rename the value column for clarity
        df = df[df.index >= start_date] # Filter by start date
        print(f"Successfully fetched Wage data. First 5 rows:\n{df.head()}")
        print(f"Last 5 rows:\n{df.tail()}")
        return df
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from FRED URL: {e}")
        return None
    except pd.errors.EmptyDataError:
        print("Error: The downloaded Wage file is empty or malformed.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while fetching Wage data: {e}")
        return None

def main():
    print("Starting data fetching process...")
    data_folder = 'data'
    os.makedirs(data_folder, exist_ok=True) # Ensure 'data' folder exists

    # Fetch CPI data
    cpi_df = fetch_cpi_data()
    if cpi_df is not None:
        cpi_file_path = os.path.join(data_folder, 'cpi_data.csv')
        cpi_df.to_csv(cpi_file_path)
        print(f"CPI data saved to {cpi_file_path}")
    else:
        print("Failed to fetch CPI data. Skipping save.")

    print("\n--- Fetching Wage Data ---")

    # Fetch Wage data
    wage_df = fetch_wage_data()
    if wage_df is not None:
        wage_file_path = os.path.join(data_folder, 'wage_data.csv')
        wage_df.to_csv(wage_file_path)
        print(f"Wage data saved to {wage_file_path}")
    else:
        print("Failed to fetch Wage data. Skipping save.")

    print("\nData fetching process complete.")

if __name__ == "__main__":
    main()