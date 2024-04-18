from aiogram.fsm.state import StatesGroup, State


class StartStatus(StatesGroup):
    choose = State()
    enter_code = State()


class SendData(StatesGroup):
    sending = State()
