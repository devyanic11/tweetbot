import requests
from bs4 import BeautifulSoup
import random

# Popular AI/ML accounts to follow for trending tweets
AI_TWITTER_ACCOUNTS = [
    "kaborobotics",
    "ylecun",
    "AndrewYNg",
    "demaborobotics",
    "hardmaru",
    "goodaborobotics",
    "jimaborobotics",
    "kaaborobotics",
    "svpino",
    "EMostaque",
]

# AI/ML search terms to find trending discussion
AI_SEARCH_TERMS = [
    "AI engineering",
    "machine learning production",
    "LLM inference",
    "AI infrastructure",
    "RAG pipeline",
    "AI agents",
    "model deployment",
    "MLOps",
    "fine tuning LLM",
    "AI startups",
]

SYNDICATION_URL = "https://syndication.twitter.com/srv/timeline-profile/screen-name/{username}"

def fetch_tweets_from_account(username):
    """
    Fetches recent tweets from a Twitter account using the syndication embed endpoint.
    This is free and doesn't require authentication.
    Returns a list of dicts with 'text' and 'url'.
    """
    tweets = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        url = SYNDICATION_URL.format(username=username)
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # The syndication page renders tweets in timeline-Tweet containers
        for tweet_div in soup.find_all('div', class_='timeline-Tweet'):
            text_el = tweet_div.find('p', class_='timeline-Tweet-text')
            link_el = tweet_div.find('a', class_='timeline-Tweet-timestamp')

            if text_el:
                tweet_text = text_el.get_text(strip=True)
                tweet_url = ""
                if link_el and link_el.get('href'):
                    tweet_url = link_el['href']
                    if not tweet_url.startswith('http'):
                        tweet_url = f"https://twitter.com{tweet_url}"

                if len(tweet_text) > 30:  # Skip very short tweets
                    tweets.append({
                        'text': tweet_text,
                        'url': tweet_url,
                        'author': username
                    })

    except Exception as e:
        # Silently skip — syndication endpoint may not work for all accounts
        pass

    return tweets

def fetch_trending_ai_tweets(max_accounts=5):
    """
    Fetches recent AI/ML tweets from a random sample of popular accounts.
    Returns a list of tweet dicts.
    """
    selected = random.sample(AI_TWITTER_ACCOUNTS, min(max_accounts, len(AI_TWITTER_ACCOUNTS)))
    all_tweets = []

    for username in selected:
        tweets = fetch_tweets_from_account(username)
        all_tweets.extend(tweets)

    if all_tweets:
        random.shuffle(all_tweets)

    return all_tweets

if __name__ == "__main__":
    tweets = fetch_trending_ai_tweets()
    print(f"Found {len(tweets)} tweets")
    for t in tweets[:5]:
        print(f"\n@{t['author']}: {t['text'][:100]}...")
        print(f"  Link: {t['url']}")
