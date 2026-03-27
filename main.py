#!/usr/bin/env python3
"""白粉ねこ X Bot - Entry point."""

import logging
import sys

from bot.database import init_db
from bot.scheduler import BotScheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ],
)

logger = logging.getLogger(__name__)


def main():
    logger.info("=== 白粉ねこ Bot starting ===")

    # Initialize database
    init_db()
    logger.info("Database initialized")

    # Start scheduler
    bot = BotScheduler()
    bot.start()


if __name__ == "__main__":
    main()
