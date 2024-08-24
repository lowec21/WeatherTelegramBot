from telebot.types import Message

from loader import bot
from keyboards.inline.kb_current_weather import key_button_func


@bot.message_handler(commands=['start'])
def bot_start(message: Message):
    markup = key_button_func()
    bot.reply_to(message, f'Привет, {message.from_user.full_name}!\nЭто погодный бот!🌧️☀️⚡❄️'
                          f'\nВыберите команду из меню или нажмите на кнопку!', reply_markup=markup)
