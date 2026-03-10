import os
import tweepy
from dotenv import load_dotenv

def post_tweet(text, quote_url=None):
    """
    Posts a tweet to Twitter using API v2 Free Tier.
    If quote_url is provided, it's appended to the text to create a Quote Tweet.
    Returns the URL of the posted tweet, or None if failed.
    """
    load_dotenv()
    
    api_key = os.environ.get("TWITTER_API_KEY")
    api_secret = os.environ.get("TWITTER_API_SECRET")
    access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")
    
    if not all([api_key, api_secret, access_token, access_token_secret]):
        print("WARNING: Twitter API credentials missing. Skipping Twitter post.")
        return None
        
    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )
    
    # Twitter automatically turns a tweet URL at the end of the text into a Quote Tweet
    final_text = text
    if quote_url:
        final_text = f"{text}\n\n{quote_url}"
        
    print("Sending to Official Twitter API...")
    
    # Retry logic for 503 / 429 limits
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.create_tweet(text=final_text)
            tweet_id = response.data['id']
            
            tweet_url = f"https://x.com/i/web/status/{tweet_id}"
            print(f"Successfully posted to Twitter! URL: {tweet_url}")
            return tweet_url
            
        except tweepy.errors.TweepyException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 10
                print(f"Waiting {wait_time} seconds before retrying...")
                import time
                time.sleep(wait_time)
            else:
                print("All retries failed.")
                return None
    return None
