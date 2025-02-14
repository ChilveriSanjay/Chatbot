from django.urls import re_path
from bot.consumers import TestWebSocket

websocket_urlspatterns=[
    re_path(r'ws/test/$',TestWebSocket.as_asgi()),
]