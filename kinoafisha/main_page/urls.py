from django.urls import path, include
from .views import index, ticket_refund, kinopoisk_artist_redirect, kinopoisk_movie_redirect, movie_detail, info

urlpatterns = [
    path('', index, name='index'),
    path('ticket-refund/', ticket_refund, name='ticket_refund'),
    path('info/', info, name="info"),
    path('movie/<int:pk>/', movie_detail, name="movie_detail"),
    path('name/<int:artist_id>/', kinopoisk_artist_redirect, name='kinopoisk_artist_redirect'),
    path('film/<int:movie_id>/', kinopoisk_movie_redirect, name='kinopoisk_movie_redirect'),
]
