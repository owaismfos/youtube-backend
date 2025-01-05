import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack  # Import routing from chat app
from main.middlewares.authchat_middleware import JwtAuthMiddleware
from main.consumers.chat_consumer import ChatConsumer
from django.urls import path
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JwtAuthMiddleware(
        URLRouter([
            path('ws/chat/', ChatConsumer.as_asgi()),
        ])
    ),
})
