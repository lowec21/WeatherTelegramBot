import datetime
from collections import Counter
from statistics import mean
from api import check_date_filter, get_info_day_weather, get_weather, get_url_info
from telebot.types import Message

from config_data import config
from database.session import session
from loader import bot
from states.states import MyStates
from database.models import UserQueryHistory


@bot.message_handler(state=MyStates.current_city)
def get_weather_information(message):
    """
    Функция get_weather_information вызывается при установке состояния MyStates.current_city.
    В начале функция устанавливает значение для переменной current_day,
    если до выполнения этой функции текущий день(current_day) был установлен,
    то функция выполнит сценарий получения погоды за конкретный день, иначе current_day == None
    и будет выполнен сценарий получения погоды в установленном городе на следующие 5 дней.
    """

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        current_day = data['current_day'] if 'current_day' in data else None

    if current_day:
        user_id, result = get_weather_by_one_day(message, current_day)
    else:
        user_id, result = get_weather_by_5_days(message)

    data_of_query = UserQueryHistory(
        user_id=user_id,
        user_query=result
    )  # создание модели запроса пользователя

    with session() as sess:  # добавление запроса в таблицу истории запросов в базе данных
        sess.add(data_of_query)
        sess.commit()


def get_weather_by_one_day(message, current_day):
    """
    В функции get_weather_by_one_day осуществляется сбор всех данных о погоде за конкретный день
    и на их основе, формирование и отправка сообщения пользователю в чат.
    Функция возвращает id пользователя и сформированный ответ на запрос.
    """
    text_w, city_name = get_url_info(city=message.text, api_key=config.RAPID_API_KEY, message=message)  # функция вернёт словарь, откуда будут получены данные о погоде
    num_iter = len(text_w['list'])  # получение числа ключей в которых находится информация о погоде с промежутком в 3ч.
    period_for_day_list = check_date_filter(text_w, num_iter, current_day)  # формирование списка ключей, которые относятся к выбранному дню

    result_dict = get_info_day_weather(text_w, period_for_day_list, current_day)  # полученный словарь содержит верхнюю и нижнюю границы температур за день

    feels_like_list = [text_w['list'][day]['main']['feels_like'] for day in period_for_day_list]  # полученный список содержит список ощущаемых температур в течение дня
    wind_list = [text_w['list'][day]['wind']['speed'] for day in period_for_day_list]  # полученный список содержит параметр скорости ветра в течение дня
    weather_param = [text_w['list'][day]['weather'][0]['main'] for day in period_for_day_list]  # полученный список содержит погодные условия (снег, дождь, облачность и т.д.)

    feels_like = round(mean(feels_like_list))  # определяется средняя ощущаемая температура за день
    wind_speed = round(mean(wind_list))  # определяется средняя скорость ветра за день

    weather_counter = Counter(weather_param)  # подсчёт собранной информации о погодных условиях
    max_w_param = weather_counter.most_common()  # выявление погодных условий, которые будут держаться большую часть дня

    param_list = []
    for key, value in max_w_param:
        param_list.append(key)

    date = result_dict[current_day]
    weather_low = date['weather_low']
    weather_high = date['weather_high']
    param_str = ', '.join(param_list)
    result_str = f'Прогноз погоды в городе {city_name} \n\nНа {current_day} число \n' \
                 f'ожидается максимальная температура {weather_high}°C\nминимальная температура {weather_low}°C\n\n' \
                 f'Ощущается температура {feels_like}°C\nСкорость ветра в среднем {wind_speed} м/c\n' \
                 f'Погодные условия {param_str}'  # собираем всю информацию в строку

    bot.send_message(message.chat.id, result_str)  # отправляем сообщение с result_str в чат
    bot.delete_state(user_id=message.from_user.id, chat_id=message.chat.id)

    return message.from_user.id, result_str


def get_weather_by_5_days(message):
    """
    В функции get_weather_by_5_days осуществляется сбор всех данных о погоде за 5 дней
    и на их основе, формирование и отправка сообщения пользователю в чат.
    Функция возвращает id пользователя и сформированный ответ на запрос.
    """
    text_w, city_name = get_url_info(city=message.text, api_key=config.RAPID_API_KEY, message=message)  # функция вернёт словарь, откуда будут получены данные о погоде

    num_iter = len(text_w['list'])  # получение числа ключей в которых находится информация о погоде с промежутком в 3ч.
    result_dict = get_weather(text_w, num_iter)  # полученный словарь содержит верхнюю и нижнюю границы температур за каждый день

    result_str = f'Прогноз погоды в городе {city_name}\n\n'

    for date, weather in result_dict.items():
        response = f"На {date} число: \nожидается максимальная температура {int(weather['weather_high'])}°C\n" \
                   f"минимальная температура {int(weather['weather_low'])}°C\n\n"
        result_str += response

    bot.send_message(message.chat.id, result_str)
    bot.delete_state(user_id=message.from_user.id, chat_id=message.chat.id)

    return message.from_user.id, result_str


@bot.message_handler(state=MyStates.current_day)
def get_day(message):
    """
    Функция get_day проверяет введенный пользователем день, и если он соответствует ожидаемому,
    то записывает в data['current_day'].
    """
    if not message.text.isdigit():  # проверка, что пользователь ввёл число, а не буквы
        bot.reply_to(message, 'Возможно вы указали текст или какие нибудь символы!\n'
                              'Попробуйте вызвать команду снова и указать только число!')
        bot.delete_state(user_id=message.from_user.id, chat_id=message.chat.id)
        return

    date_now = datetime.datetime.now()  # блок кода формирует список из 5-ти элементов, в котором собраны даты, начиная с текущей date_now и последующие четыре
    try:
        replace_date = date_now.replace(day=int(message.text))
    except ValueError:
        replace_date = None

    five_days = []
    for _ in range(5):
        date = date_now
        date_now += datetime.timedelta(days=1)
        five_days.append(date)

    if replace_date and five_days:  # если блок выше упал и переменные остались None
        if replace_date in five_days:
            try:
                with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                    data['current_day'] = message.text
                    bot.send_message(message.chat.id, 'Теперь напишите город!')
                    bot.set_state(message.from_user.id, MyStates.current_city, message.chat.id)
            except Exception as exc:
                print('Возникла ошибка: ', exc)
        else:
            bot.send_message(message.chat.id, 'Указанное число не входит в ближайшие 5 дней!\n'
                                              'Попробуйте вызвать команду снова и указать другое число!')
            bot.delete_state(user_id=message.from_user.id, chat_id=message.chat.id)
    else:
        bot.send_message(message.chat.id, 'Указанное число не входит в ближайшие 5 дней!\n'
                                          'Попробуйте вызвать команду снова и указать другое число!')
        bot.delete_state(user_id=message.from_user.id, chat_id=message.chat.id)


@bot.message_handler(commands=['weather_for_the_day'])
def weather_for_the_day(message: Message):
    bot.set_state(message.from_user.id, MyStates.current_day, message.chat.id)
    bot.send_message(message.chat.id, 'Узнайте подробную информацию о погоде на день!\n'
                                      'Укажите один из ближайших 5-ти дней, который вас интересует')


@bot.message_handler(commands=['get_weather'])
def bot_get_weather(message: Message):
    bot.set_state(message.from_user.id, MyStates.current_city, message.chat.id)
    bot.send_message(message.chat.id, 'Введите название города:🌏 ')
