"""
This is a simple Streamlit app that loads a dataset of Uber pickups in New York City and
visualizes them on a map.
"""

import ssl
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk


ssl._create_default_https_context = ssl._create_unverified_context


st.title("Uber pickups in NYC")


DATE_COLUMN = "date/time"
DATA_URL = (
    "https://s3-us-west-2.amazonaws.com/streamlit-demo-data/uber-raw-data-sep14.csv.gz"
)


@st.cache_data
def load_data(nrows):
    """
    Load data from a CSV file, process it, and return a DataFrame.

    Parameters:
    nrows (int): Number of rows of data to read from the CSV file.

    Returns:
    pandas.DataFrame: Processed data with lowercase column names and datetime conversion for the specified date column.
    """
    print("Loading data...")
    data_csv = pd.read_csv(DATA_URL, nrows=nrows)

    lowercase = lambda x: str(x).lower()
    data_csv.rename(lowercase, axis="columns", inplace=True)
    data_csv[DATE_COLUMN] = pd.to_datetime(data_csv[DATE_COLUMN])
    return data_csv


if "counter" not in st.session_state:
    st.session_state.counter = 0

st.session_state.counter += 1
# st.text(f"This page has run {st.session_state.counter} times.")


data_load_state = st.text("Loading data...")
data = load_data(10000)
data_load_state.text("Done! (using st.cache_data)")


if st.checkbox("Show raw data"):
    st.subheader("Raw data")
    st.write(data)


st.subheader("Number of pickups by hour")
hist_values = np.histogram(data[DATE_COLUMN].dt.hour, bins=24, range=(0, 24))[0]

st.bar_chart(hist_values)

hour_to_filter = st.slider("Select hour of pickup", 0, 23, 17)
filterd_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]
st.subheader(f"Map of all pickups at {hour_to_filter}:00")
# st.map(filterd_data)
st.pydeck_chart(
    pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(
            latitude=filterd_data["lat"].mean(),
            longitude=filterd_data["lon"].mean(),
            zoom=11,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                "HexagonLayer",
                data=filterd_data,
                get_position="[lon, lat]",
                radius=200,
                elevation_scale=4,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
            ),
            pdk.Layer(
                "ScatterplotLayer",
                data=filterd_data,
                get_position="[lon, lat]",
                get_color="[200, 30, 0, 160]",
                get_radius=200,
            ),
        ],
    )
)
