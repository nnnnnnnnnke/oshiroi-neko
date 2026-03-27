"""Twitter/X API v2 client wrapper using tweepy."""

import logging
import time

import tweepy

import config

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_BACKOFF = 60  # seconds


class TwitterClient:
    def __init__(self):
        self.client = tweepy.Client(
            bearer_token=config.TWITTER_BEARER_TOKEN,
            consumer_key=config.TWITTER_API_KEY,
            consumer_secret=config.TWITTER_API_SECRET,
            access_token=config.TWITTER_ACCESS_TOKEN,
            access_token_secret=config.TWITTER_ACCESS_TOKEN_SECRET,
            wait_on_rate_limit=True,
        )
        self._my_user_id = None

    @property
    def my_user_id(self) -> str:
        if self._my_user_id is None:
            me = self.client.get_me()
            self._my_user_id = me.data.id
        return self._my_user_id

    def post_tweet(self, text: str) -> str | None:
        """Post a tweet and return the tweet ID, or None on failure."""
        for attempt in range(MAX_RETRIES):
            try:
                response = self.client.create_tweet(text=text)
                tweet_id = response.data["id"]
                logger.info("Posted tweet %s: %s", tweet_id, text[:50])
                return tweet_id
            except tweepy.TooManyRequests:
                wait = RETRY_BACKOFF * (attempt + 1)
                logger.warning("Rate limited, waiting %ds", wait)
                time.sleep(wait)
            except tweepy.TwitterServerError as e:
                logger.error("Twitter server error: %s", e)
                time.sleep(RETRY_BACKOFF)
            except tweepy.TweepyException as e:
                logger.error("Failed to post tweet: %s", e)
                return None
        return None

    def like_tweet(self, tweet_id: str) -> bool:
        """Like a tweet. Returns True on success."""
        try:
            self.client.like(tweet_id)
            logger.info("Liked tweet %s", tweet_id)
            return True
        except tweepy.TweepyException as e:
            logger.error("Failed to like tweet %s: %s", tweet_id, e)
            return False

    def follow_user(self, user_id: str) -> bool:
        """Follow a user. Returns True on success."""
        try:
            self.client.follow_user(user_id)
            logger.info("Followed user %s", user_id)
            return True
        except tweepy.TweepyException as e:
            logger.error("Failed to follow user %s: %s", user_id, e)
            return False

    def search_recent_tweets(self, query: str, max_results: int = 10) -> list:
        """Search recent tweets. Returns list of tweet data."""
        try:
            response = self.client.search_recent_tweets(
                query=f"{query} -is:retweet lang:ja",
                max_results=min(max_results, 100),
                tweet_fields=["author_id", "created_at", "public_metrics"],
            )
            if response.data:
                return response.data
            return []
        except tweepy.TweepyException as e:
            logger.error("Search failed for '%s': %s", query, e)
            return []

    def get_likers(self, tweet_id: str, max_results: int = 20) -> list:
        """Get users who liked a specific tweet."""
        try:
            response = self.client.get_liking_users(
                tweet_id, max_results=min(max_results, 100)
            )
            if response.data:
                return response.data
            return []
        except tweepy.TweepyException as e:
            logger.error("Failed to get likers for %s: %s", tweet_id, e)
            return []

    def get_my_mentions(self, max_results: int = 10) -> list:
        """Get recent mentions of the bot account."""
        try:
            response = self.client.get_users_mentions(
                self.my_user_id,
                max_results=min(max_results, 100),
                tweet_fields=["author_id", "created_at"],
            )
            if response.data:
                return response.data
            return []
        except tweepy.TweepyException as e:
            logger.error("Failed to get mentions: %s", e)
            return []
