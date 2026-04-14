"""
TrendPulse - Task 2: Clean CSV
--------------------------------
Loads the JSON file produced by Task 1,
cleans and validates the data, then saves
it as a structured CSV file for Task 3.
"""

import json
import csv
import os
import glob
from datetime import datetime


# ─────────────────────────────────────────────
# Expected fields in every story record
# ─────────────────────────────────────────────
REQUIRED_FIELDS = ["post_id", "title", "category", "score", "num_comments", "author", "collected_at"]

VALID_CATEGORIES = {"technology", "worldnews", "sports", "science", "entertainment"}


def find_latest_json() -> str:
    """
    Finds the most recently created trends JSON file in the data/ folder.
    Returns the file path, or None if no file is found.
    """
    files = glob.glob("data/trends_*.json")
    if not files:
        return None
    # Sort by filename (date is embedded), pick the latest
    latest = sorted(files)[-1]
    return latest


def load_json(file_path: str) -> list:
    """
    Loads and returns the list of stories from a JSON file.
    """
    print(f"Loading data from: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"  → {len(data)} raw records loaded.")
    return data


def clean_stories(raw_stories: list) -> list:
    """
    Cleans and validates each story record.

    Cleaning steps:
    1. Remove records missing any required field
    2. Strip whitespace from string fields
    3. Replace missing/null score or num_comments with 0
    4. Ensure score and num_comments are integers
    5. Remove duplicate post_ids (keep first occurrence)
    6. Validate category is one of the 5 known categories
    7. Ensure title is not empty after stripping
    """
    cleaned = []
    seen_ids = set()       # Track post_ids to remove duplicates
    removed_missing = 0
    removed_duplicate = 0
    removed_bad_category = 0
    removed_empty_title = 0

    for story in raw_stories:

        # Step 1: Check all required fields exist in the record
        if not all(field in story for field in REQUIRED_FIELDS):
            removed_missing += 1
            continue

        # Step 2: Strip whitespace from string fields
        story["title"]        = str(story["title"]).strip()
        story["category"]     = str(story["category"]).strip().lower()
        story["author"]       = str(story["author"]).strip()
        story["collected_at"] = str(story["collected_at"]).strip()

        # Step 3 & 4: Ensure score and num_comments are valid integers
        try:
            story["score"]        = int(story["score"]) if story["score"] is not None else 0
            story["num_comments"] = int(story["num_comments"]) if story["num_comments"] is not None else 0
        except (ValueError, TypeError):
            story["score"]        = 0
            story["num_comments"] = 0

        # Step 5: Remove duplicates by post_id
        post_id = story["post_id"]
        if post_id in seen_ids:
            removed_duplicate += 1
            continue
        seen_ids.add(post_id)

        # Step 6: Validate category
        if story["category"] not in VALID_CATEGORIES:
            removed_bad_category += 1
            continue

        # Step 7: Skip stories with empty titles
        if not story["title"]:
            removed_empty_title += 1
            continue

        cleaned.append(story)

    # Print cleaning summary
    print(f"\n  Cleaning Summary:")
    print(f"    Removed (missing fields)   : {removed_missing}")
    print(f"    Removed (duplicate IDs)    : {removed_duplicate}")
    print(f"    Removed (invalid category) : {removed_bad_category}")
    print(f"    Removed (empty title)      : {removed_empty_title}")
    print(f"    ─────────────────────────────")
    print(f"    Clean records remaining    : {len(cleaned)}")

    return cleaned


def save_to_csv(stories: list) -> str:
    """
    Saves the cleaned stories to a CSV file inside the data/ folder.
    Filename format: data/trends_clean_YYYYMMDD.csv
    Returns the file path.
    """
    os.makedirs("data", exist_ok=True)

    date_str = datetime.now().strftime("%Y%m%d")
    file_path = f"data/trends_clean_{date_str}.csv"

    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=REQUIRED_FIELDS)
        writer.writeheader()          # Write column headers
        writer.writerows(stories)     # Write all cleaned story rows

    return file_path


def print_category_breakdown(stories: list):
    """
    Prints a breakdown of how many stories exist per category
    in the cleaned dataset.
    """
    counts = {}
    for story in stories:
        cat = story["category"]
        counts[cat] = counts.get(cat, 0) + 1

    print("\n  Stories per category:")
    for cat, count in sorted(counts.items()):
        print(f"    {cat:<15} : {count}")


def main():
    print("=" * 50)
    print("  TrendPulse — Task 2: Data Cleaning")
    print("=" * 50)

    # Step 1: Find the latest JSON file from Task 1
    json_file = find_latest_json()
    if not json_file:
        print("  ✗ No trends JSON file found in data/ folder.")
        print("    Please run task1_data_collection.py first.")
        return

    # Step 2: Load raw data
    raw_stories = load_json(json_file)

    # Step 3: Clean the data
    print("\nCleaning data...")
    clean = clean_stories(raw_stories)

    # Step 4: Show category breakdown
    print_category_breakdown(clean)

    # Step 5: Save to CSV
    csv_file = save_to_csv(clean)

    # Final summary
    print("\n" + "=" * 50)
    print(f"  {len(clean)} clean stories saved to {csv_file}")
    print("=" * 50)


if __name__ == "__main__":
    main()
