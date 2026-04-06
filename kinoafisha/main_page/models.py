from django.db import models
from datetime import datetime
from django.core.exceptions import ValidationError

from django.db.models.signals import post_delete
from .cleanup_handler import file_cleanup

# Create your models here.
class Genre(models.Model):
    name = models.CharField(max_length=150, verbose_name="Название жанра")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

class Country(models.Model):
    name = models.CharField(max_length=150, verbose_name='Название страны')

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Страна'
        verbose_name_plural = 'Страны'

def current_year():
    return datetime.now().year

class Movie(models.Model):
    SMALL_HALL = 'SH'
    BIG_HALL = 'BH'
    TYPE_HALL = [
        (SMALL_HALL, 'Маленький зал'),
        (BIG_HALL, 'Большой зал')
    ]

    ZERO_CONSTRAINT = 'ZC'
    SIX_CONSTRAINT = 'SC'
    TWELVE_CONSTRAINT = 'TC'
    SIXTEEN_CONSTRAINT = 'STC'
    EIGHTTEEN_CONSTRAINT = 'EC'

    TYPE_CONSTRAINT = [
        (ZERO_CONSTRAINT, '0+'),
        (SIX_CONSTRAINT, '6+'),
        (TWELVE_CONSTRAINT, '12+'),
        (SIXTEEN_CONSTRAINT, '16+'),
        (EIGHTTEEN_CONSTRAINT, '18+')
    ]

    def __str__(self):
        return self.name

    name = models.CharField(max_length=256, verbose_name='Название фильма')
    description = models.TextField(max_length=1024, verbose_name='Описание фильма', blank=True, null=True, default='Отсутствует')
    short_description = models.TextField(max_length=256, verbose_name='Краткое описание фильма', blank=True, null=True, default='Отсутствует')
    afisha = models.ImageField(upload_to='images', verbose_name='Афиша фильма', blank=True, null=True, default='Отсутствует')
    name_movie_logo = models.ImageField(upload_to='logos', verbose_name='Логотип названия фильма',
                                        help_text='Прикрепите логотип названия фильма, который будет отображаться на главной странице (только .png)',
                                        default='Отсутствует', blank=True)
    background_afisha = models.ImageField(upload_to='posters', verbose_name='Фоновый постер фильма', 
                                          help_text='Прикрепите постер фильма, который будет отображаться на главной странице сайта',
                                          default='Отсутствует')
    trailer = models.FileField(upload_to='trailers', verbose_name='Трейлер',
                               help_text='Прикрепите трейлер фильма в формате .mp4. Принимаются только файлы с названием на латинице!',
                               default='Отсутствует')
    genres = models.ManyToManyField(Genre, verbose_name='Жанры фильма')
    countries = models.ManyToManyField(Country, verbose_name='Страны производители фильма')
    age_constraint = models.CharField(max_length=3, choices=TYPE_CONSTRAINT, default=TWELVE_CONSTRAINT, verbose_name='Возрастные ограничения')
    hall = models.CharField(max_length=2, choices=TYPE_HALL, default=SMALL_HALL, verbose_name='Зал, в котором проходит сеанс')
    is_visiable = models.BooleanField(default=True, verbose_name='Фильм в прокате?')
    is_allow_pushkin_card = models.BooleanField(default=False, verbose_name='Можно по Пушкинской карте?')
    published_year = models.PositiveSmallIntegerField(default=current_year, verbose_name='Год выхода фильма')
    rental_start = models.DateField(verbose_name='Дата начала проката', null=True, blank=True)
    rental_end = models.DateField(verbose_name='Дата окончания проката', null=True, blank=True)
    # Данные получаемые с API Премьер Зала
    movie_id_premier = models.PositiveIntegerField(verbose_name='Код фильма из премьер зала', unique=True, help_text='Уникальный код фильма из Базы Данных Премьер Зала. 0 - если фильм не из Базы Данных Премьер Зала', blank=True, null=True, default=0)
    movie_directors = models.JSONField(
        verbose_name='Режиссеры фильма', 
        help_text='Укажите всех режиссеров фильма', 
        default=list,  # Заменяет blank=True на уровне логики списка
        blank=True, 
        null=True
    )
    movie_cast = models.JSONField(
        verbose_name='Каст актеров', 
        help_text='Укажите главных актеров фильма', 
        default=list, 
        blank=True, 
        null=True
    )
    pushkin_id = models.CharField(max_length=24,verbose_name='Код пушкинской карты',help_text='Укажите код полученный при регистрации показа фильма с помощью пушкинской карты, если билет нельзя оплатить Пушкинской картой - поле оставить пустым!', null=True, blank=True)
    movie_duration = models.PositiveSmallIntegerField(verbose_name='Продолжительность фильма', help_text='Укажите продолжительность фильма в минутах', blank=True, null=True)

    def clean(self):
        if self.rental_end and self.rental_start and self.rental_end < self.rental_start:
            raise ValidationError("Дата окончания проката не может быть раньше даты начала.")

    def get_all_model_fields(model):
        return model._meta.fields

    class Meta:
        verbose_name = 'Фильм'
        verbose_name_plural = 'Фильмы'

class Sessions(models.Model):
    FORMAT_2D = '2D'
    FORMAT_3D = '3D'
    MOVIE_FORMAT = [
        (FORMAT_2D, '2D'),
        (FORMAT_3D, '3D')
    ]

    def __str__(self):
        return f'{self.movie.name} - {self.session_date} {self.session_time}'

    session_id = models.PositiveIntegerField(verbose_name='Код сеанса фильма', help_text='Укажите код сеанса фильма из Базы Данных Премьер Зала')
    session_date = models.DateField(verbose_name='Дата сеанса', help_text='Укажите дату сеанса')
    session_time = models.TimeField(verbose_name='Время сеанса', help_text='Укажите время сеанса')
    session_price = models.PositiveSmallIntegerField(verbose_name='Стоимость билета', help_text='Укажите стоимость билета')
    format_session = models.CharField(verbose_name='Формат фильма', help_text='Укажите формат фильма (2D, 3D)', max_length=2, choices=MOVIE_FORMAT, default=FORMAT_2D)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name='Фильм', help_text='Выберите фильм, который будет на сеансе')

    class Meta:
        verbose_name = 'Сеанс'
        verbose_name_plural = 'Сеансы'

# Signals

post_delete.connect(
    file_cleanup, sender=Movie, dispatch_uid='movie.afisha.file_cleanup'
)
