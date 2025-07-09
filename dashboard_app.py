import streamlit as st
import pandas as pd
import os
import plotly.express as px # Import Plotly Express
from datetime import datetime
import numpy as np # For handling potential NaN values

# --- Configuration ---
st.set_page_config(
    page_title="US Economic Dashboard",
    page_icon="📈",
    layout="wide"
)

# --- Data Loading and Processing ---
@st.cache_data
def load_and_process_data():
    """
    Loads CPI and Wage data, then calculates inflation rate and real wages.
    """
    data_folder = 'data'
    cpi_file_path = os.path.join(data_folder, 'cpi_data.csv')
    wage_file_path = os.path.join(data_folder, 'wage_data.csv')

    cpi_df = None
    wage_df = None
    merged_df = pd.DataFrame() # Initialize as empty DataFrame

    # Load CPI data
    if os.path.exists(cpi_file_path):
        try:
            cpi_df = pd.read_csv(cpi_file_path, index_col='DATE', parse_dates=True)
            cpi_df.columns = ['CPI']
            # Calculate Year-over-Year Inflation Rate
            cpi_df['Inflation Rate (%)'] = cpi_df['CPI'].pct_change(periods=12) * 100
            st.success(f"Loaded and processed CPI data from {cpi_file_path}")
        except Exception as e:
            st.error(f"Error loading or processing CPI data: {e}")
    else:
        st.warning(f"CPI data file not found at {cpi_file_path}. Please run data_fetcher.py first.")

    # Load Wage data
    if os.path.exists(wage_file_path):
        try:
            wage_df = pd.read_csv(wage_file_path, index_col='DATE', parse_dates=True)
            wage_df.columns = ['Wage']
            st.success(f"Loaded and processed Wage data from {wage_file_path}")
        except Exception as e:
            st.error(f"Error loading or processing Wage data: {e}")
    else:
        st.warning(f"Wage data file not found at {wage_file_path}. Please run data_fetcher.py first.")

    # Merge dataframes if both are available
    if cpi_df is not None and wage_df is not None:
        # Align dataframes by date index, using outer join to keep all dates, then interpolate
        # For simplicity, let's use inner join to ensure common dates for now.
        # For real-world, consider resampling or more advanced merging.
        merged_df = pd.merge(cpi_df, wage_df, left_index=True, right_index=True, how='inner')

        # Calculate Real Wages
        if not merged_df.empty and 'CPI' in merged_df.columns and 'Wage' in merged_df.columns:
            # Drop rows with NaN in CPI or Wage before calculating real wage
            merged_df_clean = merged_df.dropna(subset=['CPI', 'Wage'])
            if not merged_df_clean.empty:
                # Use the CPI value from the earliest date of the CLEANED data as base
                base_cpi = merged_df_clean['CPI'].iloc[0]
                merged_df['Real Wage (Adjusted)'] = (merged_df['Wage'] / merged_df['CPI']) * base_cpi
                st.success("Calculated Real Wages.")
            else:
                st.warning("Not enough clean data to calculate Real Wages.")
        else:
            st.warning("Could not calculate Real Wages due to missing data or columns.")
    elif cpi_df is not None or wage_df is not None:
        st.info("Only one dataset loaded. Cannot merge or calculate real wages.")
    else:
        st.error("No data loaded for merging.")

    return merged_df.dropna() # Drop any rows with NaNs that might remain from calculations

# Load and process all data
df = load_and_process_data()

# --- Dashboard Layout and Content ---

st.title("📈 US Inflation and Wage Trends Dashboard")
st.markdown("""
This interactive dashboard visualizes national-level economic data:
**Consumer Price Index (CPI)** as a measure of inflation, **Average Hourly Earnings**
as a measure of nominal wage trends, and **Real Wages** (adjusted for inflation).
""")

# --- Sidebar for Filters ---
st.sidebar.header("Filter Data")

if not df.empty:
    min_date = df.index.min()
    max_date = df.index.max()

    date_range = st.sidebar.slider(
        "Select Date Range:",
        min_value=min_date.to_pydatetime(),
        max_value=max_date.to_pydatetime(),
        value=(min_date.to_pydatetime(), max_date.to_pydatetime()),
        format="YYYY-MM"
    )
    filtered_df = df[(df.index >= date_range[0]) & (df.index <= date_range[1])]
else:
    st.warning("Data not loaded, date filter unavailable.")
    filtered_df = pd.DataFrame() # Empty DataFrame if no data


