from django.urls import path
from . import consumers  # Assurez-vous que ce chemin est correct
from django.urls import re_path

websocket_urlpatterns = [
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
]
