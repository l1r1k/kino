from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Movie
from .tasks import convert_to_hls_task

def is_trailer_absent(trailer_field):
    return not trailer_field or trailer_field.name == 'Отсутствует'


@receiver(pre_save, sender=Movie)
def save_old_trailer_path(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old_instance = Movie.objects.get(pk=instance.pk)
        instance._old_trailer_name = old_instance.trailer.name
    except Movie.DoesNotExist:
        instance._old_trailer_name = None


@receiver(post_save, sender=Movie)
def handle_trailer_conversion(sender, instance, created, **kwargs):

    if is_trailer_absent(instance.trailer):
        print(f"⏭️  Нет трейлера — пропуск {instance.id}")
        return

    old_trailer_name = getattr(instance, '_old_trailer_name', None)
    new_trailer_name = instance.trailer.name

    if created:
        print(f"🆕 Новая запись → отправка в Celery {instance.id}")
        convert_to_hls_task.delay(instance.id, instance.trailer.url)
        return

    if old_trailer_name == new_trailer_name:
        print(f"⚠️ Трейлер не изменился — пропуск {instance.id}")
        return

    print(f"♻️ Трейлер обновлён → Celery {instance.id}")
    convert_to_hls_task.delay(
        instance.id,
        instance.trailer.url,
        delete_old=True
    )
