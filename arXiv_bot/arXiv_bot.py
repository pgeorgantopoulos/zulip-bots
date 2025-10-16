"""
Zulip arXiv watcher bot.
Polling arXiv API and posting new matches to a Zulip stream.
"""

import sqlite3
import urllib.parse
import requests
import feedparser
from dateutil import parser as dateparser
import zulip
import yaml
import os
from typing import List
import sys

def load_config(path):
    if os.path.exists(path):
        with open(path) as f:
            cfg = yaml.safe_load(f) or {}
    else:
        print(f"Config file {path} not found.")
    return cfg

# ---- arXiv helpers ----
ARXIV_API = "http://export.arxiv.org/api/query"

#def build_query(keywords: List[str]) -> str:
#    """
#    Build a single arXiv search_query string combining keywords with OR.
#    Searching in 'all' fields. Keywords with spaces are quoted.
#    Example: all:"graph neural network" OR all:"quantum"
#    """
#    parts = []
#    for kw in keywords:
#        kw_escaped = kw.replace('"', '')  # crude sanitize
#        parts.append(f'all:"{kw_escaped}"')
#    return " OR ".join(parts)

def build_query(keywords: List[str], operator="AND", category=None):
    """
    combine keywords with given operator (AND/OR).
    """
    parts = [f'all:"{kw.replace("\"", "")}"' for kw in keywords]
    query = f" {operator} ".join(parts)
    if category:
        query = f"({query}) AND cat:{category}"
    return query


def fetch_arxiv_entries(keywords: List[str], max_results=25):
    query = build_query(keywords)
    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "lastUpdatedDate",
        "sortOrder": "descending"
    }
    url = ARXIV_API + "?" + urllib.parse.urlencode(params)
    # polite headers
    headers = {"User-Agent": "zulip-arxiv-bot/1.0 (mailto:your-email@example.com)"}
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    feed = feedparser.parse(resp.text)
    return feed.entries

# ---- SQLite store for seen IDs ----
def init_db(path):
    con = sqlite3.connect(path, check_same_thread=False)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS seen (
            id TEXT PRIMARY KEY,
            first_seen TIMESTAMP
        )
    """)
    con.commit()
    return con

def mark_seen(con, arxiv_id):
    cur = con.cursor()
    cur.execute("INSERT OR IGNORE INTO seen(id, first_seen) VALUES (?, CURRENT_TIMESTAMP)", (arxiv_id,))
    con.commit()

def is_seen(con, arxiv_id):
    cur = con.cursor()
    cur.execute("SELECT 1 FROM seen WHERE id = ?", (arxiv_id,))
    return cur.fetchone() is not None

# ---- Zulip posting ----
def zulip_client_from_env_or_file(zuliprc_file=None):
    client = zulip.Client(config_file=zuliprc_file)  # reads ~/.zuliprc by default
    return client

def format_entry_md(entry):
    # arXiv entry fields from feedparser: id, title, summary, authors (list of dict), published
    arxiv_id = entry.id.split('/')[-1]
    title = entry.title.strip().replace('\n', ' ')
    summary = entry.summary.strip().replace('\n', ' ')
    published = dateparser.parse(entry.published).strftime("%Y-%m-%d")
    authors = ", ".join(a.name for a in entry.authors) if hasattr(entry, "authors") else "Unknown"
    # find link
    link = None
    for l in entry.get("links", []):
        if l.get("rel") == "alternate":
            link = l.get("href")
            break
    if not link and entry.get("id"):
        link = entry.id
    md = f"**{title}**  \n" \
         f"*arXiv:* `{arxiv_id}`  \n" \
         f"*Published:* {published}  \n" \
         f"*Authors:* {authors}  \n\n" \
         f"{summary[:800]}{'...' if len(summary) > 800 else ''}  \n\n" \
         f"[View on arXiv]({link})"
    return md, arxiv_id

def send_to_zulip(client, stream, subject, content_md):
    message = {
        "type": "stream",
        "to": stream,
        "subject": subject,
        "content": content_md
    }
    result = client.send_message(message)
    return result

# ---- Main loop ----
def run_once(CONFIG_FILE, ZULIPRC_FILE, BOT_DIR):
    cfg = load_config(CONFIG_FILE)
    name = cfg["name"]
    keywords = cfg["keywords"]
    # poll_interval = cfg["poll_interval_seconds"]
    max_results = cfg["max_results_per_query"]
    zulip_stream = cfg["zulip_stream"]
    zulip_subject = cfg["zulip_subject"]
    db_path = os.path.join(BOT_DIR,cfg["sqlite_db"])
    
    print("Starting bot: ", name)
    print("Keywords:", keywords)
    db = init_db(db_path)
    client = zulip_client_from_env_or_file(ZULIPRC_FILE)

    try:
        entries = fetch_arxiv_entries(keywords, max_results=max_results)
        new_count = 0
        # entries are sorted by lastUpdatedDate descending
        # iterate oldest-first to post in chronological order
        for entry in reversed(entries):
            md, arxiv_id = format_entry_md(entry)
            if is_seen(db, arxiv_id):
                continue
            post
            status = send_to_zulip(client, zulip_stream, zulip_subject, md)
            # status contains Zulip response
            if status.get("result") == "success":
                print(f"Posted {arxiv_id}")
            else:
                print("Failed to post", status)
            mark_seen(db, arxiv_id)
            new_count += 1
        print(f"Complete")
        print(f"New: {new_count}")
    except Exception as e:
        print("Error:", repr(e))
        sys.exit(1)

if __name__ == "__main__":
    
    run_once(CONFIG_FILE, ZULIPRC_FILE, BOT_DIR)
