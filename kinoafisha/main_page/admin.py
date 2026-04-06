from django.contrib import admin
from .models import Genre, Country, Movie, Sessions

# Register your models here.
@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    pass

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    pass

@admin.register(Sessions)
class SessionsAdmin(admin.ModelAdmin):
    pass