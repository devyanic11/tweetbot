/*
 * Cloudflare Worker: Telegram → GitHub Actions instant trigger
 * (Service Worker syntax — paste directly into Cloudflare dashboard)
 *
 * After pasting, go to Settings → Variables and add:
 *   TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, GITHUB_PAT, GITHUB_OWNER, GITHUB_REPO
 */

addEventListener("fetch", (event) => {
    event.respondWith(handleRequest(event.request));
});

async function handleRequest(request) {
    if (request.method !== "POST") {
        return new Response("OK", { status: 200 });
    }

    try {
        const body = await request.json();
        const message = body && body.message;

        if (!message || !message.text) {
            return new Response("OK", { status: 200 });
        }

        const chatId = String(message.chat.id);
        const text = message.text.trim().toLowerCase();

        // Only respond to /givetweet from the correct chat
        if (text !== "/givetweet" || chatId !== TELEGRAM_CHAT_ID) {
            return new Response("OK", { status: 200 });
        }

        // Send "on it" reply to Telegram
        await fetch("https://api.telegram.org/bot" + TELEGRAM_BOT_TOKEN + "/sendMessage", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ chat_id: chatId, text: "On it! Triggering tweet generation now..." })
        });

        // Trigger GitHub Actions workflow
        var ghUrl = "https://api.github.com/repos/" + GITHUB_OWNER + "/" + GITHUB_REPO + "/actions/workflows/tweet_engine.yml/dispatches";
        var ghRes = await fetch(ghUrl, {
            method: "POST",
            headers: {
                "Authorization": "Bearer " + GITHUB_PAT,
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "TweetBot-Worker"
            },
            body: JSON.stringify({ ref: "main" })
        });

        if (ghRes.status === 204) {
            await fetch("https://api.telegram.org/bot" + TELEGRAM_BOT_TOKEN + "/sendMessage", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ chat_id: chatId, text: "Workflow triggered! Tweet incoming in ~1-2 minutes." })
            });
        } else {
            await fetch("https://api.telegram.org/bot" + TELEGRAM_BOT_TOKEN + "/sendMessage", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ chat_id: chatId, text: "Failed to trigger workflow. Check GitHub PAT." })
            });
        }

        return new Response("OK", { status: 200 });
    } catch (err) {
        return new Response("Error: " + err.message, { status: 500 });
    }
}
