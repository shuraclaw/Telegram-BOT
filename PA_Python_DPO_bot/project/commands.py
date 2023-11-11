from datetime import date
import telebot
from telebot.types import InputMediaPhoto

from hotel_api import *
from logs import get_logger

bot = telebot.TeleBot('6070953572:AAHNbQHSRtaIIZvaZBsVx7quHaMkIyvj4Pc')
logger = get_logger('commands')


def low_price(message, data, history):
    """
    Ищет дешевые отели по заданным параметрам и выводит их пользователю
    :param message: информация о сообщении
    :param data: данные, которые ввел пользователь
    :param history: история команд
    """
    logger.debug("Пользователь {} вызвал команду low_price с параметрами {}".format(message.from_user.id, data))

    # Поиск города по названию и получение его id
    city_data = search_location(data['city'])
    city_id = city_data['city_id']

    # Если город не найден, то выводится сообщение об ошибке
    if city_id is not None:
        checkin: date = data['checkin']
        checkout: date = data['checkout']

        # Перевод даты в список из трех чисел
        check_in = [checkin.day, checkin.month, checkin.year]
        check_out = [checkout.day, checkout.month, checkout.year]

        # Подсчет количества дней между датами
        delta = (date(check_out[2], check_out[1], check_out[0]) - date(check_in[2], check_in[1],
                                                                       check_in[0])).days + 1

        # Поиск отелей по заданным параметрам
        hotels_data = search_hotels(city_data, check_in, check_out, data['count'], 'PRICE_LOW_TO_HIGH')

        # Цикл, который проходит по всем найденным отелям
        for hotel in hotels_data['data']['propertySearch']['properties']:
            # Добавление названия отеля в историю
            history[-1]['hotels'] += hotel['name'] + '\n'

            # Получение информации об отеле
            hotel_info = get_hotel_info(hotel['id'])['data']['propertyInfo']

            # Поиск расстояния до центра
            center_length = 0
            for marker in hotel_info['summary']['map']['markers']:
                if marker['mapMarker']['icon'] == 'AIRPORT':
                    center_length = int(marker['subtitle'].split()[0])
                    break

            # Если фотографии нужно вывести, то добавляются в список фотографий и выводятся пользователю
            # Иначе выводится информация об отеле без фотографий
            if data['is_photo']:
                hotel_photos = []
                for photo in hotel_info['propertyGallery']['images']:
                    hotel_photos.append(InputMediaPhoto(photo['image']['url']))

                # Вывод минимального количества фотографий между введенным количеством и доступным
                photo_len = min(len(hotel_photos), data['photo_count'])

                # Вывод информации об отеле
                bot.send_message(message.chat.id,
                                 'Отель {}\n\n'
                                 'Цена за ночь: {:.2f}$\n'
                                 'Цена за все дни: {:.2f}$\n'
                                 'Адрес: {}\n'
                                 'Расстояние до центра: {}'.format(
                                     hotel["name"],
                                     hotel["price"]["lead"]["amount"],
                                     abs(hotel["price"]["lead"]["amount"] * delta),
                                     hotel_info['summary']['location']['address']['addressLine'],
                                     center_length))

                # Вывод фотографий
                bot.send_media_group(message.chat.id, hotel_photos[:photo_len])
            else:
                # Вывод информации об отеле без фотографий
                bot.send_message(message.chat.id,
                                 'Отель {}\n\n'
                                 'Цена за ночь: {:.2f}$\n'
                                 'Цена за все дни: {:.2f}$\n'
                                 'Адрес: {}\n'
                                 'Расстояние до центра: {} минут на машине'.format(
                                     hotel["name"],
                                     hotel["price"]["lead"]["amount"],
                                     abs(hotel["price"]["lead"]["amount"] * delta),
                                     hotel_info['summary']['location']['address']['addressLine'],
                                     center_length))

    else:
        bot.send_message(message.chat.id, "Ошибка, введите правильное название города")


