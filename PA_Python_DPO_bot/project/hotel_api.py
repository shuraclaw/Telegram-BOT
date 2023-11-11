import requests
import json

from logs import get_logger

logger = get_logger('hotel_api')

# Глобальные переменные
HOTELS_API_KEY = API_TOKEN
HOTELS_API_HOST = "hotels4.p.rapidapi.com"


def search_location(city: str):
    """
        Функция поиска города по названию
        :param city: название города
        :type city: str
        :return: список, содержащий id города, его долготуБ широту и название
    """
    logger.debug(f'Поиск города {city}')
    url = "https://hotels4.p.rapidapi.com/locations/v3/search"

    headers = {
        "X-RapidAPI-Key": HOTELS_API_KEY,
        "X-RapidAPI-Host": HOTELS_API_HOST
    }

    params = {
        "q": city,
        "locale": "en_US",
        "langid": "1033",
        "siteid": "300000001"
    }

    response = requests.request("GET", url, headers=headers, params=params).text
    text = json.loads(response)

    data = {}

    for gaia in text['sr']:
        if gaia['type'] == 'CITY':
            print(gaia['gaiaId'])
            data['city_id'] = gaia['gaiaId']
            data['lat'] = gaia['coordinates']['lat']
            data['long'] = gaia['coordinates']['long']
            data['name'] = gaia['regionNames']['displayName']
            break

    logger.debug(f'Найден город {data["name"]}')

    return data


def search_hotels(city_data: dict, checkin: list, checkout: list, count: int, sort: str, max_price: int = 1000,
                  min_price: int = 5):
    """
    Функция поиска отелей по городу

    :param city_data: данные о городе
    :param checkin: дата прибытия
    :param checkout: дата уезда
    :param count: количество отелей
    :param sort: тип сортировки отелей
    :param max_price: максимальная цена отеля
    :param min_price: минимальная цена отеля

    :type city_data: dict
    :type checkin: List[Int]
    :type checkout: List[Int]
    :type count: int
    :type sort: str
    :type max_price: int
    :type min_price: int

    :return: список отелей с информацией о них
    """
    logger.debug(f'Поиск отелей в городе {city_data["name"]}')

    url = "https://hotels4.p.rapidapi.com/properties/v2/list"

    headers = {
        "X-RapidAPI-Key": HOTELS_API_KEY,
        'X-RapidAPI-Host': HOTELS_API_HOST
    }

    params = {
        "currency": "USD",
        "eapid": 1,
        "locale": "ru_RU",
        "siteId": 300000001,
        "destination": {"regionId": city_data['city_id']},
        "checkInDate": {
            "day": checkin[0],
            "month": checkin[1],
            "year": checkin[2]
        },
        "checkOutDate": {
            "day": checkout[0],
            "month": checkout[1],
            "year": checkout[2]
        },
        "rooms": [
            {
                "adults": 1,
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": count,
        "sort": sort,
        "filters": {"price": {
            "max": max_price,
            "min": min_price
        }}
    }

    response = requests.request("POST", url, headers=headers, json=params)
    data = json.loads(response.text)
    logger.debug("Пользователь получил список отелей")

    return data


def get_hotel_info(hotel_id: str):
    """
    Функция получения информации об отеле по его id
    :param hotel_id: id отеля
    :type hotel_id: str
    :return: информация об отеле
    """
    logger.debug(f'Получение информации об отеле с id {hotel_id}')

    url = "https://hotels4.p.rapidapi.com/properties/v2/detail"

    params = {
        "currency": "USD",
        "eapid": 1,
        "locale": "ru_RU",
        "siteId": 300000001,
        "propertyId": hotel_id
    }
    headers = {
        "X-RapidAPI-Key": HOTELS_API_KEY,
        "X-RapidAPI-Host": HOTELS_API_HOST
    }

    response = requests.request("POST", url, headers=headers, json=params)
    data = json.loads(response.text)
    logger.debug('Получена информация об отеле')

    return data
