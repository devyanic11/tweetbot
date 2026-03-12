## AI Insight Tweet Engine

**An automated tweet engine that turns AI/news articles and trending AI Twitter into opinionated, human-sounding tech tweets – then posts them to X (Twitter) and notifies you on Telegram.**

This project periodically:

- Pulls AI/tech news from RSS feeds and Hacker News
- Scrapes full article content
- Generates an insight-style tweet using Gemini
- Auto‑critiques and rewrites the tweet until it passes a quality bar
- Optionally quote‑tweets trending AI/ML accounts
- Posts to your X (Twitter) account
- Mirrors each tweet to a Telegram chat

It is designed to run **on a GitHub Actions cron schedule** or **locally via `python main.py`**, with an optional **instant `/givetweet` Telegram command** powered by a Cloudflare Worker.

---

### Table of contents

- **Overview**
- **Core features**
- **Architecture**
- **Setup**
  - Local development
  - Environment variables
  - GitHub Actions cron
  - Optional `/givetweet` Telegram webhook
- **Running the engine**
- **Folder structure**
- **Notes & limitations**

---

### Overview

The engine targets an **AI/ML engineer persona on tech Twitter**. Instead of generic AI posts, it focuses on:

- Short, opinionated takes
- Real engineering tradeoffs and observations
- A casual, slightly cynical tone

Tweets are generated and then **reviewed by Gemini itself**; low‑scoring drafts are automatically rewritten until they meet a minimum quality score or the engine gives up for that cycle.

---

### Core features

- **Article‑based insights**
  - Fetches AI/tech stories from:
    - `https://venturebeat.com/category/ai/feed/`
    - `https://www.technologyreview.com/feed/`
    - `https://techcrunch.com/latest/`
  - Scrapes article content and distills it into a single, sharp tweet (not a summary).

- **Random engineering thoughts**
  - When there’s no article or by random choice, generates standalone engineering reflections/observations in a human, texting‑style tone.

- **Quote‑tweets from real AI accounts**
  - Scrapes recent tweets from a curated list of AI/ML accounts.
  - Generates a short quote‑tweet response with your own take.

- **Quality gate**
  - Every tweet is auto‑reviewed on:
    - Hook strength
    - Clarity
    - Insight value
    - Originality
    - “Twitter‑native” tone (no AI clichés)
  - Tweets below the threshold are rewritten up to a few times.

- **Multi‑channel output**
  - Posts to X (Twitter) via the official API.
  - Sends each tweet (and link) to a Telegram chat so you can see or reuse it.

- **Automation‑ready**
  - GitHub Actions workflow to run on a cron schedule throughout the day.
  - Optional Cloudflare Worker + Telegram webhook for instant `/givetweet` commands.

---

### Architecture

- **High‑level flow (Mermaid)**

```mermaid
flowchart LR
    subgraph Trigger
        A[GitHub Actions cron\nor Local python main.py]
        B[Telegram /givetweet\nvia Cloudflare Worker]
    end

    subgraph Pipeline
        C[run_tweet_pipeline()\n(scheduler/runner.py)]
        D{Choose path}
        E[Fetch RSS/HN links\nscraper/rss_fetcher.py\nscraper/hackernews_fetcher.py]
        F[Scrape article text\nscraper/article_scraper.py]
        G[Generate insight\nanalysis/insight_generator.py]
        H[Generate random thought\nanalysis/insight_generator.py]
        I[Fetch trending AI tweets\nscraper/twitter_fetcher.py]
        J[Generate quote tweet\nanalysis/insight_generator.py]
        K[Evaluate & rewrite tweet\ntweet/tweet_writer.py]
    end

    subgraph Outputs
        L[Post to X/Twitter\nnotification/twitter_sender.py]
        M[Send to Telegram\nnotification/telegram_sender.py]
    end

    A --> C
    B --> C

    C --> D
    D -->|Article path| E --> F --> G
    D -->|Random thought| H
    D -->|Quote-tweet| I --> J

    G --> K
    H --> K
    J --> K

    K -->|Final tweet| L
    K -->|Final tweet + link| M
```

- **Entry point**
  - `main.py` – loads environment, then calls `scheduler/runner.py::run_tweet_pipeline()`.

- **Scheduler / pipeline**
  - `scheduler/runner.py`
    - Randomly chooses a path each run:
      1. Quote‑tweet a trending AI tweet (~30%)
      2. Generate an insight from a news article (~40%)
      3. Generate a random engineering thought (~30% or fallback)
    - Routes the chosen idea through the tweet writer and then posts it.

- **Insight generation**
  - `analysis/insight_generator.py`
    - `init_gemini()` – initializes the Gemini client using `GEMINI_API_KEY`.
    - `generate_insight()` – crafts an insight tweet from article text or from scratch.
    - `generate_quote_tweet()` – generates a quote‑tweet style response to an existing tweet.

- **Tweet crafting & quality control**
  - `tweet/tweet_writer.py`
    - `evaluate_tweet()` – asks Gemini to score the tweet on 5 criteria and returns JSON.
    - `rewrite_tweet()` – rewrites the tweet based on critic feedback and optional article context.
    - `craft_final_tweet()` – loops generate → evaluate → (optionally rewrite) until a good tweet or max attempts.

