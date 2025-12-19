import requests
import pandas as pd
import sqlite3
from datetime import datetime
import os

DB_PATH = "data/stack_questions.db"
CSV_PATH = "data/stack_questions.csv"

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT,
            scraped_at TEXT,
            title TEXT,
            author TEXT,
            score INTEGER,
            url TEXT,
            answer_count INTEGER,
            is_answered INTEGER,
            view_count INTEGER,
            creation_date TEXT,
            tags TEXT
        )
        """
    )
    conn.commit()
    conn.close()

def scrape_keyword(keyword: str):
    # build API url
    url = (
        "https://api.stackexchange.com/2.3/search?"
        f"order=desc&sort=votes&intitle={keyword}"
        "&site=stackoverflow&pagesize=100"
    )

    response = requests.get(url)
    data = response.json()

    posts = []
    scraped_at = datetime.utcnow().isoformat()

    for item in data.get("items", []):
        title = item.get("title", "No title")
        author = item.get("owner", {}).get("display_name", "Anonymous")
        score = item.get("score", 0)
        link = item.get("link", "")
        answer_count = item.get("answer_count", 0)
        is_answered = 1 if item.get("is_answered", False) else 0
        view_count = item.get("view_count", 0)
        creation_ts = item.get("creation_date")  # unix timestamp
        creation_date = (
            datetime.utcfromtimestamp(creation_ts).isoformat()
            if creation_ts is not None else None
        )
        tags = ",".join(item.get("tags", []))

        posts.append([
            keyword, scraped_at, title, author, score, link,
            answer_count, is_answered, view_count, creation_date, tags
        ])

    # Updated column names to match the SQLite table schema
    cols = [
        "keyword",
        "scraped_at",
        "title",
        "author",
        "score",
        "url",
        "answer_count",
        "is_answered",
        "view_count",
        "creation_date",
        "tags"
    ]
    df = pd.DataFrame(posts, columns=cols)

    # Save to CSV (for backward compatibility)
    df.to_csv(CSV_PATH, index=False, encoding="utf-8")
    print(f"Scraped {len(df)} questions → {CSV_PATH}")

    # Save to SQLite
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("questions", conn, if_exists="append", index=False)
    conn.close()
    print(f"Appended {len(df)} rows to {DB_PATH}")

def main():
    keyword = input("Enter a keyword to scrape from StackOverflow: ")
    init_db()
    scrape_keyword(keyword)

if __name__ == "__main__":
    main()
