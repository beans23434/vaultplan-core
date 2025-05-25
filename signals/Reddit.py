import typer
import json
from pathlib import Path
from datetime import datetime, timedelta
import requests
import time

app = typer.Typer()

CONFIG_PATH = Path.home() / "vaultplan" / "config.json"
SIGNAL_PATH = Path.home() / "vaultplan" / "signals" / "reddit"
SIGNAL_PATH.mkdir(parents=True, exist_ok=True)

REDDIT_HEADERS = {
    "User-Agent": "VaultPlanRedditScraper/1.0"
}

# Load config
with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)

SUBREDDITS = CONFIG.get("reddit_subreddits", ["CryptoCurrency", "finance"])
KEYWORDS = CONFIG.get("reddit_keywords", ["btc", "eth", "degen", "crypto", "inflation"])
ENABLED = CONFIG.get("reddit_enabled", False)

@app.command("reddit-toggle")
def toggle(enable: bool):
    CONFIG["reddit_enabled"] = enable
    with open(CONFIG_PATH, "w") as f:
        json.dump(CONFIG, f, indent=2)
    typer.echo(f"Reddit signal collection {'enabled' if enable else 'disabled'}.")

@app.command("reddit-summary")
def reddit_summary():
    today = datetime.utcnow().strftime("%Y-%m-%d")
    file = SIGNAL_PATH / f"reddit_daily_{today}.json"
    if file.exists():
        with open(file) as f:
            data = json.load(f)
    else:
        typer.echo("No summary found for today.")
        raise typer.Exit()

    typer.echo(json.dumps(data, indent=2))

@app.command("reddit-fetch")
def reddit_fetch():
    if not ENABLED:
        typer.echo("Reddit signal scraping is disabled.")
        raise typer.Exit()

    today = datetime.utcnow().strftime("%Y-%m-%d")
    posts = []

    for sub in SUBREDDITS:
        url = f"https://www.reddit.com/r/{sub}/new.json?limit=50"
        try:
            res = requests.get(url, headers=REDDIT_HEADERS, timeout=10)
            items = res.json().get("data", {}).get("children", [])
            for item in items:
                post = item.get("data", {})
                title = post.get("title", "")
                if any(k.lower() in title.lower() for k in KEYWORDS):
                    posts.append({
                        "title": title,
                        "subreddit": sub,
                        "score": post.get("score"),
                        "url": post.get("url"),
                        "created": datetime.utcfromtimestamp(post.get("created_utc", 0)).isoformat()
                    })
        except Exception as e:
            typer.echo(f"Error fetching from {sub}: {e}")

    daily_file = SIGNAL_PATH / f"reddit_daily_{today}.json"
    with open(daily_file, "w") as f:
        json.dump(posts, f, indent=2)

    typer.echo(f"Saved {len(posts)} matching posts for {today}.")

@app.command("reddit-weekly")
def reddit_weekly():
    end = datetime.utcnow()
    start = end - timedelta(days=7)
    weekly_posts = []

    for file in SIGNAL_PATH.glob("reddit_daily_*.json"):
        try:
            date_str = file.stem.replace("reddit_daily_", "")
            file_date = datetime.strptime(date_str, "%Y-%m-%d")
            if start <= file_date <= end:
                with open(file) as f:
                    posts = json.load(f)
                    weekly_posts.extend(posts)
        except Exception:
            continue

    week_file = SIGNAL_PATH / f"reddit_weekly_{end.strftime('%Y-%m-%d')}.json"
    with open(week_file, "w") as f:
        json.dump(weekly_posts, f, indent=2)

    typer.echo(f"Compiled weekly Reddit summary with {len(weekly_posts)} posts.")

if __name__ == "__main__":
    app()
