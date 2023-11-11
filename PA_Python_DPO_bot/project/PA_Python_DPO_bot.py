from datetime import datetime
import telebot
from telebot import types
from telebot import custom_filters
from telebot.handler_backends import State, StatesGroup
from telegram_bot_calendar import DetailedTelegramCalendar

from commands import low_price, best_deal, high_price
from logs import get_logger

# Запись истории команд
history = []
logger = get_logger("bot")

# Инициализация бота
bot = telebot.TeleBot(TOKEN)


# Класс со всеми состояниями
class MyStates(StatesGroup):
    count = State()
    city = State()
    checkin = State()
    checkout = State()
    is_photo = State()
    photo_count = State()
    price_range = State()
    len_range = State()

    lowprice = State()
    highprice = State()
    bestdeal = State()


@bot.message_handler(state="*", commands=['cancel'])
def any_state(message):
    """
     Команда cancel, которая сбрасывает все состояния
    :param message: информация о сообщении
    """
    logger.info("Пользователь {} сбросил команду".format(message.from_user.id))

    bot.send_message(message.chat.id, "Вы сбросили команду")

    bot.delete_state(message.from_user.id, message.chat.id)
    logger.debug("Пользователь {} сбросил состояние".format(message.from_user.id))


@bot.message_handler(state="*", commands=['help'])
def help_command(message):
    """
    Команда help, которая выводит информацию об использовании бота
    :param message: информация о сообщении
    """
    logger.info("Пользователь {} вызвал команду help".format(message.from_user.id))

    bot.send_message(message.chat.id, "Доступные команды:\n\n"
                                      "/lowprice -  вывод самых дешёвых отелей в городе\n"
                                      "/highprice -  вывод самых дорогих отелей в городе\n"
                                      "/bestdeal - вывод отелей, наиболее подходящих по цене и расположению от центра\n"
                                      "/history - вывод истории поиска отелей\n"
                                      "/help - помощь по командам бота\n"
                                      "/cancel - сбросить команду")


