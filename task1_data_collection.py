import requests
import json
import os
from datetime import datetime
import time

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────
HEADERS = {"User-Agent": "TrendPulse/1.0"}
TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{id}.json"

MAX_PER_CATEGORY = 25  # Collect up to 25 stories per category (125 total)
FETCH_LIMIT = 500      # Fetch the first 500 top story IDs

# ──────────────────────────────────────────────
# Category keyword mapping (case-insensitive)
# ──────────────────────────────────────────────
CATEGORIES = {
    "technology":    ["ai", "software", "tech", "code", "computer", "data", "cloud", "api", "gpu", "llm"],
    "worldnews":     ["war", "government", "country", "president", "election", "climate", "attack", "global"],
    "sports":        ["nfl", "nba", "fifa", "sport", "game", "team", "player", "league", "championship"],
    "science":       ["research", "study", "space", "physics", "biology", "discovery", "nasa", "genome"],
    "entertainment": ["movie", "film", "music", "netflix", "game", "book", "show", "award", "streaming"],
}

def assign_category(title: str) -> str | None:
    """
    Check the story title against each category's keywords.
    Returns the first matching category name, or None if no match.
    """
    title_lower = title.lower()
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword in title_lower:
                return category
    return None  # No category matched


def fetch_top_story_ids() -> list[int]:
    """Fetch the top 500 story IDs from HackerNews."""
    print("Fetching top story IDs...")
    try:
        response = requests.get(TOP_STORIES_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        ids = response.json()
        print(f"  → Retrieved {len(ids)} story IDs. Using first {FETCH_LIMIT}.")
        return ids[:FETCH_LIMIT]
    except requests.RequestException as e:
        print(f"  ✗ Failed to fetch story IDs: {e}")
        return []


def fetch_story(story_id: int) -> dict | None:
    """Fetch a single story's details by its ID."""
    url = ITEM_URL.format(id=story_id)
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"  ✗ Failed to fetch story {story_id}: {e}")
        return None  # Don't crash — just skip this story


def collect_stories(story_ids: list[int]) -> list[dict]:
    """
    Iterate through story IDs and collect up to MAX_PER_CATEGORY stories
    per category. Sleeps 2 seconds between category quota fills.
    """
    collected = {cat: [] for cat in CATEGORIES}  # Track stories per category
    collected_at = datetime.now().isoformat()      # Single timestamp for the run

    print("\nCollecting stories by category...")

    for story_id in story_ids:
        # Stop early if all categories are full
        if all(len(v) >= MAX_PER_CATEGORY for v in collected.values()):
            print("  ✓ All categories full. Stopping early.")
            break

        story = fetch_story(story_id)
        if not story:
            continue  # Skip failed requests

        title = story.get("title", "")
        if not title:
            continue  # Skip stories without a title

        category = assign_category(title)
        if not category:
            continue  # Skip uncategorised stories

        if len(collected[category]) >= MAX_PER_CATEGORY:
            continue  # This category is already full

        # Extract required fields
        record = {
            "post_id":      story.get("id"),
            "title":        title,
            "category":     category,
            "score":        story.get("score", 0),
            "num_comments": story.get("descendants", 0),
            "author":       story.get("by", ""),
            "collected_at": collected_at,
        }
        collected[category].append(record)

        # Sleep 2 seconds each time a category just reached its quota
        if len(collected[category]) == MAX_PER_CATEGORY:
            print(f"  ✓ '{category}' complete ({MAX_PER_CATEGORY} stories). Sleeping 2s...")
            time.sleep(2)

    # Flatten all categories into a single list
    all_stories = [story for stories in collected.values() for story in stories]

    # Print a summary
    print("\nCollection summary:")
    for cat, stories in collected.items():
        print(f"  {cat:15s}: {len(stories)} stories")

    return all_stories


def save_to_json(stories: list[dict]) -> str:
    """Save the collected stories to data/trends_YYYYMMDD.json."""
    # Create the data/ folder if it doesn't exist
    os.makedirs("data", exist_ok=True)

    filename = f"data/trends_{datetime.now().strftime('%Y%m%d')}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(stories, f, indent=2, ensure_ascii=False)

    return filename


# ──────────────────────────────────────────────
# Main entry point
# ──────────────────────────────────────────────
if __name__ == "__main__":
    # Step 1: Get top story IDs
    story_ids = fetch_top_story_ids()

    if not story_ids:
        print("No story IDs fetched. Exiting.")
        exit(1)

    # Step 2: Collect stories across all categories
    stories = collect_stories(story_ids)

    # Step 3: Save to JSON
    output_file = save_to_json(stories)
    print(f"\nCollected {len(stories)} stories. Saved to {output_file}")
