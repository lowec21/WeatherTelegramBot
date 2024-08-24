from telebot.handler_backends import StatesGroup, State


class MyStates(StatesGroup):
    current_city = State()
    current_day = State()
    current_weather = State()
    home_city = State()