def high_price(message, data, history):
    """
    Ищет дорогие отели по заданным параметрам и выводит их пользователю
    :param message: информация о сообщении
    :param data: данные, которые ввел пользователь
    :param history: история команд
    """
    logger.debug("Пользователь {} вызвал команду high_price с параметрами {}".format(message.from_user.id, data))

    # Поиск города по названию и получение его id
    city_data = search_location(data['city'])
    city_id = city_data['city_id']

    # Если город не найден, то выводится сообщение об ошибке
    if city_id is not None:
        checkin: date = data['checkin']
        checkout: date = data['checkout']

        # Перевод даты в список из трех чисел
        check_in = [checkin.day, checkin.month, checkin.year]
        check_out = [checkout.day, checkout.month, checkout.year]

        # Подсчет количества дней между датами
        delta = (date(check_out[2], check_out[1], check_out[0]) - date(check_in[2], check_in[1],
                                                                       check_in[0])).days + 1

        # Поиск отелей по заданным параметрам
        hotels_data = search_hotels(city_data, check_in, check_out, 200, 'PRICE_LOW_TO_HIGH')

        # Счетчик отелей
        hotel_count = 0

        # Цикл, который проходит по всем найденным отелям
        for hotel in hotels_data['data']['propertySearch']['properties'][::-1]:
            # Если количество отелей больше или равно заданному, то цикл прерывается
            if hotel_count >= data['count']:
                break
            hotel_count += 1

            # Добавление названия отеля в историю
            history[-1]['hotels'] += hotel['name'] + '\n'

            # Получение информации об отеле
            hotel_info = get_hotel_info(hotel['id'])['data']['propertyInfo']

            # Поиск расстояния до центра
            center_length = 0
            for marker in hotel_info['summary']['map']['markers']:
                if marker['mapMarker']['icon'] == 'AIRPORT':
                    center_length = int(marker['subtitle'].split()[0])
                    break

            # Если фотографии нужно вывести, то добавляются в список фотографий и выводятся пользователю
            if data['is_photo']:
                hotel_photos = []
                for photo in hotel_info['propertyGallery']['images']:
                    hotel_photos.append(InputMediaPhoto(photo['image']['url']))

                # Вывод минимального количества фотографий между введенным количеством и доступным
                photo_len = min(len(hotel_photos), data['photo_count'])

                # Вывод информации об отеле
                bot.send_message(message.chat.id,
                                 'Отель {}\n\n'
                                 'Цена за ночь: {:.2f}$\n'
                                 'Цена за все дни: {:.2f}$\n'
                                 'Адрес: {}\n'
                                 'Расстояние до центра: {} минут на машине'.format(
                                     hotel["name"],
                                     hotel["price"]["lead"]["amount"],
                                     abs(hotel["price"]["lead"]["amount"] * delta),
                                     hotel_info['summary']['location']['address']['addressLine'],
                                     center_length))

                # Вывод фотографий
                bot.send_media_group(message.chat.id, hotel_photos[:photo_len])
            else:
                # Вывод информации об отеле без фотографий
                bot.send_message(message.chat.id,
                                 'Отель {}\n\n'
                                 'Цена за ночь: {:.2f}$\n'
                                 'Цена за все дни: {:.2f}$\n'
                                 'Адрес: {}\n'
                                 'Расстояние до центра: {} минут на машине'.format(
                                     hotel["name"],
                                     hotel["price"]["lead"]["amount"],
                                     abs(hotel["price"]["lead"]["amount"] * delta),
                                     hotel_info['summary']['location']['address']['addressLine'],
                                     center_length))

    else:
        bot.send_message(message.chat.id, "Ошибка, введите правильное название города")


def best_deal(message, data, history):
    """
    Ищет наиболее подходящие отели по заданным параметрам и выводит их пользователю
    :param message: информация о сообщении
    :param data: данные, которые ввел пользователь
    :param history: история команд
    """
    logger.debug("Пользователь {} вызвал команду best_deal с параметрами {}".format(message.from_user.id, data))

    # Поиск города по названию и получение его id
    city_data = search_location(data['city'])
    city_id = city_data['city_id']

    # Если город не найден, то выводится сообщение об ошибке
    if city_id is not None:
        checkin: date = data['checkin']
        checkout: date = data['checkout']

        # Перевод даты в список из трех чисел
        check_in = [checkin.day, checkin.month, checkin.year]
        check_out = [checkout.day, checkout.month, checkout.year]

        # Подсчет количества дней между датами
        delta = (date(check_out[2], check_out[1], check_out[0]) - date(check_in[2], check_in[1],
                                                                       check_in[0])).days + 1

        # Поиск отелей по заданным параметрам
        hotels_data = search_hotels(city_data, check_in, check_out, 200, 'RECOMMENDED',
                                    max_price=data['max_price'], min_price=data['min_price'])

        # Счетчик отелей
        hotel_count = 0

        # Цикл, который проходит по всем найденным отелям
        for hotel in hotels_data['data']['propertySearch']['properties']:
            hotel_info = get_hotel_info(hotel['id'])['data']['propertyInfo']

            # Поиск расстояния до центра
            center_length = 0
            for marker in hotel_info['summary']['map']['markers']:
                if marker['mapMarker']['icon'] == 'AIRPORT':
                    center_length = int(marker['subtitle'].split()[0])
                    break

            # Если расстояние до центра меньше заданного, то выводится информация об отеле
            if data['min_length'] <= center_length <= data['max_length']:
                if hotel_count >= data['count']:
                    break
                hotel_count += 1

                # Добавление названия отеля в историю
                history[-1]['hotels'] += hotel['name'] + '\n'

                # Если фотографии нужно вывести, то добавляются в список фотографий и выводятся пользователю
                if data['is_photo']:
                    hotel_photos = []
                    for photo in hotel_info['propertyGallery']['images']:
                        hotel_photos.append(InputMediaPhoto(photo['image']['url']))

                    # Вывод минимального количества фотографий между введенным количеством и доступным
                    photo_len = min(len(hotel_photos), data['photo_count'])

                    # Вывод информации об отеле
                    bot.send_message(message.chat.id,
                                     'Отель {}\n\n'
                                     'Цена за ночь: {:.2f}$\n'
                                     'Цена за все дни: {:.2f}$\n'
                                     'Адрес: {}\n'
                                     'Расстояние до центра: {} минут на машине'.format(
                                         hotel["name"],
                                         hotel["price"]["lead"]["amount"],
                                         abs(hotel["price"]["lead"]["amount"] * delta),
                                         hotel_info['summary']['location']['address']['addressLine'],
                                         center_length))

                    # Вывод фотографий
                    bot.send_media_group(message.chat.id, hotel_photos[:photo_len])
                else:
                    # Вывод информации об отеле без фотографий
                    bot.send_message(message.chat.id,
                                     'Отель {}\n\n'
                                     'Цена за ночь: {:.2f}$\n'
                                     'Цена за все дни: {:.2f}$\n'
                                     'Адрес: {}\n'
                                     'Расстояние до центра: {}'.format(
                                         hotel["name"],
                                         hotel["price"]["lead"]["amount"],
                                         abs(hotel["price"]["lead"]["amount"] * delta),
                                         hotel_info['summary']['location']['address']['addressLine'],
                                         center_length))

    else:
        bot.send_message(message.chat.id, "Ошибка, введите правильное название города")
