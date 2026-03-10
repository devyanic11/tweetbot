import sys
import os
from dotenv import load_dotenv

from scheduler.runner import run_tweet_pipeline

def main():
    print("Starting AI Insight Tweet Engine...")

    # Load environment variables from .env (locally) or from env (GitHub Actions)
    load_dotenv()

    if not os.environ.get("GEMINI_API_KEY"):
        print("ERROR: GEMINI_API_KEY is not set.")
        print("Add it to your .env file or set it as a GitHub Secret.")
        sys.exit(1)

    # Run the pipeline once and exit.
    # GitHub Actions cron handles the 2-hour scheduling.
    run_tweet_pipeline()

if __name__ == "__main__":
    main()
