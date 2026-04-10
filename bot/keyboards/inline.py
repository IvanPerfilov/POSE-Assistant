from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.utils.constants import (
    ADMIN_FAQ_ITEMS,
    ADMIN_IMAGE_ITEMS,
    ADMIN_SECTION_ITEMS,
    BTN_ADMIN_APPLICATIONS,
    BTN_ADMIN_EDIT_CONTACT,
    BTN_ADMIN_EDIT_FAQ,
    BTN_ADMIN_EDIT_IMAGES,
    BTN_ADMIN_EDIT_SECTIONS,
    BTN_ADMIN_EDIT_WELCOME,
    BTN_BACK,
    BTN_BACK_TO_MENU,
    BTN_CANCEL,
    BTN_MAIN_MENU,
    BTN_REFILL,
    BTN_REPLY_USER,
    BTN_SEND,
    FAQ_ITEMS,
    MAIN_MENU_ITEMS,
)


def main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for callback_suffix, label in MAIN_MENU_ITEMS:
        if callback_suffix in {"install_poizon", "register_poizon", "product_card"}:
            callback_data = f"section:{callback_suffix}"
        elif callback_suffix == "faq_menu":
            callback_data = "faq_menu"
        elif callback_suffix == "support_info":
            callback_data = "support_info"
        else:
            callback_data = "apply_start"
        builder.button(text=label, callback_data=callback_data)
    builder.adjust(2, 2, 2)
    return builder.as_markup()


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=BTN_BACK_TO_MENU, callback_data="main_menu")
    return builder.as_markup()


def faq_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for faq_key, label in FAQ_ITEMS:
        builder.button(text=label, callback_data=f"faq_item:{faq_key}")
    builder.button(text=BTN_BACK, callback_data="main_menu")
    builder.adjust(2, 1, 1)
    return builder.as_markup()


def faq_navigation_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Назад в FAQ", callback_data="faq_menu")
    builder.button(text=BTN_MAIN_MENU, callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()


def application_confirmation_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=BTN_SEND, callback_data="application_send")
    builder.button(text=BTN_REFILL, callback_data="application_refill")
    builder.adjust(2)
    return builder.as_markup()


def admin_reply_keyboard(user_tg_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=BTN_REPLY_USER, callback_data=f"admin_reply:{user_tg_id}")
    return builder.as_markup()


def cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=BTN_CANCEL, callback_data="flow_cancel")
    return builder.as_markup()


def admin_cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=BTN_CANCEL, callback_data="admin_cancel")
    return builder.as_markup()


def admin_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=BTN_ADMIN_APPLICATIONS, callback_data="admin_apps")
    builder.button(text=BTN_ADMIN_EDIT_WELCOME, callback_data="admin_edit_welcome")
    builder.button(text=BTN_ADMIN_EDIT_SECTIONS, callback_data="admin_edit_sections")
    builder.button(text=BTN_ADMIN_EDIT_FAQ, callback_data="admin_edit_faq")
    builder.button(text=BTN_ADMIN_EDIT_CONTACT, callback_data="admin_edit_contact")
    builder.button(text=BTN_ADMIN_EDIT_IMAGES, callback_data="admin_edit_images")
    builder.button(text=BTN_MAIN_MENU, callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()


def admin_sections_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for section_key, label in ADMIN_SECTION_ITEMS:
        builder.button(text=label, callback_data=f"admin_section:{section_key}")
    builder.button(text=BTN_BACK, callback_data="admin_back_menu")
    builder.adjust(1)
    return builder.as_markup()


def admin_faq_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for faq_key, label in ADMIN_FAQ_ITEMS:
        builder.button(text=label, callback_data=f"admin_faq:{faq_key}")
    builder.button(text=BTN_BACK, callback_data="admin_back_menu")
    builder.adjust(1)
    return builder.as_markup()


def admin_images_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for section_key, label in ADMIN_IMAGE_ITEMS:
        builder.button(text=label, callback_data=f"admin_image:{section_key}")
    builder.button(text=BTN_BACK, callback_data="admin_back_menu")
    builder.adjust(1)
    return builder.as_markup()
