"""SQLite database for tracking tweets, likes, and follows."""

import sqlite3
from datetime import datetime
from pathlib import Path

import config


def get_connection() -> sqlite3.Connection:
    config.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS tweets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tweet_id TEXT UNIQUE,
            content TEXT NOT NULL,
            category TEXT,
            posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tweet_id TEXT UNIQUE,
            liked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS follows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE,
            username TEXT,
            followed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()


def save_tweet(tweet_id: str, content: str, category: str):
    conn = get_connection()
    conn.execute(
        "INSERT OR IGNORE INTO tweets (tweet_id, content, category) VALUES (?, ?, ?)",
        (tweet_id, content, category),
    )
    conn.commit()
    conn.close()


def get_recent_tweets(n: int = 20) -> list[str]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT content FROM tweets ORDER BY posted_at DESC LIMIT ?", (n,)
    ).fetchall()
    conn.close()
    return [row["content"] for row in rows]


def save_like(tweet_id: str):
    conn = get_connection()
    conn.execute(
        "INSERT OR IGNORE INTO likes (tweet_id) VALUES (?)", (tweet_id,)
    )
    conn.commit()
    conn.close()


def is_already_liked(tweet_id: str) -> bool:
    conn = get_connection()
    row = conn.execute(
        "SELECT 1 FROM likes WHERE tweet_id = ?", (tweet_id,)
    ).fetchone()
    conn.close()
    return row is not None


def save_follow(user_id: str, username: str = ""):
    conn = get_connection()
    conn.execute(
        "INSERT OR IGNORE INTO follows (user_id, username) VALUES (?, ?)",
        (user_id, username),
    )
    conn.commit()
    conn.close()


def is_already_followed(user_id: str) -> bool:
    conn = get_connection()
    row = conn.execute(
        "SELECT 1 FROM follows WHERE user_id = ?", (user_id,)
    ).fetchone()
    conn.close()
    return row is not None


def get_today_tweet_count() -> int:
    conn = get_connection()
    today = datetime.now().strftime("%Y-%m-%d")
    row = conn.execute(
        "SELECT COUNT(*) as cnt FROM tweets WHERE date(posted_at) = ?", (today,)
    ).fetchone()
    conn.close()
    return row["cnt"]


def get_today_like_count() -> int:
    conn = get_connection()
    today = datetime.now().strftime("%Y-%m-%d")
    row = conn.execute(
        "SELECT COUNT(*) as cnt FROM likes WHERE date(liked_at) = ?", (today,)
    ).fetchone()
    conn.close()
    return row["cnt"]


def get_today_follow_count() -> int:
    conn = get_connection()
    today = datetime.now().strftime("%Y-%m-%d")
    row = conn.execute(
        "SELECT COUNT(*) as cnt FROM follows WHERE date(followed_at) = ?", (today,)
    ).fetchone()
    conn.close()
    return row["cnt"]
