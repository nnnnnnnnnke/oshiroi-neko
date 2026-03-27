#!/usr/bin/env python3
"""Like tweets matching keywords. Usage: python do_likes.py [max_likes]"""

import sys
import os
import random
from dotenv import load_dotenv
import tweepy

load_dotenv()

KEYWORDS = [
    "Proxmox",
    "自宅サーバー",
    "homelab",
    "VALORANT",
    "esports ネットワーク",
    "Neovim",
    "Linux サーバー",
    "猫 かわいい",
]


def get_client() -> tweepy.Client:
    return tweepy.Client(
        bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
        consumer_key=os.getenv("TWITTER_API_KEY"),
        consumer_secret=os.getenv("TWITTER_API_SECRET"),
        access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
        access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
    )


def do_likes(max_likes: int = 3):
    client = get_client()
    keyword = random.choice(KEYWORDS)

    try:
        results = client.search_recent_tweets(
            query=f"{keyword} -is:retweet lang:ja",
            max_results=10,
        )
    except tweepy.TweepyException as e:
        print(f"Search failed: {e}")
        return

    if not results.data:
        print(f"No tweets found for '{keyword}'")
        return

    liked = 0
    for tweet in random.sample(results.data, min(max_likes, len(results.data))):
        try:
            client.like(tweet.id)
            print(f"Liked: {tweet.id}")
            liked += 1
        except tweepy.TweepyException as e:
            print(f"Like failed: {e}")

    print(f"Liked {liked} tweets for '{keyword}'")


def main():
    max_likes = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    do_likes(max_likes)


if __name__ == "__main__":
    main()
