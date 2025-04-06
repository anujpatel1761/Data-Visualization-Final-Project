import pandas as pd

# File path
file_path = r"C:\Users\anujp\Desktop\Data-Visualization-Final-Project\data\UserBehavior\user_behavior_sample_data.parquet"

# Load the full dataset
df = pd.read_parquet(file_path)

# Sample 1000 rows
df_sample = df.sample(n=1000000, random_state=42)

# Save the sample
sample_path = r"C:\Users\anujp\Desktop\Data-Visualization-Final-Project\data\UserBehavior\user_behavior_sample_1000000.parquet"
df_sample.to_parquet(sample_path)

print("Sample saved at:", sample_path)
