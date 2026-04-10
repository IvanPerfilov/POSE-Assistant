from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.database.db import Database
from bot.keyboards.inline import (
    admin_cancel_keyboard,
    admin_faq_keyboard,
    admin_images_keyboard,
    admin_menu_keyboard,
    admin_sections_keyboard,
)
from bot.states.forms import (
    AdminEditContact,
    AdminEditFaq,
    AdminEditImage,
    AdminEditSection,
    AdminEditWelcome,
    AdminReply,
)
from bot.utils.formatters import normalize_username

router = Router(name="admin")


def _is_admin(user_id: int, admin_id: int) -> bool:
    return user_id == admin_id


async def _deny_if_not_admin_message(message: Message, db: Database, admin_id: int) -> bool:
    if _is_admin(message.from_user.id, admin_id):
        return False
    text = await db.get_text("admin_only", "Эта команда доступна только администратору.")
    await message.answer(text)
    return True


async def _deny_if_not_admin_callback(callback: CallbackQuery, db: Database, admin_id: int) -> bool:
    if _is_admin(callback.from_user.id, admin_id):
        return False
    text = await db.get_text("admin_only", "Эта команда доступна только администратору.")
    await callback.answer(text, show_alert=True)
    return True


async def _open_admin_menu(message: Message, db: Database) -> None:
    intro = await db.get_text("admin_menu_intro", "Админ-панель открыта 👇")
    await message.answer(intro, reply_markup=admin_menu_keyboard())


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext, db: Database, admin_id: int) -> None:
    if await _deny_if_not_admin_message(message, db, admin_id):
        return
    await state.clear()
    await _open_admin_menu(message, db)


@router.callback_query(
    StateFilter(
        AdminEditWelcome.waiting_text,
        AdminEditSection.choose_section,
        AdminEditSection.waiting_text,
        AdminEditFaq.choose_question,
        AdminEditFaq.waiting_answer,
        AdminEditContact.waiting_contact,
        AdminEditImage.choose_section,
        AdminEditImage.waiting_photo,
        AdminReply.waiting_message,
    ),
    F.data == "admin_cancel",
)
async def cancel_admin_flow(callback: CallbackQuery, state: FSMContext, db: Database, admin_id: int) -> None:
    if await _deny_if_not_admin_callback(callback, db, admin_id):
        return
    await state.clear()
    if callback.message:
        await _open_admin_menu(callback.message, db)
    await callback.answer()


