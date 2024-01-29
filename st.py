import streamlit as st
import polars as pl
import plotly.express as px
from datetime import datetime, time
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

st.set_page_config(layout="wide")
col_mapping = column_mapping = {
    "": "time",
    "Språk": "language",
    "Temperature unit: 0 = Celcius, 1 = Fahrenheit": "temperature_unit",
    "Power: 0 = Low, 1 = High, 2 = Auto": "power_mode",
    "Pellet storlek [mm]": "pellet_size_mm",
    "Current start dose [s]": "current_start_dose_seconds",
    "Low power wattage [kW]": "low_power_wattage_kw",
    "Low power fan [%]": "low_power_fan_percent",
    "High power wattage [kW]": "high_power_wattage_kw",
    "High power fan [%]": "high_power_fan_percent",
    "Power change temperature [°C]": "power_change_temperature_celsius",
    "External sensor: 0 = No, 1 = Used, 2 = Disabled": "external_sensor_state",
    "Temperature for starting [°C]": "start_temperature_celsius",
    "Temperature for stopping [°C]": "stop_temperature_celsius",
    "Fan target rpm [rpm]": "fan_target_rpm",
    "Get auger status": "auger_status",
    "Is ignition element on": "ignition_element_status",
    "Software version, Major": "software_version_major",
    "Software version, Minor": "software_version_minor",
    "Burner state": "burner_state",
    "External temperature [°C]": "external_temperature_celsius",
    "Fan RPM [rpm]": "fan_rpm",
    "Measured DC current [mA]": "measured_dc_current_mA",
    "Measured AC current [mA]": "measured_ac_current_mA",
    "Flame present": "flame_presence",
    "Overheat input state": "overheat_input_state",
    "Safety switch input state": "safety_switch_state",
    "Thermostat input state": "thermostat_input_state",
    "Door switch (future)": "door_switch_state",
    "Ash since latest scrape": "ash_since_scrape",
    "PCB temperature [°C]": "pcb_temperature_celsius",
    "Hours since boiler clean up [h]": "hours_since_boiler_cleanup",
    "Long average flame AD value": "long_average_flame_AD_value",
    "Feed calibration, low [g]": "feed_calibration_low_grams",
    "Feed calibration, high [g]": "feed_calibration_high_grams",
    "Ignition try": "ignition_try",
    "Establish try": "establish_try",
    "Extinguish try": "extinguish_try",
}
# df = pl.read_csv("test/log.csv", separator=";")[:, 1:].rename(col_mapping)
uploaded_files = st.file_uploader(
    "Choose CSV files", accept_multiple_files=True, type="csv"
)

# Check if files are uploaded
if uploaded_files:
    # Initialize an empty DataFrame
    df_combined = pl.DataFrame()

    # Loop through each uploaded file
    for uploaded_file in uploaded_files:
        # Read the file into a DataFrame

        # df = pd.read_csv(uploaded_file, sep=";", index_col=None)
        # st.write(df)
        df = pl.read_csv(uploaded_file, separator=";", encoding="utf16")[:, 1:].rename(
            col_mapping
        )

        # Combine date and time into a single datetime column
        df = df.with_columns(
            [
                pl.col("time").str.strptime(
                    pl.Datetime, "%Y-%m-%d_%H-%M-%S", strict=False
                )
            ]
        )

        # Append to the combined DataFrame
        df_combined = df_combined.vstack(df) if df_combined.height > 0 else df
        df = df_combined

    # Continue with your existing plotting code, but use df_combined instead of df
    # ...

    # User selects multiple columns to plot

    # selected_column = st.selectbox("Select variable to plot", options=df.columns)
    selected_columns = st.multiselect(
        "Select variables to plot",
        options=df.columns,
    )
    start_date = st.date_input("Start date", value=df["time"].min())
    end_date = st.date_input("End date", value=df["time"].max())

    # Ensure that start_date is not after end_date
    if start_date > end_date:
        st.error("Error: End date must fall after start date.")
        st.stop()

    # Ensure that start_date is not after end_date
    if start_date > end_date:
        st.error("Error: End date must fall after start date.")
        st.stop()

    start_time = st.time_input("Start time", value=time(0, 0))
    end_time = st.time_input("End time", value=time(23, 59))

    # Combine date and time inputs to create datetime objects
    start_datetime = datetime.combine(start_date, start_time)
    end_datetime = datetime.combine(end_date, end_time)

    # Convert the 'time' column to datetime format using the correct format string

    df_plot = df.filter(
        (pl.col("time") >= start_datetime)
        & (pl.col("time") <= end_datetime)
        # & (pl.col(selected_column) != pl.col(selected_column).shift(-1))
    )

    if len(selected_columns) == 0:
        st.warning("Select variable to plot")
    else:
        fig = make_subplots(
            rows=len(selected_columns), cols=1, shared_xaxes=True, vertical_spacing=0.02
        )
        # Update layout if needed
        for i, col in enumerate(selected_columns, start=1):
            # Create a mask to identify rows where the selected column changes
            change_mask = (pl.col(col) != pl.col(col).shift(-1)) | (
                pl.col(col) != pl.col(col).shift()
            )

            # Apply the mask to the DataFrame
            df_plot = df.filter(change_mask)

            # Add a line plot to the current subplot
            fig.add_trace(
                go.Scatter(x=df_plot["time"], y=df_plot[col], mode="lines", name=col),
                row=i,
                col=1,
            )
        fig.update_layout(
            height=500 * len(selected_columns),
            title_text="Subplots for Selected Variables",
        )
        st.plotly_chart(fig, use_container_width=True)

    # df.rename({a.})
    # df.columns = ['date','lang','temp_c','pwr','pellet_size','current_start_dose','']

    # st.dataframe(df)
st.write("## Column mapping")
st.json(col_mapping, expanded=False)
