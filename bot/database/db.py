from __future__ import annotations

from pathlib import Path

import aiosqlite

DEFAULT_TEXTS: dict[str, str] = {
    "welcome": (
        "Привет! 👋\n\n"
        "Я помогу с сервисом доставки товаров с Poizon: инструкции, FAQ и заявка менеджеру.\n"
        "Выберите нужный раздел в меню ниже 👇"
    ),
    "menu_prompt": "Главное меню 👇",
    "install_poizon": (
        "📲 Установка Poizon:\n"
        "1. Откройте App Store / Google Play.\n"
        "2. Найдите приложение Poizon.\n"
        "3. Установите и запустите приложение."
    ),
    "register_poizon": (
        "📝 Регистрация в Poizon:\n"
        "1. Откройте приложение.\n"
        "2. Выберите регистрацию по телефону или почте.\n"
        "3. Подтвердите код и заполните профиль."
    ),
    "product_card": (
        "🧾 Карточка товара:\n"
        "• Фото — внешний вид товара.\n"
        "• Размеры — доступные варианты.\n"
        "• Цена — стоимость в приложении.\n"
        "• Описание — важные детали модели."
    ),
    "faq_intro": "Выберите вопрос из FAQ 👇",
    "support_instruction": (
        "Если нужна помощь, напишите менеджеру в Telegram.\n"
        "Опишите вопрос коротко и приложите ссылку на товар."
    ),
    "ask_name": "Как вас зовут?",
    "ask_link": "Пришлите ссылку на товар (http/https).",
    "ask_size": "Укажите нужный размер.",
    "ask_comment": "Комментарий к заявке (или отправьте \"-\").",
    "validation_name": "Имя не должно быть пустым. Введите имя ещё раз.",
    "validation_link": "Ссылка должна содержать http:// или https://. Попробуйте ещё раз.",
    "validation_size": "Размер не должен быть пустым. Введите размер ещё раз.",
    "application_confirmation": (
        "Проверьте заявку 👇\n\n"
        "Имя: {name}\n"
        "Username: {username}\n"
        "Ссылка: {link}\n"
        "Размер: {size}\n"
        "Комментарий: {comment}"
    ),
    "application_sent": "Заявка отправлена. Менеджер свяжется с вами в ближайшее время.",
    "application_admin_template": (
        "📦 НОВАЯ ЗАЯВКА\n\n"
        "Имя: {name}\n"
        "Username: {username}\n"
        "Ссылка: {link}\n"
        "Размер: {size}\n"
        "Комментарий: {comment}"
    ),
    "admin_only": "Эта команда доступна только администратору.",
    "admin_menu_intro": "Админ-панель открыта 👇",
    "admin_no_applications": "Пока нет заявок.",
    "admin_enter_welcome": "Отправьте новый текст приветствия.",
    "admin_welcome_updated": "Приветствие обновлено ✅",
    "admin_choose_section": "Выберите раздел, который хотите изменить.",
    "admin_enter_section_text": "Отправьте новый текст для выбранного раздела.",
    "admin_section_updated": "Текст раздела обновлён ✅",
    "admin_choose_faq": "Выберите пункт FAQ для редактирования.",
    "admin_enter_faq_answer": "Отправьте новый ответ для выбранного FAQ.",
    "admin_faq_updated": "FAQ обновлён ✅",
    "admin_enter_contact": "Отправьте @username менеджера.",
    "admin_contact_updated": "Контакт менеджера обновлён ✅",
    "admin_choose_image": "Выберите раздел, для которого хотите изменить изображение.",
    "admin_send_image": "Отправьте фотографию для выбранного раздела.",
    "admin_image_updated": "Изображение обновлено ✅",
    "admin_reply_prompt": "Введите сообщение пользователю.",
    "admin_reply_sent": "Сообщение пользователю отправлено ✅",
    "manager_reply_prefix": "💬 Сообщение от менеджера:\n\n{text}",
    "faq_not_found": "Ответ пока не добавлен.",
    "faq_back_prompt": "Выберите вопрос из FAQ 👇",
    "user_unreachable": "Не удалось отправить сообщение пользователю.",
    "error_generic": "Что-то пошло не так. Попробуйте ещё раз чуть позже.",
}

