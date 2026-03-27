"""Tweet generation using Claude API."""

import logging
from datetime import datetime

import anthropic

import config
from bot.prompts import (
    CATEGORY_PROMPTS,
    DEDUP_INSTRUCTION,
    GENERATION_INSTRUCTION,
    SYSTEM_PROMPT_TEMPLATE,
)
from bot.database import get_recent_tweets

logger = logging.getLogger(__name__)

DAY_NAMES_JA = ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"]


class TweetGenerator:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self.profile = self._load_profile()

    def _load_profile(self) -> str:
        return config.CHARACTER_PROFILE_PATH.read_text(encoding="utf-8")

    def _build_system_prompt(self) -> str:
        return SYSTEM_PROMPT_TEMPLATE.format(character_profile=self.profile)

    def generate_tweet(self, category: str) -> str:
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M")
        day_of_week = DAY_NAMES_JA[now.weekday()]

        # Build user prompt
        parts = []

        # Category-specific instructions
        if category in CATEGORY_PROMPTS:
            parts.append(CATEGORY_PROMPTS[category])

        # Dedup context
        recent = get_recent_tweets(20)
        if recent:
            recent_text = "\n".join(f"- {t}" for t in recent)
            parts.append(DEDUP_INSTRUCTION.format(recent_tweets=recent_text))

        # Generation instruction
        parts.append(
            GENERATION_INSTRUCTION.format(
                current_time=current_time,
                day_of_week=day_of_week,
                category=category,
            )
        )

        user_prompt = "\n\n".join(parts)

        # Call Claude API
        try:
            response = self.client.messages.create(
                model=config.CLAUDE_MODEL,
                max_tokens=400,
                temperature=0.85,
                system=self._build_system_prompt(),
                messages=[{"role": "user", "content": user_prompt}],
            )
            tweet = response.content[0].text.strip()

            # Remove quotes if Claude wraps the tweet in them
            if tweet.startswith(("「", "『", '"')) and tweet.endswith(("」", "』", '"')):
                tweet = tweet[1:-1]

            # Validate length
            if len(tweet) > 280:
                logger.warning(
                    "Tweet too long (%d chars), retrying with strict instruction",
                    len(tweet),
                )
                return self._retry_shorter(user_prompt, tweet)

            return tweet

        except anthropic.APIError as e:
            logger.error("Claude API error: %s", e)
            raise

    def _retry_shorter(self, original_prompt: str, long_tweet: str) -> str:
        retry_prompt = (
            f"以下のツイートが280文字を超えています。内容を維持しつつ280文字以内に短縮してください。\n\n"
            f"元のツイート:\n{long_tweet}\n\n"
            f"短縮版のツイート本文のみを出力してください。"
        )

        response = self.client.messages.create(
            model=config.CLAUDE_MODEL,
            max_tokens=400,
            temperature=0.7,
            system=self._build_system_prompt(),
            messages=[{"role": "user", "content": retry_prompt}],
        )
        tweet = response.content[0].text.strip()
        if tweet.startswith(("「", "『", '"')) and tweet.endswith(("」", "』", '"')):
            tweet = tweet[1:-1]

        # Hard truncate as last resort
        if len(tweet) > 280:
            tweet = tweet[:277] + "..."

        return tweet
