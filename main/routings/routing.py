from django.urls import re_path
from main.consumers.chat_consumer import ChatConsumer
from main.consumers.user_list_consumer import UserListConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/', ChatConsumer.as_asgi()),  # WebSocket URL
    re_path(r'ws/update-user-list', UserListConsumer.as_asgi())
]