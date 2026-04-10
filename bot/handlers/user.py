from __future__ import annotations

import re

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from bot.database.db import Database
from bot.keyboards.inline import (
    admin_reply_keyboard,
    application_confirmation_keyboard,
    back_to_menu_keyboard,
    cancel_keyboard,
    faq_menu_keyboard,
    faq_navigation_keyboard,
    main_menu_keyboard,
)
from bot.states.forms import ApplicationForm
from bot.utils.constants import SECTION_IMAGE_KEYS, SECTION_TEXT_KEYS
from bot.utils.formatters import normalize_username

router = Router(name="user")


async def _send_main_menu(message: Message, db: Database) -> None:
    menu_text = await db.get_text("menu_prompt", "Главное меню 👇")
    await message.answer(menu_text, reply_markup=main_menu_keyboard())


async def _send_section(message: Message, db: Database, section_key: str) -> None:
    text_key = SECTION_TEXT_KEYS[section_key]
    image_key = SECTION_IMAGE_KEYS[section_key]
    section_text = await db.get_text(text_key)
    image_file_id = await db.get_image(image_key)

    if image_file_id:
        await message.answer_photo(
            photo=image_file_id,
            caption=section_text,
            reply_markup=back_to_menu_keyboard(),
        )
        return

    await message.answer(section_text, reply_markup=back_to_menu_keyboard())


async def _replace_callback_message_with_text(
    callback: CallbackQuery,
    text: str,
    reply_markup: InlineKeyboardMarkup,
) -> None:
    if not callback.message:
        return
    chat_id = callback.message.chat.id
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass
    await callback.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)


async def _replace_callback_message_with_media(
    callback: CallbackQuery,
    text: str,
    reply_markup: InlineKeyboardMarkup,
    image_file_id: str | None,
) -> None:
    if not callback.message:
        return
    chat_id = callback.message.chat.id
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass
    if image_file_id:
        await callback.bot.send_photo(
            chat_id=chat_id,
            photo=image_file_id,
            caption=text,
            reply_markup=reply_markup,
        )
        return
    await callback.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, db: Database) -> None:
    await state.clear()
    await db.upsert_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name,
    )
    welcome_text = await db.get_text("welcome")
    welcome_image = await db.get_image("welcome")
    if welcome_image:
        await message.answer_photo(
            photo=welcome_image,
            caption=welcome_text,
            reply_markup=main_menu_keyboard(),
        )
        return
    await message.answer(welcome_text, reply_markup=main_menu_keyboard())


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext, db: Database) -> None:
    await state.clear()
    await _send_main_menu(message, db)


@router.callback_query(F.data == "main_menu")
async def open_main_menu(callback: CallbackQuery, state: FSMContext, db: Database) -> None:
    await state.clear()
    menu_text = await db.get_text("menu_prompt", "Главное меню 👇")
    await _replace_callback_message_with_text(callback, menu_text, main_menu_keyboard())
    await callback.answer()


@router.callback_query(StateFilter("*"), F.data == "flow_cancel")
async def cancel_any_flow(callback: CallbackQuery, state: FSMContext, db: Database) -> None:
    await state.clear()
    menu_text = await db.get_text("menu_prompt", "Главное меню 👇")
    await _replace_callback_message_with_text(callback, menu_text, main_menu_keyboard())
    await callback.answer()


@router.callback_query(StateFilter(None), F.data.startswith("section:"))
async def section_handler(callback: CallbackQuery, db: Database) -> None:
    if not callback.message:
        await callback.answer()
        return

    _, section_key = callback.data.split(":", maxsplit=1)
    if section_key not in SECTION_TEXT_KEYS:
        await callback.answer()
        return

    text_key = SECTION_TEXT_KEYS[section_key]
    image_key = SECTION_IMAGE_KEYS[section_key]
    section_text = await db.get_text(text_key)
    image_file_id = await db.get_image(image_key)
    await _replace_callback_message_with_media(
        callback=callback,
        text=section_text,
        reply_markup=back_to_menu_keyboard(),
        image_file_id=image_file_id,
    )
    await callback.answer()


@router.callback_query(StateFilter(None), F.data == "faq_menu")
async def faq_menu(callback: CallbackQuery, db: Database) -> None:
    intro_text = await db.get_text("faq_intro")
    image_file_id = await db.get_image("faq")
    await _replace_callback_message_with_media(
        callback=callback,
        text=intro_text,
        reply_markup=faq_menu_keyboard(),
        image_file_id=image_file_id,
    )
    await callback.answer()


