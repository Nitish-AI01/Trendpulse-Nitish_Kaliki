import pandas as pd
import numpy as np

# ──────────────────────────────────────────────
# Step 1 — Load and Explore (4 marks)
# ──────────────────────────────────────────────

# Load the cleaned CSV from Task 2
df = pd.read_csv("data/trends_clean.csv")

# Print shape: (rows, columns)
print(f"Loaded data: {df.shape}")

# Print the first 5 rows for a quick look
print("\nFirst 5 rows:")
print(df[["post_id", "title", "category", "score", "num_comments"]].head())

# Print average score and average num_comments across all stories
avg_score    = df["score"].mean()
avg_comments = df["num_comments"].mean()
print(f"\nAverage score   : {avg_score:,.3f}")
print(f"Average comments: {avg_comments:,.3f}")

# ──────────────────────────────────────────────
# Step 2 — Basic Analysis with NumPy (8 marks)
# ──────────────────────────────────────────────

scores = df["score"].to_numpy()  # Convert to NumPy array for stats

print("\n--- NumPy Stats ---")

# Mean, median, and standard deviation of score
mean_score   = np.mean(scores)
median_score = np.median(scores)
std_score    = np.std(scores)
max_score    = np.max(scores)
min_score    = np.min(scores)

print(f"Mean score   : {mean_score:,.3f}")
print(f"Median score : {median_score:,.3f}")
print(f"Std deviation: {std_score:,.3f}")
print(f"Max score    : {max_score:,.0f}")
print(f"Min score    : {min_score:,.0f}")

# Which category has the most stories?
top_category       = df["category"].value_counts().idxmax()
top_category_count = df["category"].value_counts().max()
print(f"\nMost stories in: {top_category} ({top_category_count} stories)")

# Which story has the most comments? Print its title and comment count.
most_commented_idx   = df["num_comments"].idxmax()
most_commented_title = df.loc[most_commented_idx, "title"]
most_commented_count = df.loc[most_commented_idx, "num_comments"]
print(f'\nMost commented story: "{most_commented_title}" — {most_commented_count:,} comments')

# ──────────────────────────────────────────────
# Step 3 — Add New Columns (5 marks)
# ──────────────────────────────────────────────

# engagement = num_comments / (score + 1)
# Measures how much discussion a story generates per upvote
# Adding 1 to score avoids division-by-zero
df["engagement"] = df["num_comments"] / (df["score"] + 1)

# is_popular = True if score > average score, else False
# Uses the mean we already calculated above
df["is_popular"] = df["score"] > avg_score

print(f"\nNew columns added:")
print(f"  engagement  — sample values: {df['engagement'].head(3).round(3).tolist()}")
print(f"  is_popular  — True: {df['is_popular'].sum()}, False: {(~df['is_popular']).sum()}")

# ──────────────────────────────────────────────
# Step 4 — Save the Result (3 marks)
# ──────────────────────────────────────────────

output_file = "data/trends_analysed.csv"

# Save the updated DataFrame (now with engagement and is_popular columns)
df.to_csv(output_file, index=False, encoding="utf-8")
print(f"\nSaved to {output_file}")