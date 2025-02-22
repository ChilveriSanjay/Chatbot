"""
ASGI config for chatbot project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import bot.routing  # Import WebSocket routing from your app

os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'chatbot.settings')

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),  # Handles HTTP requests
        "websocket": AuthMiddlewareStack(
        URLRouter(
            bot.routing.websocket_urlspatterns  # Use your app's routing file
        )
    )
    }
)
