from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from channels.db import database_sync_to_async
from main.models.user_model import User  # Adjust according to your User model
import jwt
import os
from asgiref.sync import sync_to_async
# @database_sync_to_async
# def get_user(token):
#     try:
#         access_token = AccessToken(token)
#         user = User.objects.get(id=access_token['user_id'])
#         return user
#     except Exception:
#         return AnonymousUser()

class JwtAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        close_old_connections()
        query_params = parse_qs(scope["query_string"].decode())

        token = query_params.get("token", [None])[0]
        receiver_id = query_params.get("receiverId", [None])[0]
        print("receiver_id ", receiver_id)
        try:
            tokenSecretKey = os.getenv('TOKEN_SECRET')
            payload = jwt.decode(token, tokenSecretKey, algorithms=['HS256']) ## decode the token
            # print(payload)
        except jwt.ExpiredSignatureError as e:
            raise str(e)
        except jwt.InvalidTokenError as e:
            print("Invalid token:", str(e))
            raise str(e)
        
        user_id = payload.get('id')
        user = await sync_to_async(User.getUserById)(user_id)
        if user is None:
            raise str("User not found")

        user.is_authenticated = True
        scope['user'] = user
        scope['receiverId'] = int(receiver_id) if receiver_id else None

        return await super().__call__(scope, receive, send)
