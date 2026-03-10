import random

from scraper.rss_fetcher import fetch_rss_links
from scraper.hackernews_fetcher import fetch_hackernews_links
from scraper.article_scraper import scrape_article_text
from tweet.tweet_writer import craft_final_tweet
from notification.telegram_sender import send_telegram_message

def _output_tweet(tweet_text, source_url, score):
    """Prints the tweet and sends it to Telegram."""
    print("\nTweet generated:\n")
    print(tweet_text)
    if source_url:
        print(f"\nSource: {source_url}")
    print(f"\nQuality Score: {score}/10\n")
    print("-" * 40)

    # Send to Telegram
    send_telegram_message(tweet_text, source_url)

def run_tweet_pipeline():
    """
    Executes a single run of the tweet engine pipeline:
    1. Decide whether to use an article or just generate a thought directly.
    2. Try fetching and scraping if decided.
    3. Generate, validate, output, and send to Telegram.
    """
    print("\n[Job Started] Running tweet pipeline...")

    # 50% chance to just generate a random thought without an article
    if random.random() < 0.5:
        print("Generating a random engineering thought (no article).")
        tweet_text, source_url, score = craft_final_tweet(article_url=None, article_text=None)
        if tweet_text:
            _output_tweet(tweet_text, source_url, score)
            return

    # If we are here, we are trying with an article
    print("Fetching articles for inspiration...")

    rss_links = fetch_rss_links()
    hn_links = fetch_hackernews_links(limit=10)

    all_links = rss_links + hn_links
    if all_links:
        random.shuffle(all_links)

        for url in all_links:
            print(f"Trying article: {url}")

            text = scrape_article_text(url)
            if len(text) < 100:
                print("Article content too short or failed to scrape. Skipping.")
                continue

            tweet_text, source_url, score = craft_final_tweet(article_url=url, article_text=text)

            if tweet_text:
                _output_tweet(tweet_text, source_url, score)
                return
            else:
                print(f"Failed to generate quality tweet (score: {score}). Trying next...")

    # Fallback: generate without an article
    print("Falling back to random thought...")
    tweet_text, source_url, score = craft_final_tweet(article_url=None, article_text=None)
    if tweet_text:
        _output_tweet(tweet_text, source_url, score)
    else:
        print("Failed to generate any tweet this cycle.")

if __name__ == "__main__":
    run_tweet_pipeline()
