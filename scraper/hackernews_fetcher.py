import requests

HN_TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"

def fetch_hackernews_links(limit=15):
    """Fetches top recent links from Hacker News."""
    links = []
    try:
        # Get top story IDs
        response = requests.get(HN_TOP_STORIES_URL, timeout=10)
        response.raise_for_status()
        story_ids = response.json()
        
        # Fetch details for the top N stories
        for story_id in story_ids[:limit]:
            item_response = requests.get(HN_ITEM_URL.format(story_id), timeout=5)
            item_response.raise_for_status()
            item = item_response.json()
            
            # We want articles with external URLs, not HN discussions (Ask HN, etc.)
            if item and item.get('type') == 'story' and 'url' in item:
                links.append(item['url'])
                
    except Exception as e:
        print(f"Error fetching Hacker News links: {e}")
        
    return links

if __name__ == "__main__":
    links = fetch_hackernews_links()
    print(f"Fetched {len(links)} links from Hacker News.")
    for link in links[:5]:
        print("-", link)
