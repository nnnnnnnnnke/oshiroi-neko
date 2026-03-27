import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent

# X (Twitter) API
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", "")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET", "")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "")

# Anthropic API
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = "claude-opus-4-6"

# Character
CHARACTER_PROFILE_PATH = BASE_DIR / "character_profile.md"

# Database
DB_PATH = BASE_DIR / "data" / "tweet_history.db"

# Tweet scheduling
TWEETS_PER_DAY = (10, 20)
LIKES_PER_DAY = (5, 15)
FOLLOWS_PER_DAY = (0, 3)

# Active hours with weights (hour: weight)
# Matches her daily routine from the profile
ACTIVE_HOURS_WEIGHTS = {
    9: 0.3,   # just woke up
    10: 0.5,  # research start
    11: 0.5,
    12: 0.4,  # lunch
    13: 0.6,  # research
    14: 0.6,
    15: 0.6,
    16: 0.6,
    17: 0.5,
    18: 0.3,  # commute home
    19: 0.5,  # gaming
    20: 0.5,
    21: 0.8,  # personal dev, peak posting
    22: 1.0,  # peak
    23: 1.0,  # peak
    0: 0.8,   # late night
    1: 0.6,   # winding down
}

# Tweet categories with time-of-day mapping
TWEET_CATEGORIES = {
    "proxmox_daily": {
        "hours": range(21, 26),
        "weight": 1.0,
        "description": "今日のroot@proxmox 作業報告",
    },
    "research_progress": {
        "hours": range(10, 18),
        "weight": 0.8,
        "description": "研究の進捗・実験結果",
    },
    "daily_life": {
        "hours": range(9, 14),
        "weight": 0.6,
        "description": "日常 (食事・コーヒー・朝のつらさ)",
    },
    "gaming": {
        "hours": range(19, 22),
        "weight": 0.7,
        "description": "VALORANT・esports観戦",
    },
    "tech_discovery": {
        "hours": range(21, 25),
        "weight": 0.9,
        "description": "新しい技術・ツール発見",
    },
    "shitpost": {
        "hours": range(0, 3),
        "weight": 0.5,
        "description": "深夜テンションのゆるいツイート",
    },
    "cat_content": {
        "hours": range(0, 24),
        "weight": 0.4,
        "description": "猫関連",
    },
    "lab_life": {
        "hours": range(10, 18),
        "weight": 0.5,
        "description": "研究室の日常・後輩との会話",
    },
}

# Keywords for finding tweets to like
LIKE_SEARCH_KEYWORDS = [
    "Proxmox",
    "自宅サーバー",
    "homelab",
    "VALORANT",
    "esports ネットワーク",
    "SDN",
    "Neovim",
    "Linux サーバー",
    "ネットワーク遅延",
    "猫 かわいい",
    "近畿大学",
]
