Для развертывания сайта киноафиши необходимо:

1. Скопироть репозиторий на хостинг
2. Создать .env файл на уровне файла settings.py (kinoafisha/kinoafisha/.env)
3. Заполнить файл своими данными (пример будет в ТГ)
4. Догрузить необходимые библиотеки из файла requirements.txt
5. Создать миграции
6. Выполнить миграции
7. Создать суперпользователя
8. В файле kinoafisha/kinoafisha/settings.py изменить allowed_hosts, оставить локальные, убрать IP моего хоста, добавить айпи и домен своего хоста
9. Собрать и запустить локально redis

   9.1. Перейти в папку redis-stable
   9.2. Выполнить команду make MALLOC=libc
   9.3. После успешной сборки запустить redis с помошью команды src/redis-server --daemonize yes
   9.4. Проверить, запустился ли redis, через команду src/redis-cli ping, в ответ в консоли должен быть выведен PONG

10. Выдать права доступа на запуск ffmpeg и ffprobe

   10.1. chmod +x ffmpeg/ffmpeg-7.0.2-amd64-static/ffmpeg
   10.2. chmod +x ffmpeg/ffmpeg-7.0.2-amd64-static/ffprobe
   
11. Запустить celery-worker

   11.1. Первый celery-worker, который будет обрабатывать задачу по разбиению на части трейлера nohup celery -A kinoafisha worker -l info > worker.log 2>&1 &
   11.2. Второй celery-beat-worker, который запустит в фоне задачу по проверке наличия новых фильмох на API Премьер Зала и задачу по удалению уже пройденных сеансов nohup celery -A kinoafisha beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler > beat.log 2>&1 &
   
15. Запустить django через gunicorn. nohup gunicorn kinoafisha.wsgi:application --bind unix:/var/www/kinoafisha/gunicorn.sock --log-level info --access-logfile /var/www/kinoafisha/logs/access.log --error-logfile /var/www/kinoafisha/logs/error.log &
16. Настроить nginx на обработку запросов на сайт киноафиши
