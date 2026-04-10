PRAGMA foreign_keys = ON;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL UNIQUE,
    username TEXT,
    full_name TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_tg_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    username TEXT,
    link TEXT NOT NULL,
    size TEXT NOT NULL,
    comment TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE texts (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE faq (
    key TEXT PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE images (
    section_key TEXT PRIMARY KEY,
    file_id TEXT NOT NULL,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO texts (key, value) VALUES
('welcome', 'Привет! 👋\n\nЯ помогу с сервисом доставки товаров с Poizon: инструкции, FAQ и заявка менеджеру.\nВыберите нужный раздел в меню ниже 👇'),
('menu_prompt', 'Главное меню 👇'),
('install_poizon', '📲 Установка Poizon:\n1. Откройте App Store / Google Play.\n2. Найдите приложение Poizon.\n3. Установите и запустите приложение.'),
('register_poizon', '📝 Регистрация в Poizon:\n1. Откройте приложение.\n2. Выберите регистрацию по телефону или почте.\n3. Подтвердите код и заполните профиль.'),
('product_card', '🧾 Карточка товара:\n• Фото — внешний вид товара.\n• Размеры — доступные варианты.\n• Цена — стоимость в приложении.\n• Описание — важные детали модели.'),
('faq_intro', 'Выберите вопрос из FAQ 👇'),
('support_instruction', 'Если нужна помощь, напишите менеджеру в Telegram.\nОпишите вопрос коротко и приложите ссылку на товар.'),
('application_sent', 'Заявка отправлена. Менеджер свяжется с вами в ближайшее время.');

INSERT INTO faq (key, question, answer) VALUES
('faq_order', 'Как заказать', 'Выбираете товар, отправляете ссылку через кнопку «Оставить заявку», дальше менеджер подскажет по шагам.'),
('faq_delivery', 'Сроки доставки', 'Обычно доставка занимает от 10 до 25 дней, в зависимости от склада и логистики.'),
('faq_size', 'Подбор размера', 'Для подбора размера отправьте менеджеру длину стельки и модель — поможем выбрать точнее.');

INSERT INTO settings (key, value) VALUES
('manager_username', '@poizon_manager');

INSERT INTO users (telegram_id, username, full_name) VALUES
(111111111, 'test_user', 'Тестовый Пользователь');

INSERT INTO applications (user_tg_id, name, username, link, size, comment) VALUES
(111111111, 'Иван', '@test_user', 'https://poizon.com/item/123', '42', 'Нужна консультация по размеру');
