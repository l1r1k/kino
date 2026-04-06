import requests
import json
import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_DIR = BASE_DIR.parent

load_dotenv(ENV_DIR)

KINOPOISK_JSONS_DIR = BASE_DIR / 'info'

KINOPOISK_UNOFFICIAL_API_KEY = os.environ.get('KINOPOISK_API_KEY', '')

FILM_INFO_BASE_URL = 'https://kinopoiskapiunofficial.tech/api/v2.2/films/'
FILM_FACTS_INCLUDE_PATH = '/facts'
FILM_VIDEOS_INCLUDE_PATH = '/videos'
FILM_ACTORS_BASE_URL = 'https://kinopoiskapiunofficial.tech/api/v1/staff?filmId='
RATING_KEY = 'ratingKinopoisk'
FILM_LENGTH_KEY = 'filmLength'

HEADERS = {'X-API-KEY': KINOPOISK_UNOFFICIAL_API_KEY}

def update_kinopoisk_ratings(kinopoisk_films_ids: dict[int, int]):
    for id, kinopoisk_film_id in kinopoisk_films_ids.items():
        response = requests.get(f'{FILM_INFO_BASE_URL}{kinopoisk_film_id}', headers=HEADERS)
        response = response.json()
        with open(KINOPOISK_JSONS_DIR / f'{id}.json', 'r', encoding='utf-8') as file:
            json_from_file = json.load(file)
            json_from_file['kinopoisk_rating'] = response[RATING_KEY]

        with open(f'{id}.json', 'w', encoding='utf-8') as file:
            json.dump(json_from_file, file, indent=4, ensure_ascii=False)

        

def info_about_film_from_kinopoisk(kinopoisk_film_id: int, film_id: int):
    response = requests.get(f'{FILM_INFO_BASE_URL}{kinopoisk_film_id}', headers=HEADERS)
    response = response.json()
    print(f'{ENV_DIR=}')
    print(f'{KINOPOISK_UNOFFICIAL_API_KEY=}')
    rating_kinopoisk = response[RATING_KEY]
    film_length = response[FILM_LENGTH_KEY]

    response = requests.get(f'{FILM_INFO_BASE_URL}{kinopoisk_film_id}{FILM_FACTS_INCLUDE_PATH}', headers=HEADERS)
    response = response.json()
    film_facts = []
    for fact in response['items']:
        if not fact['spoiler']:
            film_facts.append({fact['type']: fact['text']})

    response = requests.get(f'{FILM_ACTORS_BASE_URL}{kinopoisk_film_id}', headers=HEADERS)
    response = response.json()
    major_actors = []
    i = 0
    for actor in response:
        if actor['professionKey'] == 'ACTOR':
            if actor['nameRu'] and actor['nameRu'] != '':
                major_actors.append(actor['nameRu'])
            i += 1

        if i == 5:
            break

    info_about_film = {
        'kinopoisk_rating': rating_kinopoisk,
        'film_length': film_length,
        'film_facts': film_facts,
        'major_actors': major_actors
    }

    with open(KINOPOISK_JSONS_DIR / f'{film_id}.json', 'w', encoding='utf-8') as file:
        json.dump(info_about_film, file, indent=4, ensure_ascii=False)
   