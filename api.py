import requests
from loader import bot


def check_url(url, message):
    """
    Функция get_url получает на вход строку, которая содержит url-ссылку,
    используя эту ссылку отправляется запрос к api, если статус запроса не положительный,
    то выводится сообщение об ошибке.
    """
    response = requests.get(url, timeout=5)
    if response.status_code == 200:
        return response.json()
    else:
        print('Ошибка выполнения запроса. Код состояния:', response.status_code)
        bot.send_message(message.chat.id, 'Ошибка выполнения запроса.\n Попробуйте снова!\n Выберите команду из меню')


def get_info_day_weather(text: dict, period_days: list, current_day: int) -> dict:
    """
    Функция get_info_day_weather получает на вход словарь с информацией о погоде на 5 дней,
    список ключей, которые относятся к конкретному дню и сам день.
    В цикле определяется верхняя и нижняя границы температур и записываются в словарь, если границы сдвигаются,
    то в словаре перезаписывается значение этой границы.
    Функция возвращает заполненный словарь на 1 день.
    """
    result_dict = {}
    for i in period_days:
        weather_high = text['list'][i]['main']['temp_max']
        weather_low = text['list'][i]['main']['temp_min']
        if current_day in result_dict:
            if result_dict[current_day]['weather_high'] < weather_high:
                result_dict[current_day]['weather_high'] = weather_high
            if result_dict[current_day]['weather_low'] > weather_low:
                result_dict[current_day]['weather_low'] = weather_low
        else:
            result_dict[current_day] = {'weather_high': weather_high, 'weather_low': weather_low}

    return result_dict


def get_weather(text_w: dict, num_iter: int):
    """
    Функция get_weather получает на вход словарь с информацией о погоде на 5 дней и число итераций для цикла.
    В цикле определяется день на который предоставлена информация,
    а далее верхняя и нижняя границы температур, для этого дня, записываются в словарь, если границы сдвигаются,
    то в словаре перезаписывается значение этой границы.
    Функция возвращает заполненный словарь на 5 дней.
    """
    info_about_the_days = {}
    for i in range(num_iter):
        current_day = text_w['list'][i]['dt_txt'][8:10]
        weather_high = text_w['list'][i]['main']['temp_max']
        weather_low = text_w['list'][i]['main']['temp_min']
        if current_day in info_about_the_days:
            if info_about_the_days[current_day]['weather_high'] < weather_high:
                info_about_the_days[current_day]['weather_high'] = weather_high
            if info_about_the_days[current_day]['weather_low'] > weather_low:
                info_about_the_days[current_day]['weather_low'] = weather_low
        else:
            info_about_the_days[current_day] = {'weather_high': weather_high, 'weather_low': weather_low}
    return info_about_the_days


def get_current_weather(text: dict):
    """
    Функция получает на вход словарь с данными о погоде на текущее время,
    затем присваивает переменным информацию о погоде и возвращает эти переменные.
    """
    weather_high = text['list'][0]['main']['temp_max']
    weather_low = text['list'][0]['main']['temp_min']
    feels_like = round(text['list'][0]['main']['feels_like'], 1)
    wind_speed = text['list'][0]['wind']['speed']
    weather_param = text['list'][0]['weather'][0]['main']
    temperature = round((weather_high + weather_low) / 2, 1)

    return temperature, feels_like, wind_speed, weather_param


def check_date_filter(text_w, num_iter, current_day):
    """
    Функция check_date_filter получает на вход словарь с информацией о погоде на 5 дней,
    число итераций для цикла и сам день.
    Задача функции: сформировать список тех ключей в словаре, в которых содержится информация об определённом дне.
    Функция возвращает заполненный список и корректное название города на русском.
    """
    period_for_day_list = []

    for i in range(num_iter):
        this_day = text_w['list'][i]['dt_txt'][8:10]
        if int(this_day) == int(current_day):
            period_for_day_list.append(i)
    return period_for_day_list


def get_url_info(city, api_key, message):
    """
    Функция get_url_info формирует url-ссылки для обращения к api,
    сначала используя название города получает координаты,
    затем используя координаты, получает данные о погоде в виде словаря и возвращает его.
    """
    url = f'http://api.openweathermap.org/geo/1.0/direct?q={city}&appid={api_key}'  # первый эндпоинт, подставляем город и ключ-api
    text = check_url(url, message)  # проверка статуса ответа от api, получение словаря с координатами города

    if len(text) > 0:  # проверка на то, что text не пуст, ответ от сервера может быть положительным и при этом пустым
        lat = text[0]['lat']
        lon = text[0]['lon']
        city_name = text[0]['local_names']['ru']  # достаём из API корректное имя на русском

        url_2 = f'http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric'
        # второй эндпоинт, подставляем координаты и ключ-api

        text_w = check_url(url_2, message)  # проверка статуса ответа от api и получение словаря с информацией о погоде
    else:  # если text будет пуст, значит город был указан неверно, сообщаем об этом пользователю
        bot.delete_state(user_id=message.from_user.id, chat_id=message.chat.id)
        bot.reply_to(message, 'Возможно город введён неверно, попробуйте снова!\nВыберите команду из меню')
        return

    return text_w, city_name
