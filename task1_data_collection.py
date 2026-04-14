"""
TrendPulse - Task 1: Fetch Data from API
-----------------------------------------
Fetches top trending stories from HackerNews API,
categorizes them by keywords, and saves to a JSON file.
"""

import requests
import json
import os
import time
from datetime import datetime

# ─────────────────────────────────────────────
# Category keyword mapping (case-insensitive)
# ─────────────────────────────────────────────
CATEGORIES = {
    "technology":    ["ai", "software", "tech", "code", "computer", "data", "cloud", "api", "gpu", "llm"],
    "worldnews":     ["war", "government", "country", "president", "election", "climate", "attack", "global"],
    "sports":        ["nfl", "nba", "fifa", "sport", "game", "team", "player", "league", "championship"],
    "science":       ["research", "study", "space", "physics", "biology", "discovery", "nasa", "genome"],
    "entertainment": ["movie", "film", "music", "netflix", "game", "book", "show", "award", "streaming"],
}

# Maximum stories to collect per category
MAX_PER_CATEGORY = 25

# Header required by HackerNews API
HEADERS = {"User-Agent": "TrendPulse/1.0"}


def assign_category(title: str) -> str:
    """
    Assigns a category to a story based on keyword matches in the title.
    Returns the matched category name, or None if no keywords match.
    """
    title_lower = title.lower()
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            # Match whole-word style: check if keyword appears in title
            if keyword in title_lower:
                return category
    return None  # Story doesn't fit any category


def fetch_top_story_ids() -> list:
    """
    Fetches the list of top story IDs from HackerNews.
    Returns first 500 IDs.
    """
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    print("Fetching top story IDs from HackerNews...")
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        story_ids = response.json()
        print(f"  → Retrieved {len(story_ids)} story IDs. Using first 500.")
        return story_ids[:500]
    except requests.RequestException as e:
        print(f"  ✗ Failed to fetch story IDs: {e}")
        return []


def fetch_story_details(story_id: int) -> dict:
    """
    Fetches details of a single story by its ID.
    Returns the story object as a dict, or None on failure.
    """
    url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"  ✗ Could not fetch story {story_id}: {e}")
        return None


def collect_stories(story_ids: list) -> list:
    """
    Iterates through story IDs, fetches each story's details,
    assigns a category, and collects up to 25 stories per category.

    Waits 2 seconds between each category's processing loop (not per story).
    Returns a list of collected story dicts.
    """
    # Track how many stories we've collected per category
    category_counts = {cat: 0 for cat in CATEGORIES}
    collected_stories = []

    # Group story IDs by category first, processing each category in a loop
    # As required: time.sleep(2) once per category loop, not per story fetch
    print("\nCollecting stories by category...")

    for category in CATEGORIES:
        print(f"\n  Processing category: [{category}]")

        for story_id in story_ids:
            # Stop if we've already collected enough for this category
            if category_counts[category] >= MAX_PER_CATEGORY:
                break

            # Fetch story details
            story = fetch_story_details(story_id)

            # Skip if fetch failed or story has no title
            if not story or "title" not in story:
                continue

            title = story.get("title", "")
            assigned_cat = assign_category(title)

            # Only collect this story if it belongs to the current category
            if assigned_cat == category:
                # Extract required fields
                record = {
                    "post_id":      story.get("id"),
                    "title":        title,
                    "category":     assigned_cat,
                    "score":        story.get("score", 0),
                    "num_comments": story.get("descendants", 0),
                    "author":       story.get("by", "unknown"),
                    "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                collected_stories.append(record)
                category_counts[category] += 1

        print(f"  ✓ Collected {category_counts[category]} stories for [{category}]")

        # Wait 2 seconds between category loops (as required)
        time.sleep(2)

    return collected_stories


def save_to_json(stories: list) -> str:
    """
    Saves collected stories to a JSON file inside the data/ folder.
    Filename format: data/trends_YYYYMMDD.json
    Returns the file path.
    """
    # Create data/ folder if it doesn't exist
    os.makedirs("data", exist_ok=True)

    # Build filename with today's date
    date_str = datetime.now().strftime("%Y%m%d")
    file_path = f"data/trends_{date_str}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(stories, f, indent=2, ensure_ascii=False)

    return file_path


def main():
    print("=" * 50)
    print("  TrendPulse — Task 1: Data Collection")
    print("=" * 50)

    # Step 1: Get top story IDs
    story_ids = fetch_top_story_ids()
    if not story_ids:
        print("No story IDs fetched. Exiting.")
        return

    # Step 2: Collect stories across all categories
    stories = collect_stories(story_ids)

    # Step 3: Save to JSON file
    file_path = save_to_json(stories)

    # Final summary
    print("\n" + "=" * 50)
    print(f"  Collected {len(stories)} stories. Saved to {file_path}")
    print("=" * 50)


if __name__ == "__main__":
    main()