@router.callback_query(StateFilter(None), F.data == "admin_apps")
async def admin_list_applications(
    callback: CallbackQuery,
    db: Database,
    admin_id: int,
) -> None:
    if await _deny_if_not_admin_callback(callback, db, admin_id):
        return
    if not callback.message:
        await callback.answer()
        return

    applications = await db.list_recent_applications(limit=15)
    if not applications:
        text = await db.get_text("admin_no_applications", "Пока нет заявок.")
        await callback.message.answer(text, reply_markup=admin_menu_keyboard())
        await callback.answer()
        return

    lines: list[str] = []
    for app in applications:
        lines.append(
            "\n".join(
                [
                    f"ID: {app['id']}",
                    f"Имя: {app['name']}",
                    f"Username: {app['username']}",
                    f"Ссылка: {app['link']}",
                    f"Размер: {app['size']}",
                    f"Комментарий: {app['comment']}",
                    f"Дата: {app['created_at']}",
                ]
            )
        )
    await callback.message.answer(
        "Последние заявки:\n\n" + "\n\n".join(lines),
        reply_markup=admin_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(StateFilter(None), F.data == "admin_edit_welcome")
async def admin_edit_welcome(callback: CallbackQuery, state: FSMContext, db: Database, admin_id: int) -> None:
    if await _deny_if_not_admin_callback(callback, db, admin_id):
        return
    await state.set_state(AdminEditWelcome.waiting_text)
    prompt = await db.get_text("admin_enter_welcome")
    if callback.message:
        await callback.message.answer(prompt, reply_markup=admin_cancel_keyboard())
    await callback.answer()


@router.message(AdminEditWelcome.waiting_text)
async def admin_save_welcome(message: Message, state: FSMContext, db: Database, admin_id: int) -> None:
    if await _deny_if_not_admin_message(message, db, admin_id):
        return
    new_text = (message.text or "").strip()
    if not new_text:
        prompt = await db.get_text("admin_enter_welcome")
        await message.answer(prompt)
        return
    await db.set_text("welcome", new_text)
    await state.clear()
    done = await db.get_text("admin_welcome_updated")
    await message.answer(done, reply_markup=admin_menu_keyboard())


@router.callback_query(StateFilter(None), F.data == "admin_edit_sections")
async def admin_edit_sections(callback: CallbackQuery, state: FSMContext, db: Database, admin_id: int) -> None:
    if await _deny_if_not_admin_callback(callback, db, admin_id):
        return
    await state.set_state(AdminEditSection.choose_section)
    prompt = await db.get_text("admin_choose_section")
    if callback.message:
        await callback.message.answer(prompt, reply_markup=admin_sections_keyboard())
    await callback.answer()


@router.callback_query(
    StateFilter(
        AdminEditSection.choose_section,
        AdminEditFaq.choose_question,
        AdminEditImage.choose_section,
    ),
    F.data == "admin_back_menu",
)
async def admin_back_menu(callback: CallbackQuery, state: FSMContext, db: Database, admin_id: int) -> None:
    if await _deny_if_not_admin_callback(callback, db, admin_id):
        return
    await state.clear()
    if callback.message:
        await _open_admin_menu(callback.message, db)
    await callback.answer()


@router.callback_query(AdminEditSection.choose_section, F.data.startswith("admin_section:"))
async def admin_choose_section(callback: CallbackQuery, state: FSMContext, db: Database, admin_id: int) -> None:
    if await _deny_if_not_admin_callback(callback, db, admin_id):
        return
    _, text_key = callback.data.split(":", maxsplit=1)
    if text_key not in {"install_poizon", "register_poizon", "product_card"}:
        await callback.answer()
        return
    await state.update_data(section_text_key=text_key)
    await state.set_state(AdminEditSection.waiting_text)
    prompt = await db.get_text("admin_enter_section_text")
    if callback.message:
        await callback.message.answer(prompt, reply_markup=admin_cancel_keyboard())
    await callback.answer()


@router.message(AdminEditSection.waiting_text)
async def admin_save_section_text(message: Message, state: FSMContext, db: Database, admin_id: int) -> None:
    if await _deny_if_not_admin_message(message, db, admin_id):
        return
    new_text = (message.text or "").strip()
    if not new_text:
        prompt = await db.get_text("admin_enter_section_text")
        await message.answer(prompt)
        return
    data = await state.get_data()
    section_text_key = data.get("section_text_key")
    if not section_text_key:
        await state.clear()
        await _open_admin_menu(message, db)
        return
    await db.set_text(section_text_key, new_text)
    await state.clear()
    done = await db.get_text("admin_section_updated")
    await message.answer(done, reply_markup=admin_menu_keyboard())


@router.callback_query(StateFilter(None), F.data == "admin_edit_faq")
async def admin_edit_faq(callback: CallbackQuery, state: FSMContext, db: Database, admin_id: int) -> None:
    if await _deny_if_not_admin_callback(callback, db, admin_id):
        return
    await state.set_state(AdminEditFaq.choose_question)
    prompt = await db.get_text("admin_choose_faq")
    if callback.message:
        await callback.message.answer(prompt, reply_markup=admin_faq_keyboard())
    await callback.answer()


@router.callback_query(AdminEditFaq.choose_question, F.data.startswith("admin_faq:"))
async def admin_choose_faq(callback: CallbackQuery, state: FSMContext, db: Database, admin_id: int) -> None:
    if await _deny_if_not_admin_callback(callback, db, admin_id):
        return
    _, faq_key = callback.data.split(":", maxsplit=1)
    if faq_key not in {"faq_order", "faq_delivery", "faq_size"}:
        await callback.answer()
        return
    await state.update_data(faq_key=faq_key)
    await state.set_state(AdminEditFaq.waiting_answer)
    prompt = await db.get_text("admin_enter_faq_answer")
    if callback.message:
        await callback.message.answer(prompt, reply_markup=admin_cancel_keyboard())
    await callback.answer()


@router.message(AdminEditFaq.waiting_answer)
async def admin_save_faq_answer(message: Message, state: FSMContext, db: Database, admin_id: int) -> None:
    if await _deny_if_not_admin_message(message, db, admin_id):
        return
    answer = (message.text or "").strip()
    if not answer:
        prompt = await db.get_text("admin_enter_faq_answer")
        await message.answer(prompt)
        return
    data = await state.get_data()
    faq_key = data.get("faq_key")
    if not faq_key:
        await state.clear()
        await _open_admin_menu(message, db)
        return
    await db.set_faq_answer(faq_key, answer)
    await state.clear()
    done = await db.get_text("admin_faq_updated")
    await message.answer(done, reply_markup=admin_menu_keyboard())


@router.callback_query(StateFilter(None), F.data == "admin_edit_contact")
async def admin_edit_contact(callback: CallbackQuery, state: FSMContext, db: Database, admin_id: int) -> None:
    if await _deny_if_not_admin_callback(callback, db, admin_id):
        return
    await state.set_state(AdminEditContact.waiting_contact)
    prompt = await db.get_text("admin_enter_contact")
    if callback.message:
        await callback.message.answer(prompt, reply_markup=admin_cancel_keyboard())
    await callback.answer()


@router.message(AdminEditContact.waiting_contact)
async def admin_save_contact(message: Message, state: FSMContext, db: Database, admin_id: int) -> None:
    if await _deny_if_not_admin_message(message, db, admin_id):
        return
    contact = (message.text or "").strip()
    if not contact:
        prompt = await db.get_text("admin_enter_contact")
        await message.answer(prompt)
        return

    contact = normalize_username(contact)
    await db.set_setting("manager_username", contact)
    await state.clear()
    done = await db.get_text("admin_contact_updated")
    await message.answer(done, reply_markup=admin_menu_keyboard())


@router.callback_query(StateFilter(None), F.data == "admin_edit_images")
async def admin_edit_images(callback: CallbackQuery, state: FSMContext, db: Database, admin_id: int) -> None:
    if await _deny_if_not_admin_callback(callback, db, admin_id):
        return
    await state.set_state(AdminEditImage.choose_section)
    prompt = await db.get_text("admin_choose_image")
    if callback.message:
        await callback.message.answer(prompt, reply_markup=admin_images_keyboard())
    await callback.answer()


@router.callback_query(AdminEditImage.choose_section, F.data.startswith("admin_image:"))
async def admin_choose_image_section(
    callback: CallbackQuery,
    state: FSMContext,
    db: Database,
    admin_id: int,
) -> None:
    if await _deny_if_not_admin_callback(callback, db, admin_id):
        return
    _, section_key = callback.data.split(":", maxsplit=1)
    if section_key not in {"welcome", "install_poizon", "register_poizon", "product_card", "faq"}:
        await callback.answer()
        return

    await state.update_data(image_section_key=section_key)
    await state.set_state(AdminEditImage.waiting_photo)
    prompt = await db.get_text("admin_send_image")
    if callback.message:
        await callback.message.answer(prompt, reply_markup=admin_cancel_keyboard())
    await callback.answer()


@router.message(AdminEditImage.waiting_photo, F.photo)
async def admin_save_image(message: Message, state: FSMContext, db: Database, admin_id: int) -> None:
    if await _deny_if_not_admin_message(message, db, admin_id):
        return
    data = await state.get_data()
    section_key = data.get("image_section_key")
    if not section_key:
        await state.clear()
        await _open_admin_menu(message, db)
        return
    file_id = message.photo[-1].file_id
    await db.set_image(section_key=section_key, file_id=file_id)
    await state.clear()
    done = await db.get_text("admin_image_updated")
    await message.answer(done, reply_markup=admin_menu_keyboard())


@router.message(AdminEditImage.waiting_photo)
async def admin_save_image_invalid(message: Message, db: Database, admin_id: int) -> None:
    if await _deny_if_not_admin_message(message, db, admin_id):
        return
    prompt = await db.get_text("admin_send_image")
    await message.answer(prompt, reply_markup=admin_cancel_keyboard())


@router.callback_query(F.data.startswith("admin_reply:"))
async def admin_reply_to_user_start(
    callback: CallbackQuery,
    state: FSMContext,
    db: Database,
    admin_id: int,
) -> None:
    if await _deny_if_not_admin_callback(callback, db, admin_id):
        return
    if not callback.message:
        await callback.answer()
        return

    _, user_tg_id_raw = callback.data.split(":", maxsplit=1)
    if not user_tg_id_raw.isdigit():
        await callback.answer()
        return

    await state.set_state(AdminReply.waiting_message)
    await state.update_data(reply_user_tg_id=int(user_tg_id_raw))
    prompt = await db.get_text("admin_reply_prompt")
    await callback.message.answer(prompt, reply_markup=admin_cancel_keyboard())
    await callback.answer()


@router.message(AdminReply.waiting_message)
async def admin_reply_to_user_send(
    message: Message,
    state: FSMContext,
    db: Database,
    admin_id: int,
) -> None:
    if await _deny_if_not_admin_message(message, db, admin_id):
        return
    reply_text = (message.text or "").strip()
    if not reply_text:
        prompt = await db.get_text("admin_reply_prompt")
        await message.answer(prompt)
        return

    data = await state.get_data()
    target_user_id = data.get("reply_user_tg_id")
    if not isinstance(target_user_id, int):
        await state.clear()
        await _open_admin_menu(message, db)
        return

    message_template = await db.get_text("manager_reply_prefix")
    try:
        await message.bot.send_message(
            chat_id=target_user_id,
            text=message_template.format(text=reply_text),
        )
    except Exception:
        unreachable = await db.get_text("user_unreachable")
        await message.answer(unreachable, reply_markup=admin_menu_keyboard())
        await state.clear()
        return

    await state.clear()
    done = await db.get_text("admin_reply_sent")
    await message.answer(done, reply_markup=admin_menu_keyboard())
