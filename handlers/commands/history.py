from telebot.types import Message

from database.models import UserQueryHistory
from database.session import session
from loader import bot


@bot.message_handler(commands=['history'])
def history_user_query(message: Message):
    """
    Функция history_user_query выводит историю последних 10-ти запросов пользователя.
    Открывается сессия, в которой создается объект запроса к таблице UserQueryHistory.
    Получившийся список объектов мы обходим в цикле и заполняем строку res_message,
    если она превышает лимит символов, то заполняется резервная строка reserve_string.
    В чат отправляется получившееся сообщение из res_message,
    и если reserve_string не пустая строка, то так же отправляется.
    """

    with session() as sess:
        res_select = (
            sess.query(UserQueryHistory)
            .filter(UserQueryHistory.user_id == message.from_user.id)
            .order_by(UserQueryHistory.timestamp.desc())
            .limit(10)
            .all()
        )

    res_message = ''  # строка для формирования сообщения
    reserve_string = ''  # резервная строка на случай если 10 запросов не уместятся в 4000 символов
    limit_length_message = 3500  # лимит символов, чтобы не превысить 4000(макс. длина сообщения в телеграм)
    for index, query in enumerate(res_select, 1):
        timestamp = query.timestamp.strftime('%m.%d.%Y  Время %H:%M')
        if len(res_message) < limit_length_message:
            res_message += f'{index}. Запрос на {timestamp}:\n\n{query.user_query}' \
                          f'\n\n-----------------------------------------------------------------------\n\n'
        else:
            reserve_string += f'{index}. Запрос на {timestamp}:\n\n{query.user_query}' \
                          f'\n\n-----------------------------------------------------------------------\n\n'

    if res_message == '':
        bot.send_message(message.chat.id, 'История пуста!')
    else:
        bot.send_message(message.chat.id, 'Ваши последние 10 запросов: ')
        bot.send_message(message.chat.id, res_message)
        if len(reserve_string) > 0:
            bot.send_message(message.chat.id, reserve_string)
