from api import get_current_weather, get_url_info
from config_data import config
from database.models import UserCity
from database.session import session
from loader import bot
from states.states import MyStates


@bot.callback_query_handler(func=lambda call: True)
def edit_home(call):
    """
    Функция edit_home обращается к базе данных и устанавливает значение переменной home_city равное current_user_city,
    далее если пользователь не устанавливал свой текущий город, то будет вызвана функция set_home_city,
    для установки MyStates.home_city. Город используется для формирования url-ссылки(эндпоинт).
    Этот первый запрос, позволит определить координаты указанного города.
    Затем с помощью координат формируем второй эндпоинт, где будет находиться информация о погоде.
    """
    with session() as sess:
        user_id = call.from_user.id
        res_query = sess.query(UserCity).filter_by(user_id=user_id).one_or_none()
        home_city = res_query.current_user_city if res_query else None

    if home_city:
        text_w, city_name = get_url_info(city=home_city, api_key=config.RAPID_API_KEY, message=call)
        temperature, feels_like, wind_speed, weather_param = get_current_weather(text=text_w)

        result_str = f'Прогноз погоды в городе {home_city} \n\n' \
                     f'Температура {temperature}°C\n' \
                     f'Ощущается температура {feels_like}°C\nСкорость ветра {wind_speed} м/c\n' \
                     f'Погодные условия {weather_param}'

        bot.send_message(call.message.chat.id, result_str)

    else:
        bot.send_message(call.message.chat.id, 'Для начала, давайте установим ваш город!\nВведите город:')
        bot.set_state(call.from_user.id, MyStates.home_city, call.message.chat.id)
