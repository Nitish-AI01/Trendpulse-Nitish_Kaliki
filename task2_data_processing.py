import pandas as pd
import json
import glob
import os

# ──────────────────────────────────────────────
# Step 1 — Load the JSON File (4 marks)
# ──────────────────────────────────────────────

# Find the JSON file in the data/ folder (e.g. data/trends_20240115.json)
json_files = glob.glob("data/trends_*.json")

if not json_files:
    print("No trends JSON file found in data/ folder. Please run task1 first.")
    exit(1)

# Use the most recently created file if multiple exist
json_file = sorted(json_files)[-1]

# Load JSON into a Pandas DataFrame
with open(json_file, "r", encoding="utf-8") as f:
    raw_data = json.load(f)

df = pd.DataFrame(raw_data)
print(f"Loaded {len(df)} stories from {json_file}")

# ──────────────────────────────────────────────
# Step 2 — Clean the Data (10 marks)
# ──────────────────────────────────────────────

# --- Remove duplicates based on post_id ---
before = len(df)
df = df.drop_duplicates(subset="post_id")
print(f"\nAfter removing duplicates: {len(df)}")

# --- Drop rows where post_id, title, or score is missing ---
df = df.dropna(subset=["post_id", "title", "score"])
print(f"After removing nulls: {len(df)}")

# --- Fix data types: score and num_comments must be integers ---
df["score"] = pd.to_numeric(df["score"], errors="coerce").astype("Int64")
df["num_comments"] = pd.to_numeric(df["num_comments"], errors="coerce").fillna(0).astype("Int64")

# Drop any rows where score became NaN after coercion
df = df.dropna(subset=["score"])

# --- Remove low quality stories: score less than 5 ---
df = df[df["score"] >= 5]
print(f"After removing low scores: {len(df)}")

# --- Strip extra whitespace from the title column ---
df["title"] = df["title"].str.strip()

# Print total rows remaining after all cleaning steps
print(f"\nRows remaining after cleaning: {len(df)}")

# ──────────────────────────────────────────────
# Step 3 — Save as CSV (6 marks)
# ──────────────────────────────────────────────

output_file = "data/trends_clean.csv"

# Save cleaned DataFrame to CSV (no index column)
df.to_csv(output_file, index=False, encoding="utf-8")
print(f"\nSaved {len(df)} rows to {output_file}")

# --- Print a summary: stories per category ---
print("\nStories per category:")
category_counts = df["category"].value_counts()
for category, count in category_counts.items():
    print(f"  {category:<15} {count}")
