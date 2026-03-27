#!/usr/bin/env python3
import sys
import os
from dotenv import load_dotenv
import tweepy

load_dotenv()

def post_tweet(text: str) -> None:
    client = tweepy.Client(
        consumer_key=os.environ["TWITTER_API_KEY"],
        consumer_secret=os.environ["TWITTER_API_SECRET"],
        access_token=os.environ["TWITTER_ACCESS_TOKEN"],
        access_token_secret=os.environ["TWITTER_ACCESS_TOKEN_SECRET"],
    )
    response = client.create_tweet(text=text)
    print(f"投稿成功: https://twitter.com/i/web/status/{response.data['id']}")
    print(f"内容: {text}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使い方: python3 post_tweet.py \"ツイート本文\"", file=sys.stderr)
        sys.exit(1)
    tweet_text = sys.argv[1]
    post_tweet(tweet_text)
