from rest_framework.exceptions import AuthenticationFailed
from main.models.user_model import User

import jwt
import os


class RefreshTokenAuth:
    def authenticate(self, request):
        # print(request.META.get('HTTP_AUTHORIZATION'))
        token = self.get_token_from_request(request)
        print(token)
        if token is None:
            return None
        
        print("authjwt is testing every request")
        # if self.is_token_blacklisted(token):
        #     # print("token is blacklist")
        #     raise AuthenticationFailed('Token is invalid')

        try:
            tokenSecretKey = os.getenv('REFRESH_TOKEN_SECRET')
            payload = jwt.decode(token, tokenSecretKey, algorithms=['HS256']) ## decode the token
            # print(payload)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired', 401)
        except jwt.InvalidTokenError as e:
            print("Invalid token:", str(e))
            raise AuthenticationFailed('Token is invalid', 401)

        user_id = payload.get('id')
        user = User.getUserById(user_id)
        
        if user is None:
            raise AuthenticationFailed('User not found', 401)
        
        if user.refreshToken == '':
            raise AuthenticationFailed('Token invalid or used', 401)
        
        user.avatar_id = None
        user.password = None
        user.refreshToken = None
        user.fullname = None

        return (user, None)

    def get_token_from_request(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header.split(' ')[1]
        return None
    
    # def authenticate_header(self, request):
    #     print("authenticate header")
    #     pass