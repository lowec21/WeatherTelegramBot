from loader import bot
import handlers  # noqa
from utils.set_bot_commands import set_commands
from telebot.custom_filters import StateFilter

if __name__ == '__main__':
    bot.add_custom_filter(StateFilter(bot))
    set_commands(bot)
    bot.infinity_polling()
