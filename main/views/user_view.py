from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Sum, Q
from django.db import connection

from main.models.user_model import User
from main.models.video_model import Video
from main.models.subscription_model import Subscription
from main.models.channel_model import Channel
from main.utils.cloudinary import uploadOnCloudinry, deleteFromCloudinry
from main.utils.api_response import apiResponse
from main.utils.api_error import apiError
from main.auth.authenticate import authenticate

from datetime import datetime
import jwt
import os

class UserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data.copy()
        print(data)
        if not all([data.get('fullname'), data.get('email'), data.get('username'), data.get('password')]):
            return Response(apiError(400, "All fields are required!"),
                            status = status.HTTP_400_BAD_REQUEST)

        if User.getUserByEmail(data.get('email')) is not None:
            return Response(apiError(400, f"This email already exist `{data.get('email')}`"),
                            status = status.HTTP_400_BAD_REQUEST)

        if User.getUserByUsername(data.get('username')) is not None:
            return Response(apiError(400, f"This username already exist `{data.get('username')}`"),
                            status = status.HTTP_400_BAD_REQUEST)

        if data.get('avatar') is not None:
            res, msg = uploadOnCloudinry(data.get('avatar'), os.getenv('USER_AVATAR'))
            print(msg)
            print(res)
            if res is None:
                return Response(apiError(500, msg),
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            data['avatarUrl'] = res.get('url')
            data['avatarId'] = res.get('public_id')

        fullname = data.get('fullname')
        firstName, lastName = (fullname.split(' ', 1) + [None])[:2]
        data['firstName'] = firstName
        data['lastName'] = lastName
        user = User.create_user(data)
        print("User: ", user)
        # print(user.to_dict())
        if user is None:
            deleteFromCloudinry(res.get('public_id'))
            return Response(apiError(500,
                                     "internal server error to create user"),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # user.password =  make_password(data.get('password'))
        # user.save()
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
        user.lastLogin = datetime.now()
        user.save()

        data = {
            'id': user.id,
            'accessToken' : accessToken,
            'refreshToken' : refreshToken,
            'tokenExpiry': tokenExpiry,
            'user' : user.username,
            'userAvatar' : user.avatarUrl
        }

        return Response(apiResponse(200,
                                    "Logged in successfully",
                                    data),
                        status = status.HTTP_200_OK)

class LogoutView(APIView):
    def post(self, request):
        # print(request.META.get('HTTP_AUTHORIZATION'))
        user = User.getUserById(request.user.id)
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
        try:
            # print(request.user)
            user = User.getUserById(request.user.id)
            if user is None:
                return Response(apiError(401, 'User does not exist'), status=status.HTTP_401_UNAUTHORIZED)

            response = user.to_dict()
            if Channel.isChannelExistOfUser(user.id):
                channel = Channel.getChannelOfUserId(user.id)
                response['isChannel'] = True
                response['channelId'] = channel.id
                response['channelHandle'] = channel.channelHandle
            else:
                response['isChannel'] = False

            return Response(apiResponse(200, 'get user profile successfully', response), status=status.HTTP_200_OK)
        except Exception as e:
            return Response(apiError(500, str(e)), status=500)


class GetLoggedInUserAvatar(APIView):
    def get(self, request):
        userId = request.user.id
        user = User.getUserById(userId)
        if user is None:
            return Response(apiError(401, 'User does not exist'), status=status.HTTP_401_UNAUTHORIZED)
        return Response(apiResponse(200, "OK", user.avatar), status=status.HTTP_200_OK)


class UserList(APIView):
    # permission_classes = [AllowAny]
    def get(self, request):
        userId = request.user.id
        query = """SELECT 
                        u.id,
                        CONCAT(u.firstName, ' ', IFNULL(u.lastName, '')) AS fullname,
                        u.email,
                        CONCAT('@', u.username) AS username,
                        u.avatarUrl,
                        u.createdAt,
                        u.updatedAt,
                        IFNULL(mus.visitCount, 0) AS visitCount,
                        COUNT(CASE 
                            WHEN m.receiver = %s AND m.isRead = 0
                            THEN 0
                        END) AS unreadMessageCount
                    FROM Users u
                    LEFT JOIN MessageUserStatus mus ON mus.user = u.id
                    LEFT JOIN Messages m ON m.sender = u.id
                    WHERE u.id != %s
                    GROUP BY u.id, u.firstName, u.lastName, u.email, u.username, u.avatarUrl, u.createdAt, u.updatedAt, mus.visitCount;"""
        with connection.cursor() as cursor:
            cursor.execute(query, [userId, userId])
            cols = [col[0] for col in cursor.description]
            data = [dict(zip(cols, row)) for row in cursor.fetchall()]
        return Response(apiResponse(200, "OK", data), status=200)
    

class UserSearch(APIView):
    def get(self, request):
        query = request.query_params.get('query')
        print("query: ", query)
        if query is None:
            return Response(apiError(400, "Query parameter is required"), status=400)

        query_parts = query.split()

        # If there are two parts, search firstName and lastName
        if len(query_parts) > 1:
            users = User.objects.filter(
                Q(firstName__icontains=query_parts[0]) & 
                Q(lastName__icontains=query_parts[1])
            ).exclude(id=request.user.id)
        else:
            # If only one part, search in both firstName and lastName
            users = User.objects.filter(
                Q(firstName__icontains=query) | 
                Q(lastName__icontains=query)
            ).exclude(id=request.user.id)
        
        data = [user.to_dict() for user in users]
        return Response(apiResponse(200, "OK", data), status=200)
    

class PasswordResetRequestView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data.get('email')
        print(email)
        if not email:
            return Response(apiError(400, "Email is required"), status=status.HTTP_400_BAD_REQUEST)

        user = User.getUserByEmail(email)
        if not user:
            return Response(apiError(404, "User not found"), status=status.HTTP_404_NOT_FOUND)
        
        print("usrid: ", user.id)
        user.last_login = user.lastLogin
        user.get_email_field_name = lambda: 'email'
        uid = urlsafe_base64_encode(force_bytes(str(user.id)))
        pk = urlsafe_base64_decode(uid).decode()
        print("pk: ", pk, type(pk))
        print(uid)
        token = default_token_generator.make_token(user)
        resetUrl = f"http://localhost:8080/api/v1/users/password-reset-confirm/{uid}/{token}"
        print("Reset URL: ", resetUrl)
        send_mail(
            subject="Reset Your Password",
            message=f"Click the link to reset your password: {resetUrl}",
            from_email="mohammad.owais@oodles.io",
            recipient_list=[email],
        )
        # Generate a password reset token and send it to the user's email
        # This part is omitted for brevity
        response = {
            'resetLink':  resetUrl
        }

        return Response(apiResponse(200, "Password reset link sent to your email", response), status=status.HTTP_200_OK)
    


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        password = request.data.get("password")
        print("uidb64: ", uidb64)
        print("token: ", token)
        if not password:
            return Response({"error": "Password is required."}, status=400)
        
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.getUserById(uid)
            user.get_email_field_name = lambda: 'email'
            user.last_login = user.lastLogin

            if default_token_generator.check_token(user, token):
                user.password = make_password(password)
                user.save()
                return Response({"message": "Password reset successful."})
            else:
                return Response({"error": "Invalid or expired token."}, status=400)
        except Exception as e:
            print("Error during password reset:", str(e))
            return Response({"error": "Invalid request."}, status=400)