@bot.message_handler(commands=["lowprice"])
def lowprice(message):
    """
    Команда lowprice, выводит самые дешёвые отели в городе
    :param message: информация о сообщении
    """
    logger.info("Пользователь {} вызвал команду lowprice".format(message.from_user.id))

    history.append({'command': 'lowprice', 'hotels': '', 'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
    bot.send_message(message.chat.id, "Введите количество отелей")

    bot.set_state(message.from_user.id, MyStates.count, message.chat.id)
    logger.debug("Пользователь {} установил состояние count".format(message.from_user.id))

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['command'] = 'lowprice'


@bot.message_handler(commands=["highprice"])
def highprice(message):
    """
    Команда highprice, выводит самые дорогие отели в городе
    :param message: информация о сообщении
    """
    logger.info("Пользователь {} вызвал команду highprice".format(message.from_user.id))

    history.append({'command': 'highprice', 'hotels': '', 'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
    bot.send_message(message.chat.id, "Введите количество отелей")

    bot.set_state(message.from_user.id, MyStates.count, message.chat.id)
    logger.debug("Пользователь {} установил состояние count".format(message.from_user.id))

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['command'] = 'highprice'


@bot.message_handler(commands=["bestdeal"])
def bestdeal(message):
    """
    Команда bestdeal, выводит отели, наиболее подходящие по цене и расположению от центра
    :param message: информация о сообщении
    """
    logger.info("Пользователь {} вызвал команду bestdeal".format(message.from_user.id))

    history.append({'command': 'bestdeal', 'hotels': '', 'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
    bot.send_message(message.chat.id, "Введите количество отелей")

    bot.set_state(message.from_user.id, MyStates.count, message.chat.id)
    logger.debug("Пользователь {} установил состояние count".format(message.from_user.id))

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['command'] = 'bestdeal'


@bot.message_handler(commands=['history'])
def history_command(message):
    """
    Команда history, которая выводит историю команд (название, время и название отелей)
    :param message: информация о сообщении
    """
    for command_history in history:
        if command_history['hotels'] == '':
            bot.send_message(message.chat.id,
                             "Команда: {}\n"
                             "Время вызова: {}\n\n"
                             "Отели: Не было найдено".format(
                                 command_history['command'],
                                 command_history['time']))
        else:
            bot.send_message(message.chat.id,
                             "Команда: {}\n"
                             "Время вызова: {}\n\n"
                             "Отели:\n{}".format(
                                 command_history['command'],
                                 command_history['time'],
                                 command_history['hotels']))
    if len(history) == 0:
        bot.send_message(message.chat.id, "Не было вызвано ни одной команды")

    logger.info("Пользователь {} вызвал команду history, длина истории: {}".format(message.from_user.id, len(history)))


@bot.message_handler(state=MyStates.count)
def get_hotels_count(message):
    """
    Запоминает количество отелей и запрашивает название города
    :param message: информация о сообщении
    """
    logger.info("Пользователь {} ввел количество отелей: {}".format(message.from_user.id, message.text))

    if message.text.isdigit():
        bot.send_message(message.chat.id, "Введите название города")

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['count'] = int(message.text)

        bot.set_state(message.from_user.id, MyStates.city, message.chat.id)
        logger.debug("Пользователь {} установил состояние city".format(message.from_user.id))
    else:
        bot.send_message(message.chat.id, "Неправильно введенные данные: количество отелей должно быть целым числом")
        logger.warning("Пользователь {} ввел неправильные данные: количество отелей должно быть целым числом".format(message.from_user.id))


@bot.message_handler(state=MyStates.city)
def get_city_name(message):
    """
    В зависимости от команды запрашивает дату приезда или диапазон цен\n
    Если команда bestdeal, то запрашивает диапазон цен, иначе дату приезда
    :param message: информация о сообщении
    """
    logger.info("Пользователь {} ввел название города: {}".format(message.from_user.id, message.text))

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        if data['command'] != 'bestdeal':
            calendar, step = DetailedTelegramCalendar().build()
            bot.send_message(message.chat.id, "Выберите дату приезда", reply_markup=calendar)

            bot.set_state(message.from_user.id, MyStates.checkin, message.chat.id)
            logger.debug("Пользователь {} установил состояние checkin".format(message.from_user.id))
        else:
            bot.send_message(message.chat.id, "Введите диапазон цен (min max)")
            bot.set_state(message.from_user.id, MyStates.price_range, message.chat.id)
            logger.debug("Пользователь {} установил состояние price_range".format(message.from_user.id))

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['city'] = message.text


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(), state=MyStates.checkin)
def cal_checkin(call):
    """
    Обрабатывает нажатия на кнопки календаря
    :param call: информация о нажатии
    """
    result, key, step = DetailedTelegramCalendar().process(call.data)
    if not result and key:
        bot.edit_message_text("Выберите дату приезда", call.from_user.id, call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text("Выбрана дата приезда: {}".format(result), call.from_user.id, call.message.message_id)
        logger.info("Пользователь {} выбрал дату приезда: {}".format(call.from_user.id, result))

        calendar_checkout, step = DetailedTelegramCalendar().build()
        bot.send_message(call.message.chat.id, "Выберите дату уезда", reply_markup=calendar_checkout)

        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['checkin'] = result

        bot.set_state(call.from_user.id, MyStates.checkout, call.message.chat.id)
        logger.debug("Пользователь {} установил состояние checkout".format(call.from_user.id))


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(), state=MyStates.checkout)
def cal_checkout(call):
    """
    Обрабатывает нажатия на кнопки календаря
    :param call: информация о нажатии
    """
    result, key, step = DetailedTelegramCalendar().process(call.data)
    if not result and key:
        bot.edit_message_text("Выберите дату уезда", call.from_user.id, call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text("Выбрана дата уезда: {}".format(result), call.from_user.id, call.message.message_id)
        logger.info("Пользователь {} выбрал дату уезда: {}".format(call.from_user.id, result))

        keyboard = types.InlineKeyboardMarkup()
        key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
        keyboard.add(key_yes)
        key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
        keyboard.add(key_no)

        bot.send_message(call.message.chat.id, text='Нужно прикладывать фотографии?', reply_markup=keyboard)

        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['checkout'] = result

        bot.set_state(call.from_user.id, MyStates.price_range, call.message.chat.id)
        logger.debug("Пользователь {} установил состояние price_range".format(call.from_user.id))


@bot.callback_query_handler(func=lambda call: True)
def need_photos(call):
    """
    Запоминает, нужно ли прикладывать фотографии\n
    Если нужно, то запрашивает количество фотографий, иначе запускает команду выбора отелей
    :param call: информация о сообщении
    """
    logger.info("Пользователь {} выбрал: {}".format(call.from_user.id, call.data))

    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        if call.data == 'yes':
            data['is_photo'] = True
            bot.send_message(call.message.chat.id, "Введите количество фотографий")
            bot.set_state(call.from_user.id, MyStates.photo_count, call.message.chat.id)
            logger.debug("Пользователь {} установил состояние photo_count".format(call.from_user.id))
        if call.data == 'no':
            data['is_photo'] = False
            if data['command'] == 'lowprice':
                logger.debug("Пользователь {} запустил команду lowprice".format(call.from_user.id))
                low_price(call.message, data, history)
            elif data['command'] == 'highprice':
                logger.debug("Пользователь {} запустил команду highprice".format(call.from_user.id))
                high_price(call.message, data, history)
            elif data['command'] == 'bestdeal':
                logger.debug("Пользователь {} запустил команду bestdeal".format(call.from_user.id))
                best_deal(call.message, data, history)


@bot.message_handler(state=MyStates.photo_count)
def photo_count(message):
    """
    Запоминает количество фотографий и запускает команду выбора отелей
    :param message: информация о сообщении
    """
    logger.info("Пользователь {} ввел количество фотографий: {}".format(message.from_user.id, message.text))

    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['photo_count'] = int(message.text)

            if data['command'] == 'lowprice':
                logger.debug("Пользователь {} запустил команду lowprice".format(message.from_user.id))
                low_price(message, data, history)
            elif data['command'] == 'highprice':
                logger.debug("Пользователь {} запустил команду highprice".format(message.from_user.id))
                high_price(message, data, history)
            elif data['command'] == 'bestdeal':
                logger.debug("Пользователь {} запустил команду bestdeal".format(message.from_user.id))
                best_deal(message, data, history)
    else:
        bot.send_message(message.chat.id, "Неправильно введенные данные: количество фотографий должно быть целым числом")
        logger.warning("Пользователь {} ввел неправильное количество фотографий".format(message.from_user.id))


@bot.message_handler(state=MyStates.price_range)
def price_range(message):
    """
    Запоминает диапазон цен и запрашивает диапазон расстояния от центра
    :param message: информация о сообщении
    """
    logger.info("Пользователь {} ввел диапазон цен: {}".format(message.from_user.id, message.text))

    r = message.text.split()
    if len(r) == 2 and r[0].isdigit() and r[1].isdigit() and int(r[0]) > 0 and int(r[1]) > 0 and int(r[1]) > int(r[0]):
        bot.send_message(message.chat.id, "Введите диапазон расстояния, на котором находится отель от центра (min max)")

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['min_price'] = int(r[0])
            data['max_price'] = int(r[1])

        bot.set_state(message.from_user.id, MyStates.len_range, message.chat.id)
        logger.debug("Пользователь {} установил состояние len_range".format(message.from_user.id))
    else:
        bot.send_message(message.chat.id, "Неправильно введенные данные:"
                                          " диапазон цен должен быть двумя целыми числами через пробел")
        logger.warning("Пользователь {} ввел неправильный диапазон цен".format(message.from_user.id))


@bot.message_handler(state=MyStates.len_range)
def len_range(message):
    """
    Запоминает диапазон расстояния от центра и запрашивает дату приезда
    :param message: информация о сообщении
    """
    logger.info("Пользователь {} ввел диапазон расстояния: {}".format(message.from_user.id, message.text))

    r = message.text.split()
    if len(r) == 2 and r[0].isdigit() and r[1].isdigit() and int(r[0]) > 0 and int(r[1]) > 0 and int(r[1]) > int(r[0]):
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['min_length'] = int(r[0])
            data['max_length'] = int(r[1])

        calendar, step = DetailedTelegramCalendar().build()
        bot.send_message(message.chat.id, "Выберите дату приезда", reply_markup=calendar)

        bot.set_state(message.from_user.id, MyStates.checkin, message.chat.id)
        logger.debug("Пользователь {} установил состояние checkin".format(message.from_user.id))
    else:
        bot.send_message(message.chat.id, "Неправильно введенные данные:"
                                          " диапазон расстояния должен быть двумя целыми числами через пробел")
        logger.warning("Пользователь {} ввел неправильный диапазон расстояния".format(message.from_user.id))


# Запуск проверки состояний
bot.add_custom_filter(custom_filters.StateFilter(bot))

# Запуск бота
logger.info("Бот запущен")
bot.infinity_polling(skip_pending=True)
