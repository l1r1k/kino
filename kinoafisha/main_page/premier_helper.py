import json
import requests
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

from .models import Movie, Genre, Country, Sessions
from django.db.models import Q
from django.utils import timezone

from io import BytesIO
from PIL import Image

# Путь до корневой папки django
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_DIR = BASE_DIR / 'kinoafisha'

load_dotenv(ENV_DIR)

# Получение URL до API Премьер зала и ключа для доступа к запросам
PREMIER_BASE_URL = os.environ.get('PREMIER_BASE_URL', '')
PREMIER_API_KEY = os.environ.get('PREMIER_API_KEY', '')

# URL API Премьер зала
BASE_URL = PREMIER_BASE_URL + PREMIER_API_KEY

# URL-пути до эндпоинтов API Премьер зала
SESSIONS_URL = BASE_URL + '/sessions?showPrices=true&api_key=' + PREMIER_API_KEY
MOVIES_URL = BASE_URL + '/movies?api_key=' + PREMIER_API_KEY
MEDIA_DATA_URL_BASE = BASE_URL + '/mediaData?api_key=' + PREMIER_API_KEY + '&id='
HALL_BUSY_SEATS_BASE = BASE_URL + '/hm/halls/status?api_key=' + PREMIER_API_KEY + '&sessionId='


AGE_CONSTRAINTS = {
    '0+': 'ZC',
    '6+': 'SC',
    '12+': 'TC',
    '16+': 'STC',
    '18+': 'EC',
}

def get_free_place_count(session_id):
    """
    Получение количества свободных мест на сеанс
    """
    response = requests.get(f'{HALL_BUSY_SEATS_BASE}{session_id}')
    
    response.raise_for_status()
    
    json_result = response.json()

    free_place_count = json_result['Hall']['Levels'][0]['FreePlaceCount']

    if free_place_count:
        return free_place_count
    
    return -1

def get_media_parts(id, movie_id) -> Path:
    """
    Скачивание медиафайлов фильма
    """
    response = requests.get(f'{MEDIA_DATA_URL_BASE}{id}')

    response.raise_for_status()

    content_type = response.headers.get('Content-Type', '')

    filename = f'{movie_id}'
    filepath = BASE_DIR / 'media'

    if 'image/jpeg' in content_type:
        image = Image.open(BytesIO(response.content))
        max_width = 899
        max_height = 1289

        image.thumbnail((max_width, max_height), Image.LANCZOS)

        filename += '.jpeg'
        filepath = Path(filepath) / 'images' / filename

        image.save(filepath)

        relative_path = Path('images') / filename
    else:
        return None

    return relative_path

def get_movies():
    """
    Получение всех фильмов, которые есть в БД Премьер Зала
    """
    response = requests.get(MOVIES_URL)

    response.raise_for_status()

    movies = response.json()

    movies_important_info = []

    for movie in movies:
        # удаление ненужной информации и очистка имени от возврастного ограничения
        movie['Name'] = movie['Name'][:len(movie['Name']) - 4]
        del movie['Rental']
        del movie['KinoplanId']
        del movie['PzApiId']
        movies_important_info.append(movie)

    return movies_important_info

def get_movies_sessions():
    """
    Получение всех сеансов на 3 дня с Премьер Зала
    """
    response = requests.get(SESSIONS_URL)

    response.raise_for_status()

    sessions = response.json()

    sessions_by_date = {}

    for session in sessions:
        # Хранение полученных сеансов фильмов с API Премьер зала по дням в порядке
        # возрастания времени сеанса
        session_date = datetime.strptime(session['DateTime'], '%Y-%m-%dT%H:%M:%S').date()

        if session_date not in sessions_by_date.keys():
            sessions_by_date[session_date] = []

        sessions_by_date[session_date].append(session)

    return sessions_by_date