DEFAULT_FAQ: list[tuple[str, str, str]] = [
    (
        "faq_order",
        "Как заказать",
        "Выбираете товар, отправляете ссылку через кнопку «Оставить заявку», дальше менеджер подскажет по шагам.",
    ),
    (
        "faq_delivery",
        "Сроки доставки",
        "Обычно доставка занимает от 10 до 25 дней, в зависимости от склада и логистики.",
    ),
    (
        "faq_size",
        "Подбор размера",
        "Для подбора размера отправьте менеджеру длину стельки и модель — поможем выбрать точнее.",
    ),
]

DEFAULT_SETTINGS: dict[str, str] = {
    "manager_username": "@poizon_manager",
}


class Database:
    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    async def init(self) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.executescript(
                """
                PRAGMA foreign_keys = ON;

                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER NOT NULL UNIQUE,
                    username TEXT,
                    full_name TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_tg_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    username TEXT,
                    link TEXT NOT NULL,
                    size TEXT NOT NULL,
                    comment TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS texts (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS faq (
                    key TEXT PRIMARY KEY,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS images (
                    section_key TEXT PRIMARY KEY,
                    file_id TEXT NOT NULL,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            await db.executemany(
                "INSERT OR IGNORE INTO texts (key, value) VALUES (?, ?)",
                list(DEFAULT_TEXTS.items()),
            )
            await db.executemany(
                "INSERT OR IGNORE INTO faq (key, question, answer) VALUES (?, ?, ?)",
                DEFAULT_FAQ,
            )
            await db.executemany(
                "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
                list(DEFAULT_SETTINGS.items()),
            )
            await db.commit()

    async def upsert_user(
        self,
        telegram_id: int,
        username: str | None,
        full_name: str | None,
    ) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                INSERT INTO users (telegram_id, username, full_name)
                VALUES (?, ?, ?)
                ON CONFLICT(telegram_id) DO UPDATE SET
                    username = excluded.username,
                    full_name = excluded.full_name
                """,
                (telegram_id, username, full_name),
            )
            await db.commit()

    async def get_text(self, key: str, default: str = "") -> str:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT value FROM texts WHERE key = ?", (key,))
            row = await cursor.fetchone()
            await cursor.close()
            if row is None:
                return default
            return str(row["value"])

    async def set_text(self, key: str, value: str) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                INSERT INTO texts (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (key, value),
            )
            await db.commit()

    async def get_faq_answer(self, faq_key: str) -> str | None:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT answer FROM faq WHERE key = ?",
                (faq_key,),
            )
            row = await cursor.fetchone()
            await cursor.close()
            return None if row is None else str(row["answer"])

    async def set_faq_answer(self, faq_key: str, answer: str) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                UPDATE faq
                SET answer = ?, updated_at = CURRENT_TIMESTAMP
                WHERE key = ?
                """,
                (answer, faq_key),
            )
            await db.commit()

    async def get_setting(self, key: str, default: str = "") -> str:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT value FROM settings WHERE key = ?",
                (key,),
            )
            row = await cursor.fetchone()
            await cursor.close()
            if row is None:
                return default
            return str(row["value"])

    async def set_setting(self, key: str, value: str) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                INSERT INTO settings (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (key, value),
            )
            await db.commit()

    async def get_image(self, section_key: str) -> str | None:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT file_id FROM images WHERE section_key = ?",
                (section_key,),
            )
            row = await cursor.fetchone()
            await cursor.close()
            if row is None:
                return None
            return str(row["file_id"])

    async def set_image(self, section_key: str, file_id: str) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                INSERT INTO images (section_key, file_id)
                VALUES (?, ?)
                ON CONFLICT(section_key) DO UPDATE SET
                    file_id = excluded.file_id,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (section_key, file_id),
            )
            await db.commit()

    async def create_application(
        self,
        user_tg_id: int,
        name: str,
        username: str | None,
        link: str,
        size: str,
        comment: str,
    ) -> int:
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute(
                """
                INSERT INTO applications (
                    user_tg_id,
                    name,
                    username,
                    link,
                    size,
                    comment
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (user_tg_id, name, username, link, size, comment),
            )
            await db.commit()
            return int(cursor.lastrowid)

    async def list_recent_applications(self, limit: int = 10) -> list[dict[str, str]]:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT id, user_tg_id, name, username, link, size, comment, created_at
                FROM applications
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            )
            rows = await cursor.fetchall()
            await cursor.close()
            return [dict(row) for row in rows]
