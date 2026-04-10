from __future__ import annotations

import logging

from aiogram import Router
from aiogram.types import ErrorEvent

from bot.database.db import Database

router = Router(name="errors")

logger = logging.getLogger(__name__)


@router.error()
async def on_error(event: ErrorEvent, db: Database) -> bool:
    logger.exception("Unhandled error: %s", event.exception)
    generic_text = await db.get_text(
        "error_generic",
        "Что-то пошло не так. Попробуйте ещё раз чуть позже.",
    )

    if event.update.message:
        await event.update.message.answer(generic_text)
    elif event.update.callback_query and event.update.callback_query.message:
        await event.update.callback_query.answer()
        await event.update.callback_query.message.answer(generic_text)

    return True
