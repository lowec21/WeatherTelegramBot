from telebot.types import Message

from api import get_url_info
from config_data.config import RAPID_API_KEY
from database.models import UserCity
from database.session import session
from loader import bot
from states.states import MyStates


@bot.message_handler(commands=['change_home_city'])
def change_home_city(message: Message):
    """
    Функция bot_get_weather оповещает пользователя, что можно установить желаемый город,
    и для этого перенаправляет в set_home_city.
    """
    bot.send_message(message.chat.id, 'Давайте установим ваш город!\nВведите город:')
    bot.set_state(message.from_user.id, MyStates.home_city, message.chat.id)


@bot.message_handler(state=MyStates.home_city)
def set_home_city(message: Message):
    """
    Функция обрабатывает сообщение пользователя (название города), и записывает в базу данных.
    В сессии при обращении к базе, происходит проверка данных, и если по user_id уже установлен город, он будет удалён,
    а затем записан тот который пользователь указал в сообщении.
    Этот город будет использоваться для получения текущей погоды при нажатии кнопки в чате.
    """
    api_key = RAPID_API_KEY
    if get_url_info(message.text, api_key, message):
        data_of_query = UserCity(
            current_user_city=message.text,
            user_id=message.from_user.id
        )

        with session() as sess:
            user_id = message.from_user.id
            check_city_query = sess.query(UserCity).filter_by(user_id=user_id).one_or_none()
            if check_city_query:
                sess.delete(check_city_query)
            sess.add(data_of_query)
            sess.commit()

        bot.send_message(message.chat.id, 'Город сохранён! Теперь вы можете узнать актуальные данные о погоде в один клик!')
    else:
        bot.delete_state(user_id=message.from_user.id, chat_id=message.chat.id)
        return
