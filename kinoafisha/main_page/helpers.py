from datetime import datetime, timedelta
import json
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
KINOPOISK_JSONS_DIR = BASE_DIR / 'info'

MONTHS_RU = {
    1: "января",
    2: "февраля",
    3: "марта",
    4: "апреля",
    5: "мая",
    6: "июня",
    7: "июля",
    8: "августа",
    9: "сентября",
    10: "октября",
    11: "ноября",
    12: "декабря"
}

WEEKDAYS_RU = {
    0: "Понедельник",
    1: "Вторник",
    2: "Среда",
    3: "Четверг",
    4: "Пятница",
    5: "Суббота",
    6: "Воскресенье"
}

AFISHA_LABEL = {
    'Понедельник': 'В Понедельник в прокате',
    'Вторник': 'Во Вторник в прокате',
    'Среда': 'В Среду в прокате',
    'Четверг': 'В Четверг в прокате',
    'Пятница': 'В Пятницу в прокате',
    'Суббота': 'В Субботу в прокате',
    'Воскресенье': 'В Воскресенье в прокате',
}

TAB_NAME = {
    'Понедельник': 'Киноафиша на понедельник',
    'Вторник': 'Киноафиша на вторник',
    'Среда': 'Киноафиша на среду',
    'Четверг': 'Киноафиша на четверг',
    'Пятница': 'Киноафиша на пятницу',
    'Суббота': 'Киноафиша на субботу',
    'Воскресенье': 'Киноафиша на воскресенье',
}

def get_next_week_dates():
    today = datetime.today().date()
    dates = []

    for i in range(7):
        day = today + timedelta(days=i)
        weekday_name = WEEKDAYS_RU[day.weekday()]
        full_date = f"{day.day} {MONTHS_RU[day.month]} {day.year}"

        if i == 0:
            label = "Сегодня"
        elif i == 1:
            label = "Завтра"
        elif i == 2:
            label = "Послезавтра"
        else:
            label = ""

        if i >= 0 and i <= 2:
            afisha_label = label + ' в прокате'
            tab_name = 'Киноафиша на ' + label.lower()
        else:
            afisha_label = AFISHA_LABEL[weekday_name]
            tab_name = TAB_NAME[weekday_name]

        dates.append({
            'date_obj': day,
            'weekday_name': weekday_name,
            'label': label,
            'afisha_label': afisha_label,
            'full_date': full_date,
            'tab_name': tab_name,
        })

    return dates

def parse_russian_date(date_str):
    months = {
        "января": "01", "февраля": "02", "марта": "03", "апреля": "04",
        "мая": "05", "июня": "06", "июля": "07", "августа": "08",
        "сентября": "09", "октября": "10", "ноября": "11", "декабря": "12"
    }

    date_str = date_str.replace(" г.", "").strip()
    
    parts = date_str.split()
    if len(parts) != 3:
        raise ValueError("Неверный формат даты. Ожидалось 'дд месяц гггг'.")

    day, month_name, year = parts
    if month_name not in months:
        raise ValueError(f"Неизвестное название месяца: {month_name}")

    month = months[month_name]
    formatted_date = f"{day}.{month}.{year}"
    
    return datetime.strptime(formatted_date, "%d.%m.%Y").date()

def get_src(url_vkvideo: str):
    video_path = url_vkvideo[url_vkvideo.find('-'):]
    ids = video_path.split('_')
    src = f'https://vkvideo.ru/video_ext.php?oid={ids[0]}&id={ids[1]}&hd=2'
    return src

def is_not_json_kinopoisk_info_exists(model_pk: int):
    return not os.path.isfile(KINOPOISK_JSONS_DIR / f'{model_pk}.json')

def read_info_about_film_from_kinopoisk(model_pk: int):
    if not is_not_json_kinopoisk_info_exists(model_pk):
        with open(KINOPOISK_JSONS_DIR / f'{model_pk}.json', 'r', encoding='utf-8') as file:
            json_data = json.load(file)
            return json_data
    return None
