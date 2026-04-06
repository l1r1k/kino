import shutil
import subprocess
from pathlib import Path
from celery import shared_task
from django.conf import settings
from .premier_helper import add_movies_from_premier_zal_to_local_db, add_sessions_from_premier_zal_to_local_db, delete_sessions_if_them_left

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / 'media' / 'hls'
INPUT_DIR = BASE_DIR

def remove_old_hls(movie_id):
    hls_path = OUTPUT_DIR / str(movie_id)
    if hls_path.exists():
        shutil.rmtree(hls_path)
        print(f"🧹 Удалены старые HLS файлы для фильма {movie_id}")

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=5, max_retries=3)
def convert_to_hls_task(self, movie_id, file_url, delete_old=False):
    try:
        if delete_old:
            remove_old_hls(movie_id)

        file_path = INPUT_DIR.joinpath(*file_url.split('/'))
        output_path = OUTPUT_DIR / str(movie_id)
        output_path.mkdir(parents=True, exist_ok=True)

        print(f"🎬 [Celery] Конвертация {file_path} → {output_path}/index.m3u8")

        subprocess.run([
            settings.FFMPEG_PATH,
            "-i", str(file_path),
            "-profile:v", "baseline",
            "-level", "3.0",
            "-start_number", "0",
            "-hls_time", "5",
            "-hls_list_size", "0",
            "-f", "hls",
            str(output_path / "index.m3u8")
        ], check=True)

        print(f"✅ [Celery] Завершено для фильма {movie_id}")

    except Exception as e:
        print(f"❌ Ошибка конвертации: {e}")
        raise self.retry(exc=e)

@shared_task
def check_new_movies():
    """
    Проверяет наличие новых фильмов на внешнем API и добавляет их в локальную БД
    """
    add_movies_from_premier_zal_to_local_db()

    add_sessions_from_premier_zal_to_local_db()

@shared_task
def delete_old_sessions():
    """
    Удаляет из БД старые сеансы фильмов
    """
    delete_sessions_if_them_left()