- **Scraping & sources**
  - `scraper/rss_fetcher.py` – pulls article links from RSS and HTML feeds.
  - `scraper/hackernews_fetcher.py` – gets links from Hacker News (not shown above but part of pipeline).
  - `scraper/article_scraper.py` – fetches and cleans full article text.
  - `scraper/twitter_fetcher.py` – scrapes recent tweets from AI/ML accounts via the public syndication endpoint (no auth).

- **Posting & notifications**
  - `notification/twitter_sender.py` – posts tweets using the official Twitter API (tweepy).
  - `notification/telegram_sender.py` – sends final tweets to a Telegram chat via Bot API.

- **Webhooks (optional)**
  - `webhook/worker.js` – Cloudflare Worker that listens to Telegram `/givetweet` and triggers a GitHub Action run.
  - `webhook/SETUP.md` – step‑by‑step guide for deploying the worker and wiring the Telegram webhook.

---

### Setup

#### 1. Local development

Clone the repo and install dependencies:

```bash
git clone <your-fork-url> ai_insight_tweet_engine
cd ai_insight_tweet_engine

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

Create a `.env` file in the project root (same folder as `main.py`).

#### 2. Environment variables

The engine expects these variables either in `.env` (for local) or as GitHub Secrets (for Actions):

- **Gemini**
  - `GEMINI_API_KEY` – API key for `google-genai` / Gemini.

- **Twitter / X API (for posting)**
  - `TWITTER_API_KEY`
  - `TWITTER_API_SECRET`
  - `TWITTER_ACCESS_TOKEN`
  - `TWITTER_ACCESS_TOKEN_SECRET`

- **Telegram Bot**
  - `TELEGRAM_BOT_TOKEN` – Bot token from BotFather.
  - `TELEGRAM_CHAT_ID` – Chat ID where you want messages delivered.

Example `.env`:

```bash
GEMINI_API_KEY=your-gemini-key

TWITTER_API_KEY=your-twitter-api-key
TWITTER_API_SECRET=your-twitter-api-secret
TWITTER_ACCESS_TOKEN=your-access-token
TWITTER_ACCESS_TOKEN_SECRET=your-access-token-secret

TELEGRAM_BOT_TOKEN=123456:ABCDEF...
TELEGRAM_CHAT_ID=123456789
```

If Twitter or Telegram credentials are missing, the code will **log a warning** and skip posting to that channel.

#### 3. GitHub Actions cron (recommended)

This repository includes a workflow at `.github/workflows/tweet_engine.yml` that:

- Runs on a schedule:
  - At minute 30 of hours 3,5,7,9,11,13,15 UTC (`30 3-16/2 * * *`)
- Installs dependencies with Python 3.11
- Runs `python main.py`

To enable it:

1. Fork the repo (or push to your own).
2. In your GitHub repo, go to **Settings → Secrets and variables → Actions → New repository secret**.
3. Add the environment variables listed above as secrets:
   - `GEMINI_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - `TWITTER_API_KEY`
   - `TWITTER_API_SECRET`
   - `TWITTER_ACCESS_TOKEN`
   - `TWITTER_ACCESS_TOKEN_SECRET`
4. Ensure the workflow file is enabled under **Actions**.

You can also trigger it manually via the **“Run workflow”** button (`workflow_dispatch`).

#### 4. Optional: Instant `/givetweet` Telegram command

For near‑instant tweets on demand from Telegram:

1. Read `webhook/SETUP.md` carefully.
2. Deploy the `webhook/worker.js` script as a **Cloudflare Worker**.
3. Configure its environment variables (GitHub token, repo info, Telegram bot info).
4. Set your Telegram webhook to point at the Worker URL.

Once configured, typing `/givetweet` in your Telegram chat will trigger a fresh run (via GitHub) and send you a tweet shortly after.

---

### Running the engine

- **Locally (one‑off)**

```bash
python main.py
```

This runs a single pipeline cycle (one tweet or a logged failure) and exits.

- **Via GitHub Actions**
  - Enabled automatically once secrets are configured and Actions are allowed on the repo.
  - View logs under the **Actions** tab to see how tweets were generated and scored.

---

### Folder structure

High‑level layout:

```text
main.py                  # CLI entry point
requirements.txt

analysis/
  insight_generator.py   # Gemini client + tweet & quote-tweet generation

tweet/
  tweet_writer.py        # Evaluate + rewrite + craft final tweet

scraper/
  rss_fetcher.py         # AI/tech RSS + HTML feeds
  hackernews_fetcher.py  # Hacker News links
  article_scraper.py     # Article text extraction
  twitter_fetcher.py     # Trending AI tweets via syndication

scheduler/
  runner.py              # Orchestrates pipeline paths

notification/
  twitter_sender.py      # Post to Twitter/X (tweepy)
  telegram_sender.py     # Send messages to Telegram
  get_chat_id.py         # Helper script to discover your Telegram chat ID
  check_command.py       # Utility for validating bot commands

webhook/
  worker.js              # Cloudflare Worker for `/givetweet`
  SETUP.md               # Detailed deployment instructions

.github/workflows/
  tweet_engine.yml       # Cron + manual GitHub Action
```

---

### Notes & limitations

- The project relies on external sites (RSS feeds, news sites, Twitter syndication); changes or blocks on those endpoints may break scraping.
- Twitter/X API credentials are required for direct posting; without them, the engine will still generate tweets but won’t publish them.
- Gemini behavior and style can change over time; occasionally adjust prompts if the tone drifts from your preference.
- Always review your first few auto‑tweets in production to ensure they match your personal brand and risk tolerance.