def create_movie_from_premier_zal_json_to_orm_model(
        id: int, name: str, duration: int, story: str, rate: str, 
        media_datas: list, genres: list, directors: list, 
        countries: list, cast: list, pushkin_id: str):
    """
    Добавление фильма из БД Премьер Зала, если фильма нет в локальной БД
    """

    if not id or not name:
        raise Exception('Невозможно выполнить добавление записи фильма, т.к. отсутствует значение у обязательных полей:\n'
                        f'{id=}; {name=}')
    
    relative_paths = []
    
    for media_data in media_datas:
        relative_path = get_media_parts(media_data['Id'], id)

        if relative_path:
            afisha_or_trailer = 'Афиша' if '.jpeg' in str(relative_path) else 'Трейлер'
            print(f'{afisha_or_trailer} фильма {name} успешно загружен!')
            relative_paths.append(relative_path)

    print(f'Добавление записи фильма {name}')

    movie = Movie.objects.create(
        name=name, description=story, short_description=story[:story.find('.')] if story else None,
        age_constraint=AGE_CONSTRAINTS[rate], published_year=1,
        is_allow_pushkin_card= True if pushkin_id else False,
        movie_id_premier=id, movie_duration=duration, movie_cast=cast,
        pushkin_id=pushkin_id, movie_directors=directors
        )

    print(f'Запись фильма {name} успешно добавлена в локальную БД с первичным ключом {movie.pk}')

    for genre in genres:
        genre = genre.capitalize()
        genre_from_db = Genre.objects.get_or_create(
            name=genre,
            defaults={'name': genre}
        )

        movie.genres.add(genre_from_db[0])

        print(f'Жанр {genre_from_db[0].name} добавлен к фильму {name}!')

    for country in countries:
        country = country.capitalize()
        country_from_db = Country.objects.get_or_create(
            name=country,
            defaults={'name': country}
        )

        movie.countries.add(country_from_db[0])

        print(f'Страна {country_from_db[0].name} добавлена к фильму {name}!')

    for relative_path in relative_paths:
        relative_path_str = str(relative_path)
        if '.jpeg' in relative_path_str:
            movie.afisha.name = relative_path_str
            print(f'Путь {relative_path} добавлен к фильму {name}!')

    movie.save()


def add_movies_from_premier_zal_to_local_db():
    """
    Функция проверки появления новых фильмов в БД Премьер Зала
    Если новый фильм появился, то добавляется в локальную БД
    """
    movies_from_premier_zal = get_movies()

    for movie in movies_from_premier_zal:
        movie_in_local_db = Movie.objects.filter(movie_id_premier=movie['Id'])

        if not movie_in_local_db:
            create_movie_from_premier_zal_json_to_orm_model(
                id=movie['Id'], name=movie['Name'], duration=movie['Duration'],
                story=movie['Story'], rate=movie['Rate'],
                media_datas=movie['MediaDatas'], genres=movie['Genres'],
                directors=movie['Directors'],
                countries=movie['Countries'], cast=movie['Cast'],
                pushkin_id=movie['PushkinId']
            )

def create_session_from_premier_zal_json_to_orm_model(
        session_id: int, session_date: datetime, session_time: datetime,
        session_price: int, session_format: str, movie_id: int
):
    """
    Добавление сеансов фильмов из БД Премьер Зала в локальную БД
    """
    if not session_id or not session_date or not session_time or not session_price or not movie_id:
        raise Exception('Невозможно добавить сеанс, т.к. отсутствует значение у обязательных полей:\n' \
        f'{session_id=}; {session_date=}; {session_time=}; {session_price=}; {movie_id=}')

    movie = Movie.objects.get(movie_id_premier=movie_id)

    if movie:
        session = Sessions()
        session.session_id = session_id
        session.session_date = session_date
        session.session_time = session_time
        session.session_price = session_price
        session.format_session = session_format
        session.movie = movie

        session.save()


def add_sessions_from_premier_zal_to_local_db():
    """
    Добавление сеансов фильмов с Премьер зала в локальную БД, если сеанса нет
    """
    sessions_from_premier_zal = get_movies_sessions()

    for sessions_date in sessions_from_premier_zal.keys():
        for session in sessions_from_premier_zal[sessions_date]:
            session_in_local_db = Sessions.objects.filter(session_id=session['Id'])

            if not session_in_local_db:
                datetime_from_json = datetime.strptime(session['DateTime'], '%Y-%m-%dT%H:%M:%S')

                session_date = datetime_from_json.date()
                session_time = datetime_from_json.time()

                for price in session['Prices']:
                    if price['TicketName'] == 'Взрослый':
                        session_price = price['Sum']
                        break
                else:
                    session_price = 0
                

                create_session_from_premier_zal_json_to_orm_model(
                    session_id=session['Id'], session_date=session_date,
                    session_time=session_time, session_price=session_price,
                    session_format=session['Format']['Name'],
                    movie_id=session['MovieId']
                )

def delete_sessions_if_them_left():
    current_datetime = timezone.localtime(timezone.now())
    current_date = current_datetime.date()
    current_time = current_datetime.time()

    Sessions.objects.filter(
        Q(session_date__lte=current_date, session_time__lte=current_time) |
        Q(session_date__lte=current_date)
    ).delete()

