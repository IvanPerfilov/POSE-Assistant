from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    bot_token: str
    admin_id: int
    db_path: str


def load_config() -> Config:
    load_dotenv()

    bot_token = os.getenv("BOT_TOKEN", "").strip()
    admin_id_raw = os.getenv("ADMIN_ID", "").strip()
    db_path = os.getenv("DB_PATH", "data/bot.db").strip()

    if not bot_token:
        raise RuntimeError("BOT_TOKEN не задан в переменных окружения")
    if not admin_id_raw.isdigit():
        raise RuntimeError("ADMIN_ID должен быть числом")

    return Config(
        bot_token=bot_token,
        admin_id=int(admin_id_raw),
        db_path=db_path,
    )
