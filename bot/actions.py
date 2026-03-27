"""Social interaction logic: liking tweets and following users."""

import logging
import random

import config
from bot.twitter_client import TwitterClient
from bot.database import (
    is_already_liked,
    save_like,
    is_already_followed,
    save_follow,
    get_today_like_count,
    get_today_follow_count,
)

logger = logging.getLogger(__name__)


def do_likes(twitter: TwitterClient):
    """Search for relevant tweets and like some of them."""
    max_likes = random.randint(*config.LIKES_PER_DAY)
    already_today = get_today_like_count()
    remaining = max_likes - already_today

    if remaining <= 0:
        logger.info("Like quota reached for today (%d)", already_today)
        return

    # Pick a random subset of keywords to search
    keywords = random.sample(
        config.LIKE_SEARCH_KEYWORDS,
        min(3, len(config.LIKE_SEARCH_KEYWORDS)),
    )

    candidates = []
    for keyword in keywords:
        tweets = twitter.search_recent_tweets(keyword, max_results=10)
        for tweet in tweets:
            if not is_already_liked(str(tweet.id)):
                candidates.append(tweet)

    if not candidates:
        logger.info("No new tweets found to like")
        return

    # Shuffle and like up to remaining quota
    random.shuffle(candidates)
    liked = 0
    for tweet in candidates:
        if liked >= remaining:
            break
        tweet_id = str(tweet.id)
        if twitter.like_tweet(tweet_id):
            save_like(tweet_id)
            liked += 1

    logger.info("Liked %d tweets", liked)


def do_follows(twitter: TwitterClient):
    """Follow back users who interacted with us."""
    max_follows = random.randint(*config.FOLLOWS_PER_DAY)
    already_today = get_today_follow_count()
    remaining = max_follows - already_today

    if remaining <= 0:
        logger.info("Follow quota reached for today (%d)", already_today)
        return

    # Check recent mentions and follow back interesting accounts
    mentions = twitter.get_my_mentions(max_results=20)
    if not mentions:
        logger.info("No recent mentions to follow back from")
        return

    followed = 0
    author_ids = list({str(m.author_id) for m in mentions})
    random.shuffle(author_ids)

    for author_id in author_ids:
        if followed >= remaining:
            break
        if is_already_followed(author_id):
            continue
        if twitter.follow_user(author_id):
            save_follow(author_id)
            followed += 1

    logger.info("Followed %d users", followed)
