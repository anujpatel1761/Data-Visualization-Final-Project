# testing.py
import pandas as pd
import plotly.io as pio
from components.overview import create_daily_activity_overview

# Optional: set Plotly to open the figure in the browser
pio.renderers.default = "browser"

# Load your real dataset
file_path = "data/UserBehavior/user_behavior_sample_100000.parquet"
df = pd.read_parquet(file_path)

# Ensure 'Timestamp' is in datetime format
if not pd.api.types.is_datetime64_any_dtype(df["Timestamp"]):
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit='s', origin='unix', errors='coerce')

# Generate the figure using your custom function
fig = create_daily_activity_overview(df)

# Show it
fig.show()