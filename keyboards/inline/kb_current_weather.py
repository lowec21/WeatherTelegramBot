from telebot import types


def key_button_func():
    markup = types.InlineKeyboardMarkup()
    key_button = types.InlineKeyboardButton('Узнать погоду сейчас!', callback_data='current_weather')
    markup.add(key_button)
    return markup


