#!/usr/bin/env python3
"""Test script: generate sample tweets without posting to X."""

import sys
sys.path.insert(0, ".")

from bot.database import init_db
from bot.generator import TweetGenerator

CATEGORIES = [
    "proxmox_daily",
    "research_progress",
    "daily_life",
    "gaming",
    "tech_discovery",
    "shitpost",
    "cat_content",
    "lab_life",
]


def main():
    init_db()
    gen = TweetGenerator()

    print("=" * 60)
    print("白粉ねこ ツイート生成テスト")
    print("=" * 60)

    for category in CATEGORIES:
        print(f"\n--- [{category}] ---")
        try:
            tweet = gen.generate_tweet(category)
            char_count = len(tweet)
            print(f"{tweet}")
            print(f"({char_count}文字)")
        except Exception as e:
            print(f"ERROR: {e}")

    print("\n" + "=" * 60)
    print("Done!")


if __name__ == "__main__":
    main()
