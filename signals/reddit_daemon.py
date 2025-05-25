# reddit_daemon.py
import time
import typer
from signals.Reddit import reddit_fetch
from utils.config import load_config

def main(poll_interval: int = 60):
    """
    Runs reddit_fetch every `poll_interval` seconds,
    but only if reddit_enabled=True in config.json.
    """
    typer.echo(f"Starting Reddit daemon (interval={poll_interval}s)…")
    while True:
        cfg = load_config()
        if cfg.get("reddit_enabled", False):
            try:
                reddit_fetch()      # imported from signals/Reddit.py 
            except Exception as e:
                typer.echo(f"[red]Fetch error:[/] {e}")
        time.sleep(poll_interval)

if __name__ == "__main__":
    typer.run(main)
