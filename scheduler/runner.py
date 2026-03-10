import random

from scraper.rss_fetcher import fetch_rss_links
from scraper.hackernews_fetcher import fetch_hackernews_links
from scraper.article_scraper import scrape_article_text
from scraper.twitter_fetcher import fetch_trending_ai_tweets
from tweet.tweet_writer import craft_final_tweet
from analysis.insight_generator import generate_quote_tweet
from notification.telegram_sender import send_telegram_message
from notification.twitter_sender import post_tweet

def _output_tweet(tweet_text, source_url, score):
    """Prints the tweet and sends it to Telegram."""
    print("\nTweet generated:\n")
    print(tweet_text)
    if source_url:
        print(f"\nSource: {source_url}")
    print(f"\nQuality Score: {score}/10\n")
    print("-" * 40)

    # Post to Twitter
    posted_url = post_tweet(tweet_text)

    # Send to Telegram
    if posted_url:
        telegram_msg = f"Just posted a new tweet!\n\n{tweet_text}\n\nLive link: {posted_url}"
        send_telegram_message(telegram_msg)
    else:
        send_telegram_message(tweet_text, source_url)

def _try_quote_tweet_path():
    """
    Tries to find a trending AI tweet and generate a quote-tweet response.
    Returns True if successful, False otherwise.
    """
    print("Checking trending AI tweets for quote-tweet ideas...")
    tweets = fetch_trending_ai_tweets(max_accounts=5)

    if not tweets:
        print("No trending tweets found. Skipping quote-tweet path.")
        return False

    for tweet in tweets[:5]:  # Try up to 5 tweets
        original_text = tweet['text']
        original_author = tweet['author']
        tweet_url = tweet['url']

        print(f"Found tweet from @{original_author}: {original_text[:80]}...")

        response = generate_quote_tweet(original_text, original_author)
        if response:
            print(f"\nQuote Tweet Generated:\n")
            print(f"Your response: {response}")
            print(f"Original: @{original_author}: {original_text[:100]}...")
            if tweet_url:
                print(f"Tweet link: {tweet_url}")
            print("-" * 40)

            # Auto-post the quote tweet
            posted_url = post_tweet(response, quote_url=tweet_url)

            if posted_url:
                message = f"Just Quote-Tweeted this!\n\nYour response:\n{response}\n\nLive link: {posted_url}"
                send_telegram_message(message)
            else:
                # Format fallback suggestion if API fails
                message = (
                    f"Quote Tweet Idea (Auto-post failed):\n\n"
                    f"Your response:\n{response}\n\n"
                    f"Original tweet by @{original_author}:\n\"{original_text}\""
                )
                send_telegram_message(message, tweet_url)
            return True

    return False

def run_tweet_pipeline():
    """
    Executes a single run of the tweet engine pipeline.
    Randomly picks one of three paths:
      1. Quote-tweet a trending AI tweet (~30%)
      2. Generate insight from a news article (~40%)
      3. Generate a random engineering thought (~30%)
    """
    print("\n[Job Started] Running tweet pipeline...")

    roll = random.random()

    # Path 1: Quote-tweet (~30% chance)
    if roll < 0.3:
        if _try_quote_tweet_path():
            return
        # If it fails, fall through to article path

    # Path 2: Article-based tweet (~40% chance, or fallback from path 1)
    if roll < 0.7:
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
                    print("Article content too short. Skipping.")
                    continue

                tweet_text, source_url, score = craft_final_tweet(article_url=url, article_text=text)

                if tweet_text:
                    _output_tweet(tweet_text, source_url, score)
                    return
                else:
                    print(f"Quality too low (score: {score}). Trying next...")

    # Path 3: Random thought (30% or fallback)
    print("Generating a random engineering thought...")
    tweet_text, source_url, score = craft_final_tweet(article_url=None, article_text=None)
    if tweet_text:
        _output_tweet(tweet_text, source_url, score)
    else:
        print("Failed to generate any tweet this cycle.")

if __name__ == "__main__":
    run_tweet_pipeline()
