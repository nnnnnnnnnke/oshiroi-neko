"""APScheduler-based tweet scheduling with natural timing."""

import logging
import random
from datetime import datetime, timedelta

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.date import DateTrigger

import config
from bot.generator import TweetGenerator
from bot.twitter_client import TwitterClient
from bot.database import save_tweet, get_today_tweet_count
from bot.actions import do_likes, do_follows

logger = logging.getLogger(__name__)


def _pick_category_for_hour(hour: int) -> str:
    """Pick a tweet category appropriate for the given hour."""
    # Normalize hour for 24h+ (e.g., 25 -> 1)
    norm_hour = hour % 24

    candidates = []
    for cat_name, cat_info in config.TWEET_CATEGORIES.items():
        cat_hours = [h % 24 for h in cat_info["hours"]]
        if norm_hour in cat_hours:
            candidates.append((cat_name, cat_info["weight"]))

    if not candidates:
        # Fallback: pick from all categories
        candidates = [
            (name, info["weight"])
            for name, info in config.TWEET_CATEGORIES.items()
        ]

    names, weights = zip(*candidates)
    return random.choices(names, weights=weights, k=1)[0]


def _generate_tweet_times(count: int, date: datetime) -> list[datetime]:
    """Generate random tweet times weighted by active hours."""
    hours = list(config.ACTIVE_HOURS_WEIGHTS.keys())
    weights = list(config.ACTIVE_HOURS_WEIGHTS.values())

    times = []
    for _ in range(count):
        hour = random.choices(hours, weights=weights, k=1)[0]
        minute = random.randint(0, 59)
        second = random.randint(0, 59)

        # Handle hours >= 24 (next day)
        if hour >= 24:
            t = date.replace(hour=0, minute=0, second=0) + timedelta(
                days=1, hours=hour - 24, minutes=minute, seconds=second
            )
        else:
            t = date.replace(hour=hour, minute=minute, second=second)

        # Add jitter of +/- 10 minutes
        jitter = random.randint(-600, 600)
        t += timedelta(seconds=jitter)

        times.append(t)

    times.sort()
    return times


class BotScheduler:
    def __init__(self):
        self.scheduler = BlockingScheduler()
        self.generator = TweetGenerator()
        self.twitter = TwitterClient()

    def _post_tweet_job(self, category: str):
        """Job: generate and post a single tweet."""
        try:
            tweet_text = self.generator.generate_tweet(category)
            logger.info("Generated [%s]: %s", category, tweet_text[:60])

            tweet_id = self.twitter.post_tweet(tweet_text)
            if tweet_id:
                save_tweet(tweet_id, tweet_text, category)
                logger.info("Successfully posted tweet %s", tweet_id)
            else:
                logger.error("Failed to post tweet")
        except Exception:
            logger.exception("Error in post_tweet_job")

    def _social_actions_job(self):
        """Job: perform likes and follows."""
        try:
            do_likes(self.twitter)
            do_follows(self.twitter)
        except Exception:
            logger.exception("Error in social_actions_job")

    def plan_day(self):
        """Schedule all tweets and social actions for today."""
        now = datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Determine tweet count
        tweet_count = random.randint(*config.TWEETS_PER_DAY)
        already_posted = get_today_tweet_count()
        remaining = max(0, tweet_count - already_posted)

        if remaining == 0:
            logger.info("All tweets for today already posted")
            return

        logger.info("Planning %d tweets for today (already posted: %d)", remaining, already_posted)

        # Generate times
        times = _generate_tweet_times(remaining, today)

        # Filter out past times
        future_times = [t for t in times if t > now]
        if not future_times:
            # If all times are past, generate one for soon
            future_times = [now + timedelta(minutes=random.randint(1, 5))]

        # Schedule each tweet
        for t in future_times:
            category = _pick_category_for_hour(t.hour)
            self.scheduler.add_job(
                self._post_tweet_job,
                trigger=DateTrigger(run_date=t),
                args=[category],
                id=f"tweet_{t.strftime('%H%M%S')}_{category}",
                replace_existing=True,
            )
            logger.info("Scheduled [%s] at %s", category, t.strftime("%H:%M:%S"))

        # Schedule social actions 3 times throughout the day
        for hour_offset in [2, 6, 10]:
            action_time = now + timedelta(hours=hour_offset)
            if action_time.date() == now.date():
                self.scheduler.add_job(
                    self._social_actions_job,
                    trigger=DateTrigger(run_date=action_time),
                    id=f"social_{hour_offset}",
                    replace_existing=True,
                )
                logger.info("Scheduled social actions at %s", action_time.strftime("%H:%M"))

        # Schedule next day's planning at midnight + random offset
        tomorrow = today + timedelta(days=1, minutes=random.randint(1, 30))
        self.scheduler.add_job(
            self.plan_day,
            trigger=DateTrigger(run_date=tomorrow),
            id="plan_next_day",
            replace_existing=True,
        )
        logger.info("Next day planning at %s", tomorrow.strftime("%Y-%m-%d %H:%M"))

    def start(self):
        """Start the scheduler (blocking)."""
        logger.info("Starting 白粉ねこ bot scheduler...")
        self.plan_day()
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Scheduler stopped.")