@router.callback_query(StateFilter(None), F.data.startswith("faq_item:"))
async def faq_answer_handler(callback: CallbackQuery, db: Database) -> None:
    if not callback.message:
        await callback.answer()
        return

    _, faq_key = callback.data.split(":", maxsplit=1)
    answer = await db.get_faq_answer(faq_key)
    if not answer:
        answer = await db.get_text("faq_not_found", "Ответ пока не добавлен.")

    await _replace_callback_message_with_text(callback, answer, faq_navigation_keyboard())
    await callback.answer()


@router.callback_query(StateFilter(None), F.data == "support_info")
async def support_handler(callback: CallbackQuery, db: Database) -> None:
    manager_username = await db.get_setting("manager_username", "@poizon_manager")
    manager_username = normalize_username(manager_username)
    support_instruction = await db.get_text("support_instruction")
    await _replace_callback_message_with_text(
        callback=callback,
        text=f"{support_instruction}\n\nМенеджер: {manager_username}",
        reply_markup=main_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(StateFilter(None), F.data == "apply_start")
async def start_application(callback: CallbackQuery, state: FSMContext, db: Database) -> None:
    await state.clear()
    await state.set_state(ApplicationForm.name)
    ask_name = await db.get_text("ask_name")
    await _replace_callback_message_with_text(callback, ask_name, cancel_keyboard())
    await callback.answer()


@router.message(ApplicationForm.name)
async def process_application_name(message: Message, state: FSMContext, db: Database) -> None:
    name = (message.text or "").strip()
    if not name:
        validation_text = await db.get_text("validation_name")
        await message.answer(validation_text)
        return

    await state.update_data(name=name)
    await state.set_state(ApplicationForm.link)
    ask_link = await db.get_text("ask_link")
    await message.answer(ask_link, reply_markup=cancel_keyboard())


@router.message(ApplicationForm.link)
async def process_application_link(message: Message, state: FSMContext, db: Database) -> None:
    link = (message.text or "").strip()
    if not re.search(r"https?://", link, flags=re.IGNORECASE):
        validation_text = await db.get_text("validation_link")
        await message.answer(validation_text)
        return

    await state.update_data(link=link)
    await state.set_state(ApplicationForm.size)
    ask_size = await db.get_text("ask_size")
    await message.answer(ask_size, reply_markup=cancel_keyboard())


@router.message(ApplicationForm.size)
async def process_application_size(message: Message, state: FSMContext, db: Database) -> None:
    size = (message.text or "").strip()
    if not size:
        validation_text = await db.get_text("validation_size")
        await message.answer(validation_text)
        return

    await state.update_data(size=size)
    await state.set_state(ApplicationForm.comment)
    ask_comment = await db.get_text("ask_comment")
    await message.answer(ask_comment, reply_markup=cancel_keyboard())


@router.message(ApplicationForm.comment)
async def process_application_comment(message: Message, state: FSMContext, db: Database) -> None:
    comment = (message.text or "").strip()
    comment = "—" if comment == "-" else comment

    data = await state.get_data()
    username = normalize_username(message.from_user.username)

    await state.update_data(
        username=username,
        comment=comment if comment else "—",
    )

    confirmation_template = await db.get_text("application_confirmation")
    confirmation_text = confirmation_template.format(
        name=data.get("name", ""),
        username=username,
        link=data.get("link", ""),
        size=data.get("size", ""),
        comment=comment if comment else "—",
    )

    await state.set_state(ApplicationForm.confirm)
    await message.answer(
        confirmation_text,
        reply_markup=application_confirmation_keyboard(),
    )


@router.callback_query(ApplicationForm.confirm, F.data == "application_refill")
async def application_refill(
    callback: CallbackQuery,
    state: FSMContext,
    db: Database,
) -> None:
    await state.clear()
    await state.set_state(ApplicationForm.name)
    ask_name = await db.get_text("ask_name")
    await _replace_callback_message_with_text(callback, ask_name, cancel_keyboard())
    await callback.answer()


@router.callback_query(ApplicationForm.confirm, F.data == "application_send")
async def application_send(
    callback: CallbackQuery,
    state: FSMContext,
    db: Database,
    admin_id: int,
) -> None:
    data = await state.get_data()
    name = data.get("name", "")
    username = data.get("username", "без username")
    link = data.get("link", "")
    size = data.get("size", "")
    comment = data.get("comment", "—")

    await db.create_application(
        user_tg_id=callback.from_user.id,
        name=name,
        username=username,
        link=link,
        size=size,
        comment=comment,
    )

    admin_template = await db.get_text("application_admin_template")
    admin_text = admin_template.format(
        name=name,
        username=username,
        link=link,
        size=size,
        comment=comment,
    )

    await callback.bot.send_message(
        chat_id=admin_id,
        text=admin_text,
        reply_markup=admin_reply_keyboard(callback.from_user.id),
    )

    await state.clear()
    sent_text = await db.get_text("application_sent")
    await _replace_callback_message_with_text(callback, sent_text, main_menu_keyboard())
    await callback.answer()
