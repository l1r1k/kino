from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest
from django.utils import timezone
from django.db.models import Q, Subquery

from .models import Movie, Genre, Country, Sessions
from .helpers import get_next_week_dates
from .premier_helper import get_free_place_count

import os
from datetime import timedelta
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_DIR = BASE_DIR.parent

load_dotenv(ENV_DIR)

PRISMA_THEATRE_ID = os.environ.get('PRISMA_THEATRE_ID', '')
PRISMA_FILM_ID = os.environ.get('PRISMA_FILM_ID', '')
THEATRE_ID = os.environ.get('THEATRE_ID', '')

# Create your views here.

def get_kinoafisha_context(request):
    genre_ids = request.GET.getlist('genres')
    country_ids = request.GET.getlist('countries')
    selected_date = request.GET.get('selected_date')
    only_pushkin_card = request.GET.get('only_pushkin_card')

    week = get_next_week_dates()

    free_places = {}

    if not selected_date or not selected_date.isnumeric() or int(selected_date) < 0:
        selected_date = week[0]
        selected_date_number = 0
    elif int(selected_date) > 6:
        selected_date = week[2]
        selected_date_number = 6
    else:
        selected_date_number = int(selected_date)
        selected_date = week[selected_date_number]

    sessions = Sessions.objects.filter(
        session_date=selected_date['date_obj']
    ).all()

    for session in sessions:
        if session.session_id > 0:
            free_places[session.session_id] = get_free_place_count(session.session_id)

    movies = Movie.objects.filter(
        pk__in=Subquery(sessions.values('movie'))
    ).all()

    all_genres = Genre.objects.all()
    all_countries = Country.objects.all()

    selected_genres = all_genres.filter(id__in=genre_ids) if genre_ids else None
    selected_countries = all_countries.filter(id__in=country_ids) if country_ids else None

    if selected_genres and selected_genres.exists():
        movies = movies.filter(genres__in=selected_genres).distinct()

    if selected_countries and selected_countries.exists():
        movies = movies.filter(countries__in=selected_countries).distinct()

    if only_pushkin_card == '1':
        movies = movies.filter(is_allow_pushkin_card=True)

    context = {
        'movies': movies,
        'sessions': sessions,
        'free_places': free_places,
        'week_days': week,
        'selected_date': selected_date,
        'selected_date_number': selected_date_number,
        'genres': all_genres,
        'selected_genres': selected_genres,
        'countries': all_countries,
        'selected_countries': selected_countries,
        'only_pushkin_card': only_pushkin_card,
        'current_filters': request.GET.copy(),
        'theatre_id': THEATRE_ID,
        'prisma_theatre_id': PRISMA_THEATRE_ID,
        'prisma_film_id': PRISMA_FILM_ID,
    }

    return context

def index(request: HttpRequest):
    today = timezone.localtime(timezone.now())
    last_day_for_ending_movies = today + timedelta(days=2)
    tomorrow = today + timedelta(days=1)

    sessions = Sessions.objects.filter(
        Q(session_date__lte=today, session_time__lte=today.time())
    ).all()

    movies = Movie.objects.all().filter(is_visiable=True).order_by('pk')

    upcoming_movies = movies.filter(
        rental_start__gte = tomorrow
    )

    ending_movies = movies.filter(
        rental_end__gte = today,
        rental_end__lte = last_day_for_ending_movies
    )

    current_movies = movies.filter(
        sessions__isnull=False
    ).distinct()

    for movie in current_movies:
        print(movie.name)

    context = {
        'upcoming_movies': upcoming_movies,
        'ending_movies': ending_movies,
        'current_movies': current_movies
    }

    context.update(get_kinoafisha_context(request))

    return render(request, 'index.html', context=context)


def movie_detail(request, pk: int):
    movie = get_object_or_404(Movie, pk=pk)

    movie_sessions = Sessions.objects.filter(movie=movie).all()

    sessions = {}

    for movie_session in movie_sessions:
        if movie_session.session_id > 0:
            free_place = get_free_place_count(movie_session.session_id)

            if movie_session.session_date not in sessions.keys():
                sessions[movie_session.session_date] = []
            pair = (movie_session, free_place)
            sessions[movie_session.session_date].append(pair)

    today = timezone.localdate(timezone.now())

    print(sessions)

    context = {
        'movie': movie,
        'src': None,
        'today': today,
        'movie_sessions': sessions,
        'theatre_id': THEATRE_ID,
        'prisma_theatre_id': PRISMA_THEATRE_ID,
        'prisma_film_id': PRISMA_FILM_ID,
    }

    return render(request, 'movie_detail.html', context=context)

def ticket_refund(request):
    return render(request, 'ticket_refund.html')

def info(request):
    return render(request, 'info.html')

def kinopoisk_artist_redirect(request, artist_id):
    return redirect(f'https://www.kinopoisk.ru/name/{artist_id}/')

def kinopoisk_movie_redirect(request, movie_id):
    return redirect(f'https://www.kinopoisk.ru/film/{movie_id}/')
