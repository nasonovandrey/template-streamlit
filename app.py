import os
from clickhouse_driver import Client as ClickHouseClient
import streamlit as st
import numpy as np
import pandas as pd
import time
import matplotlib.cm as cm
import matplotlib.colors as mcolors

pairs = [
    "PEPEUSDT",
    "SHIBUSDT",
    "XECUSDT",
    "VTHOUSDT",
    "LUNCUSDT",
    "FLOKIUSDT",
    "PONDUSDT",
    "DENTUSDT",
    "STMXUSDT",
    "TRXUSDT",
    "LEVERUSDT",
    "GALAUSDT",
    "SPELLUSDT",
    "XVGUSDT",
    "RSRUSDT",
    "AMPUSDT",
    "USTCUSDT",
    "ADADOWNUSDT",
    "VETUSDT",
    "BTCUSDT",
]

clickhouse_password = os.environ.get("clickhouse_password")
if clickhouse_password:
    clickhouse_client = ClickHouseClient(
        host="localhost", port=9000, password=clickhouse_password
    )
else:
    clickhouse_client = ClickHouseClient(host="localhost", port=9000)


def get_dataframe():
    query = f"SELECT symbol, closeTime, closePrice FROM klines WHERE symbol in {tuple(pairs)};"
    df = pd.DataFrame(
        clickhouse_client.execute(query), columns=["symbol", "timestamp", "price"]
    )
    df = pd.pivot_table(df, values="price", columns="symbol", index="timestamp")
    df.rename(columns={pair: pair[:-4] for pair in pairs}, inplace=True)
    return df


def get_color(val):
    # None is used in self-correlation diagonal
    if val is None:
        return "background-color: white"
    # Define the gradient color map function
    norm = mcolors.TwoSlopeNorm(
        vmin=-1, vcenter=0, vmax=1
    )  # Normalize the correlation values to [-1, 1]
    cmap = cm.get_cmap("RdBu_r")
    rgba = cmap(norm(val))
    return f"background-color: {mcolors.to_hex(rgba)}"


def main():
    st.title("Correlation:")

    # Create container for dataframe
    df_container = st.empty()

    while True:
        # Call the get_dataframe function with the selected quote as an argument
        df = get_dataframe()

        # Apply the color map to the correlation dataframe
        corr_df = df.corr()
        np.fill_diagonal(corr_df.values, None)
        df_corr_styled = corr_df.style.applymap(get_color)

        # Display the correlation dataframe with colors
        df_container.write(df_corr_styled)

        # Add a short delay to avoid excessive updates (you can adjust the duration as needed)
        time.sleep(1)


if __name__ == "__main__":
    main()
