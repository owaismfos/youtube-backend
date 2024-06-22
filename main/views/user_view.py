from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed

from django.contrib.auth.hashers import make_password, check_password

from main.models.user_model import User
from main.models.video_model import Video
from main.models.subscription_model import Subscription
from main.models.channel_model import Channel
from main.utils.cloudinary import uploadOnCloudinry, deleteFromCloudinry
from main.utils.api_response import apiResponse
from main.utils.api_error import apiError
from main.auth.authenticate import authenticate
import jwt
import os

class UserView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        data = request.data
        print(data)
        print(data.get('fullname'))
        print("User avatar", data.get('avatar'))
        if data.get('fullname') is None or data.get('email') is None or data.get('username') is None or data.get('password') is None or data.get('avatar') is None:
            return Response(apiError(400, "All fields are required!"),
                            status = status.HTTP_400_BAD_REQUEST)
                
        if User.getUserByEmail(data.get('email')) is not None:
            return Response(apiError(400, "This email already exist"),
                            status = status.HTTP_400_BAD_REQUEST)
        
        if User.getUserByUsername(data.get('username')) is not None:
            return Response(apiError(400, "This username already exist"),
                            status = status.HTTP_400_BAD_REQUEST)
        
        res = uploadOnCloudinry(data.get('avatar'), 'user_avatar')
        # print(res)
        if res is None:
            return Response(apiError(500,
                                     "internal server error to upload images"), 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        data['avatar'] = res.get('url')
        data['avatar_id'] = res.get('public_id')
        user = User.create_user(data)
        print("User: ", user)
        # print(user.to_dict())
        return Response(apiResponse(201, 
                                    "create succesfully", 
                                    user.to_dict()), 
                        status = status.HTTP_201_CREATED)
        
        # return Response({'msg':'test'})
    
    
class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        user = authenticate(request.data.get('username'), request.data.get('password'))
        if user is None:
            return Response(apiError(401, "Invalid Credentials"),
                            status=status.HTTP_401_UNAUTHORIZED)
            
            
        accessToken, tokenExpiry = user.generateAccessToken()
        refreshToken = user.generateRefreshToken()

        user.refreshToken = refreshToken
        user.save()
        
        data = {
            'accessToken' : accessToken,
            'refreshToken' : refreshToken,
            'tokenExpiry': tokenExpiry,
            'user' : user.username,
            'userAvatar' : user.avatar
        }
        
        return Response(apiResponse(200,
                                    "Logged in successfully",
                                    data),
                        status = status.HTTP_200_OK)

class LogoutView(APIView):
    def post(self, request):
        # print(request.META.get('HTTP_AUTHORIZATION'))
        user = User.getUserById(request.user._id)
        if user is None:
            return Response(apiError(401, "Invalid Credentials"),
                            status=status.HTTP_401_UNAUTHORIZED)
        user.refreshToken = ''
        user.save()
        
        return Response(apiResponse(200, "Logout successfully"), 
                        status=status.HTTP_200_OK)


class RefreshedAccessTokens(APIView):
    permission_classes = [AllowAny]
    def get_token_from_request(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header.split(' ')[1]
        return None
    
    def post(self, request):
        refreshToken = self.get_token_from_request(request)
        if refreshToken is None:
            return Response(apiError(401, "Token is required"), status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            tokenSecretKey = os.getenv('TOKEN_SECRET')
            payload = jwt.decode(refreshToken, tokenSecretKey, algorithms=['HS256']) ## decode the token
            print(payload)
        except jwt.ExpiredSignatureError:
            return Response(apiError(401, "Token has expired"), status=status.HTTP_401_UNAUTHORIZED)
            # raise AuthenticationFailed('Refresh token has expired')
        except jwt.InvalidTokenError as e:
            # print("Invalid token:", str(e))
            return Response({"status":"failed"})
            # raise AuthenticationFailed('Refresh token is invalid')
        
        try:
            user_id = payload.get('id')
            user = User.getUserById(user_id)
            print('get user instance')
            if user.refreshToken != refreshToken:
                return Response(apiError(401, "Refresh token is invalid"), status=status.HTTP_401_UNAUTHORIZED)
                # raise AuthenticationFailed('Refresh token is invalid')
            (accessToken, tokenExpiry) = user.generateAccessToken()
            tokens = {
                'accessToken': accessToken,
                'refreshToken': user.generateRefreshToken(),
                'tokenExpiry': tokenExpiry
            }
            user.refreshToken = tokens['refreshToken']
            user.save()
        except User.DoesNotExist:
            return Response(apiError(401, 'User does not exist'), status=status.HTTP_401_UNAUTHORIZED)
            # raise AuthenticationFailed('User not found')
        
        
        return Response(apiResponse(200, "Tokens generate successfully", tokens),
                        status=status.HTTP_200_OK)
        
    
class ResetPassword(APIView):
    def post(self, request):
        oldPassword = request.data.get('old_password')
        newPassword = request.data.get('new_password')
        
        # print("oldPassword: %s newPassword: %s" % (oldPassword, newPassword))
        
        user = User.getUserById(request.user.id)
        
        isPasswordCorrect = check_password(oldPassword, user.password)
        
        if isPasswordCorrect is False:
            return Response(apiError(304, "wrong password"), status=status.HTTP_304_NOT_MODIFIED)
        
        user.password = make_password(newPassword)
        user.save()
        
        return Response(apiResponse(200, "Password changed successfully"), status=status.HTTP_200_OK)
    
class UpdateAvatar(APIView):
    def post(self, request):
        avatar = request.data.get('avatar')
        
        user = User.getUserById(request.user.id)
        
        removeAvatar = deleteFromCloudinry(user.avatar_id)
        
        if removeAvatar is None:
            return Response(apiError(500, 'Internal Sever Error'), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        uploadAvatar = uploadOnCloudinry(avatar)
        if uploadAvatar is None:
            return Response(apiError(500, 'Internal Sever Error'), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        user.avatar = uploadAvatar.get('url')
        user.avatar_id = uploadAvatar.get('public_id')
        user.save()
        
        data = {
            'avatar': user.avatar
        }
        
        return Response(apiResponse(200, 'upload avatar successfully', data), status=status.HTTP_200_OK)
    

class UserProfile(APIView):
    def get(self, request):
        # print(request.user)
        user = User.getUserById(request.user._id)
        if user is None:
            return Response(apiError(401, 'User does not exist'), status=status.HTTP_401_UNAUTHORIZED)
        
        response = user.to_dict()
        if Channel.isChannelExistOfUser(user._id) is True:
            channel = Channel.getChannelOfUserId(user._id)
            response['isChannel'] = True
            response['channelId'] = channel._id
            response['channelHandle'] = channel.channelHandle
        else:
            response['isChannel'] = False
        
        return Response(apiResponse(200, 'get user profile successfully', response), status=status.HTTP_200_OK)


class GetLoggedInUserAvatar(APIView):
    def get(self, request):
        userId = request.user._id
        user = User.getUserById(userId)
        if user is None:
            return Response(apiError(401, 'User does not exist'), status=status.HTTP_401_UNAUTHORIZED)
        return Response(apiResponse(200, "OK", user.avatar), status=status.HTTP_200_OK)