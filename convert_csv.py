import pandas as pd
from tqdm import tqdm

# Define file paths
parquet_file = r"C:\Users\anujp\Desktop\Data-Visualization-Final-Project\data\user_behavior_sample_data.parquet"
csv_file = r"C:\Users\anujp\Desktop\Data-Visualization-Final-Project\data\user_behavior_sample_data.csv"

# Read the Parquet file
df = pd.read_parquet(parquet_file)

# Open the CSV file and write with progress tracking
with open(csv_file, "w", encoding="utf-8", newline="") as f:
    df.head(0).to_csv(f, index=False)  # Write headers
    chunk_size = 10000  # Adjust chunk size based on memory
    total_chunks = len(df) // chunk_size + (1 if len(df) % chunk_size != 0 else 0)

    for i in tqdm(range(0, len(df), chunk_size), desc="Converting", unit="chunk"):
        df.iloc[i:i + chunk_size].to_csv(f, header=False, index=False)

print(f"✅ Conversion complete! CSV saved at: {csv_file}")