# --- Key Metrics Section ---
st.header("Key Economic Indicators (Latest Available)")
if not filtered_df.empty:
    latest_data = filtered_df.iloc[-1] # Get the most recent row of data
    latest_date = filtered_df.index[-1].strftime('%Y-%m')

    col1, col2, col3 = st.columns(3) # Create three columns for metrics

    with col1:
        st.metric(label=f"Latest Inflation Rate ({latest_date})",
                  value=f"{latest_data['Inflation Rate (%)']:.2f}%",
                  delta=f"{latest_data['Inflation Rate (%)'] - filtered_df['Inflation Rate (%)'].iloc[-2]:.2f}%" if len(filtered_df) > 1 else None,
                  delta_color="inverse") # inverse makes green for positive inflation (bad) and red for negative (good)

    with col2:
        st.metric(label=f"Latest Nominal Wage ({latest_date})",
                  value=f"${latest_data['Wage']:.2f}",
                  delta=f"${latest_data['Wage'] - filtered_df['Wage'].iloc[-2]:.2f}" if len(filtered_df) > 1 else None)

    with col3:
        if 'Real Wage (Adjusted)' in latest_data:
            st.metric(label=f"Latest Real Wage ({latest_date})",
                      value=f"${latest_data['Real Wage (Adjusted)']:.2f}",
                      delta=f"${latest_data['Real Wage (Adjusted)'] - filtered_df['Real Wage (Adjusted)'].iloc[-2]:.2f}" if len(filtered_df) > 1 else None)
        else:
            st.info("Real Wage not calculated.")
else:
    st.info("No data available to display key metrics.")

st.markdown("---") # Separator

# --- Interactive Visualization Section ---
st.header("Interactive Economic Trends Over Time")

if not filtered_df.empty:
    # Plot Inflation Rate with Plotly
    st.subheader("US Inflation Rate (Year-over-Year CPI Change)")
    fig_inflation = px.line(
        filtered_df,
        x=filtered_df.index,
        y='Inflation Rate (%)',
        title='US Year-over-Year Inflation Rate',
        labels={'x': 'Date', 'Inflation Rate (%)': 'Inflation Rate (%)'},
        color_discrete_sequence=['red']
    )
    fig_inflation.update_traces(mode='lines+markers', marker=dict(size=4)) # Add markers for clarity
    fig_inflation.update_layout(hovermode="x unified") # Unified hover for better comparison
    fig_inflation.add_hline(y=0, line_dash="dot", line_color="grey", annotation_text="Zero Inflation")
    st.plotly_chart(fig_inflation, use_container_width=True)

    st.markdown("---") # Separator

    # Plot Nominal vs. Real Wages with Plotly
    st.subheader("US Average Hourly Earnings: Nominal vs. Real")
    # Create a long-form dataframe for Plotly to easily plot multiple lines
    wage_plot_df = filtered_df[['Wage', 'Real Wage (Adjusted)']].reset_index()
    wage_plot_df_melted = wage_plot_df.melt(id_vars='DATE', var_name='Wage Type', value_name='Earnings ($)')

    fig_wages = px.line(
        wage_plot_df_melted,
        x='DATE',
        y='Earnings ($)',
        color='Wage Type',
        title='US Average Hourly Earnings: Nominal vs. Real',
        labels={'DATE': 'Date', 'Earnings ($)': 'Earnings ($)'},
        color_discrete_map={'Wage': 'green', 'Real Wage (Adjusted)': 'purple'}
    )
    fig_wages.update_traces(mode='lines+markers', marker=dict(size=4)) # Add markers for clarity
    fig_wages.update_layout(hovermode="x unified") # Unified hover for better comparison
    st.plotly_chart(fig_wages, use_container_width=True)

else:
    st.error("No data available to display charts. Please ensure data_fetcher.py ran successfully.")

# --- About/Methodology Section ---
st.markdown("---")
with st.expander("About This Dashboard & Methodology"):
    st.markdown("""
    This dashboard presents national-level economic data from the Federal Reserve Economic Data (FRED).

    **Data Series Used:**
    * **Consumer Price Index (CPI):** `CPIAUCSL` (Consumer Price Index for All Urban Consumers: All Items in U.S. City Average).
        * **Inflation Rate:** Calculated as the Year-over-Year percentage change in CPI:
            $$ \\text{Inflation Rate} = \\left( \\frac{\\text{CPI}_{\\text{current}}}{\\text{CPI}_{\\text{12 months ago}}} - 1 \\right) \\times 100 $$
    * **Average Hourly Earnings:** `AHETPI` (Average Hourly Earnings of All Employees, Total Private).
        * **Real Wage:** Calculated by adjusting nominal wages for inflation using the CPI. The formula used here is:
            $$ \\text{Real Wage} = \\left( \\frac{\\text{Nominal Wage}}{\\text{CPI}} \\right) \\times \\text{Base CPI} $$
            where the 'Base CPI' is the CPI value at the start of the dataset, allowing for a relative comparison of purchasing power over time.

    **Interactive Charts:**
    * **Hover:** Move your mouse over the lines to see specific data points.
    * **Zoom:** Click and drag a rectangle on the chart to zoom in. Double-click to zoom out.
    * **Pan:** Click and drag the chart when zoomed in.
    * **Toggle Series:** Click on the legend items to hide or show specific lines (e.g., hide 'Nominal Wage' to focus only on 'Real Wage').

    **Disclaimer:** This dashboard uses publicly available data for educational and illustrative purposes. For official economic analysis, please refer to government and academic sources.
    """)

st.info("Data sourced from the Federal Reserve Economic Data (FRED).")