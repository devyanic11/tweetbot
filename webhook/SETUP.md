# Instant `/givetweet` Trigger — Setup Guide

This sets up an **instant** Telegram command trigger using a free **Cloudflare Worker**.
When you type `/givetweet` in Telegram, the tweet arrives in ~1-2 minutes.

---

## Step 1: Create a GitHub Personal Access Token

1. Go to **https://github.com/settings/tokens** → **Generate new token (classic)**
2. Give it a name like `tweetbot-trigger`
3. Select scope: **`repo`** (full control of private repos)
4. Click **Generate token** → copy it

---

## Step 2: Deploy the Cloudflare Worker

1. Go to **https://dash.cloudflare.com** → sign up (free)
2. Click **Workers & Pages** → **Create Worker**
3. Give it a name like `tweetbot-webhook`
4. **Replace** all the default code with the contents of `webhook/worker.js`
5. Click **Deploy**
6. Go to **Settings → Variables** for your worker and add these:

| Variable Name | Value |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID |
| `GITHUB_PAT` | The GitHub token from Step 1 |
| `GITHUB_OWNER` | `devyanic11` |
| `GITHUB_REPO` | `tweetbot` |

7. Copy your **Worker URL** (looks like `https://tweetbot-webhook.YOUR_SUBDOMAIN.workers.dev`)

---

## Step 3: Set the Telegram Webhook

Run this command (replace the URL with your actual Worker URL):

```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://tweetbot-webhook.YOUR_SUBDOMAIN.workers.dev"
```

You should see: `{"ok":true,"result":true,"description":"Webhook was set"}`

---

## Done!

Now type `/givetweet` in your Telegram chat with the bot.
You'll get an instant reply + a tweet within 1-2 minutes.
