from aiogram.fsm.state import State, StatesGroup


class ApplicationForm(StatesGroup):
    name = State()
    link = State()
    size = State()
    comment = State()
    confirm = State()


class AdminEditWelcome(StatesGroup):
    waiting_text = State()


class AdminEditSection(StatesGroup):
    choose_section = State()
    waiting_text = State()


class AdminEditFaq(StatesGroup):
    choose_question = State()
    waiting_answer = State()


class AdminEditContact(StatesGroup):
    waiting_contact = State()


class AdminEditImage(StatesGroup):
    choose_section = State()
    waiting_photo = State()


class AdminReply(StatesGroup):
    waiting_message = State()
