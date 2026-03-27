#!/usr/bin/env python3
"""Follow back users who mentioned us. Usage: python do_follow.py [max_follows]"""

import sys
import os
from dotenv import load_dotenv
import tweepy

load_dotenv()


def get_client() -> tweepy.Client:
    return tweepy.Client(
        bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
        consumer_key=os.getenv("TWITTER_API_KEY"),
        consumer_secret=os.getenv("TWITTER_API_SECRET"),
        access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
        access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
    )


def do_follow(max_follows: int = 2):
    client = get_client()

    me = client.get_me()
    my_id = me.data.id

    try:
        mentions = client.get_users_mentions(my_id, max_results=20)
    except tweepy.TweepyException as e:
        print(f"Get mentions failed: {e}")
        return

    if not mentions.data:
        print("No recent mentions")
        return

    # Get current following to avoid re-following
    try:
        following = client.get_users_following(my_id, max_results=1000)
        following_ids = {str(u.id) for u in (following.data or [])}
    except tweepy.TweepyException:
        following_ids = set()

    followed = 0
    seen = set()
    for mention in mentions.data:
        author_id = str(mention.author_id)
        if author_id in seen or author_id == str(my_id) or author_id in following_ids:
            continue
        seen.add(author_id)

        try:
            client.follow_user(author_id)
            print(f"Followed: {author_id}")
            followed += 1
        except tweepy.TweepyException as e:
            print(f"Follow failed: {e}")

        if followed >= max_follows:
            break

    print(f"Followed {followed} users")


def main():
    max_follows = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    do_follow(max_follows)


if __name__ == "__main__":
    main()
