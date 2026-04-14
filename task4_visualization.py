import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

# ──────────────────────────────────────────────
# Step 1 — Setup (2 marks)
# ──────────────────────────────────────────────

# Load the analysed CSV from Task 3
df = pd.read_csv("data/trends_analysed.csv")
print(f"Loaded data: {df.shape}")

# Create outputs/ folder if it doesn't exist
os.makedirs("outputs", exist_ok=True)

# ──────────────────────────────────────────────
# Chart 1 — Top 10 Stories by Score (6 marks)
# ──────────────────────────────────────────────

# Sort by score descending and take the top 10
top10 = df.nlargest(10, "score").copy()

# Shorten titles longer than 50 characters for readability on y-axis
top10["short_title"] = top10["title"].apply(
    lambda t: t[:47] + "..." if len(t) > 50 else t
)

fig1, ax1 = plt.subplots(figsize=(10, 6))

# Horizontal bar chart — stories on y-axis, score on x-axis
ax1.barh(top10["short_title"], top10["score"], color="steelblue")

# Invert y-axis so the highest score appears at the top
ax1.invert_yaxis()

ax1.set_title("Top 10 Stories by Score", fontsize=14, fontweight="bold")
ax1.set_xlabel("Score (Upvotes)")
ax1.set_ylabel("Story Title")
plt.tight_layout()

# Save before show (as required)
plt.savefig("outputs/chart1_top_stories.png", dpi=150)
print("Saved: outputs/chart1_top_stories.png")
plt.close(fig1)  # Close figure to free memory

# ──────────────────────────────────────────────
# Chart 2 — Stories per Category (6 marks)
# ──────────────────────────────────────────────

# Count stories per category
category_counts = df["category"].value_counts()

# Use a distinct colour for each bar
colours = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2"]

fig2, ax2 = plt.subplots(figsize=(8, 5))

ax2.bar(category_counts.index, category_counts.values, color=colours)

ax2.set_title("Stories per Category", fontsize=14, fontweight="bold")
ax2.set_xlabel("Category")
ax2.set_ylabel("Number of Stories")

# Add count labels on top of each bar for clarity
for i, count in enumerate(category_counts.values):
    ax2.text(i, count + 0.3, str(count), ha="center", fontsize=11)

plt.tight_layout()
plt.savefig("outputs/chart2_categories.png", dpi=150)
print("Saved: outputs/chart2_categories.png")
plt.close(fig2)

# ──────────────────────────────────────────────
# Chart 3 — Score vs Comments Scatter (6 marks)
# ──────────────────────────────────────────────

# Split data into popular and non-popular using the is_popular column
popular     = df[df["is_popular"] == True]
not_popular = df[df["is_popular"] == False]

fig3, ax3 = plt.subplots(figsize=(9, 6))

# Plot non-popular stories first (background layer)
ax3.scatter(
    not_popular["score"],
    not_popular["num_comments"],
    color="cornflowerblue",
    alpha=0.6,
    label="Not Popular",
    edgecolors="white",
    linewidths=0.5
)

# Plot popular stories on top (foreground layer)
ax3.scatter(
    popular["score"],
    popular["num_comments"],
    color="tomato",
    alpha=0.8,
    label="Popular",
    edgecolors="white",
    linewidths=0.5
)

ax3.set_title("Score vs Comments (Popular vs Not Popular)", fontsize=14, fontweight="bold")
ax3.set_xlabel("Score (Upvotes)")
ax3.set_ylabel("Number of Comments")
ax3.legend(title="is_popular")

plt.tight_layout()
plt.savefig("outputs/chart3_scatter.png", dpi=150)
print("Saved: outputs/chart3_scatter.png")
plt.close(fig3)

# ──────────────────────────────────────────────
# Bonus — Dashboard (3 marks)
# ──────────────────────────────────────────────
# Combine all 3 charts into one figure using subplots(2, 2) layout

fig, axes = plt.subplots(2, 2, figsize=(18, 12))
fig.suptitle("TrendPulse Dashboard", fontsize=18, fontweight="bold", y=1.01)

# --- Panel 1: Top 10 Stories by Score (top-left) ---
axes[0, 0].barh(top10["short_title"], top10["score"], color="steelblue")
axes[0, 0].invert_yaxis()
axes[0, 0].set_title("Top 10 Stories by Score")
axes[0, 0].set_xlabel("Score")
axes[0, 0].set_ylabel("Story Title")

# --- Panel 2: Stories per Category (top-right) ---
axes[0, 1].bar(category_counts.index, category_counts.values, color=colours)
axes[0, 1].set_title("Stories per Category")
axes[0, 1].set_xlabel("Category")
axes[0, 1].set_ylabel("Number of Stories")
for i, count in enumerate(category_counts.values):
    axes[0, 1].text(i, count + 0.2, str(count), ha="center", fontsize=10)

# --- Panel 3: Score vs Comments Scatter (bottom-left) ---
axes[1, 0].scatter(
    not_popular["score"], not_popular["num_comments"],
    color="cornflowerblue", alpha=0.6, label="Not Popular",
    edgecolors="white", linewidths=0.5
)
axes[1, 0].scatter(
    popular["score"], popular["num_comments"],
    color="tomato", alpha=0.8, label="Popular",
    edgecolors="white", linewidths=0.5
)
axes[1, 0].set_title("Score vs Comments")
axes[1, 0].set_xlabel("Score")
axes[1, 0].set_ylabel("Number of Comments")
axes[1, 0].legend(title="is_popular")

# --- Panel 4: Engagement by Category (bottom-right, bonus insight) ---
engagement_by_cat = df.groupby("category")["engagement"].mean().sort_values(ascending=False)
axes[1, 1].bar(engagement_by_cat.index, engagement_by_cat.values, color=colours)
axes[1, 1].set_title("Avg Engagement by Category")
axes[1, 1].set_xlabel("Category")
axes[1, 1].set_ylabel("Avg Engagement (comments per upvote)")

plt.tight_layout()
plt.savefig("outputs/dashboard.png", dpi=150, bbox_inches="tight")
print("Saved: outputs/dashboard.png")
plt.close(fig)

print("\nAll charts saved to outputs/")