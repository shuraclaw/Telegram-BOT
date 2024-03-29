# Инструкция по эксплуатации скрипта и бота

## Описание
Этот проект представляет собой телеграм-бота, который помогает найти отель в заданном городе по заданным параметрам: датам пребывания, бюджету, расположению, сортировке по цене и т.д.
Бот работает с помощью API, которое предоставляет данные по отелям.

---
## Установка
Для использования данного проекта необходимо установить библиотеки, которые используются в проекте.

---
## Запуск скрипта
Для запуска скрипта необходимо запустить файл **bot.py** с помощью команды:
```commandline
python bot.py
```

---
## Использование
- После запуска бота, вы можете ввести следующие команды:

  - `/help` - выводит информацию об использовании бота.
  - `/lowprice` - выводит самые дешевые отели в городе.
  - `/highprice` - выводит самые дорогие отели в городе.
  - `/bestdeal` - выводит отели, наиболее подходящие по цене и расположению от центра.
  - `/history` - выводит историю команд (название, время и название отелей).

- При выборе команды `/lowprice`, `/highprice`, `/bestdeal` бот запрашивает у пользователя следующие параметры:

  - Название города
  - Даты приезда и отъезда
  - Диапазон цен между минимальной и максимальной
  - Диапазон расстояния от центра города
  - Количество фотографий
  - Даты прибытия и убытия в формате `DD-MM-YYYY`

- В случае успешного поиска отелей, бот выводит список отелей, соответствующих заданным параметрам, вместе с их названием, адресом, ценой, расстоянием от центра и т.д.