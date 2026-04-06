"""
URL configuration for kinoafisha project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from .settings import DEBUG, STATIC_URL, MEDIA_URL, STATIC_ROOT, MEDIA_ROOT, EMAIL_HOST_USER
from django.conf.urls.static import static

from django.conf.urls import handler400, handler403, handler404, handler500
from django.shortcuts import render
from django.core.mail import send_mail
from django.http import JsonResponse
import traceback

def custom_bad_request(request, exception):
    return render(request, "errors/400.html", status=400)

def custom_permission_denied(request, exception):
    return render(request, "errors/403.html", status=403)

def custom_page_not_found(request, exception):
    return render(request, "errors/404.html", status=404)

def custom_server_error(request):
    tb = traceback.format_exc()
    send_mail(
        subject="Ошибка 500 на сайте",
        message=f"Произошла ошибка 500 на сайте.\n\nСтек ошибки:\n{tb}",
        from_email= EMAIL_HOST_USER,
        recipient_list=["kirillperewalov@yandex.ru", EMAIL_HOST_USER],
        fail_silently=True
    )
    return render(request, "errors/500.html", status=500)

handler400 = custom_bad_request
handler403 = custom_permission_denied
handler404 = custom_page_not_found
handler500 = custom_server_error


urlpatterns = [
    path('admin-panel/', admin.site.urls),
    path('', include('main_page.urls'), name='main_page'),
]

def health(request):
    return JsonResponse({"status": "ok"})

urlpatterns += [
    path("health", health),
]

if DEBUG:
    urlpatterns += static(STATIC_URL, document_root=STATIC_ROOT)
    urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
