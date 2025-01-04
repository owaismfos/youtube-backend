from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from main.models.channel_model import Channel

from main.utils.api_response import apiResponse
from main.utils.api_error import apiError
from main.utils.cloudinary import uploadOnCloudinry

import os

class ChannelView(APIView):
    def post(self, request):
        print(request.data)
        if Channel.isChannelExistOfUser(request.user.id) is True:
            return Response(apiError(400, "channel exist with this user"), status=400)
        data = {
            'userId' : request.user.id,
            'channelName' : request.data.get('channelName'),
            'channelDescription' : request.data.get('channelDescription'),
            'channelAvatarUrl' : None,
            'channelAvatarId' : None,
            'channelBackgroundUrl' : None,
            'channelBackgroundId' : None
        }
        channelAvatar = request.data.get('channelAvatar')
        print("Channel Avatar: ", type(channelAvatar))
        if channelAvatar is not None:
            avatarResponse = uploadOnCloudinry(channelAvatar, os.getenv('CHANNEL_AVATAR'))
            if avatarResponse is None:
                return Response(apiError(500, 'internal server error for uploading avatar'), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            data['channelAvatarUrl'] = avatarResponse.get('url')
            data['channelAvatarId'] = avatarResponse.get('public_id')

        channelBackground = request.data.get('channelBackground')
        print("Channel Background Image: ", channelBackground)
        if channelBackground is not None:
            backgroundResponse = uploadOnCloudinry(channelBackground, os.getenv('CHANNEL_BACKGROUND'))
            if backgroundResponse is None:
                return Response(apiError(500, 'internal server error for uploading background image'), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            data['channelBackgroundUrl'] = backgroundResponse.get('url')
            data['channelBackgroundId'] = backgroundResponse.get('public_id')

        print("Data: ", data)
        channel = Channel.createChannel(data)
        # channel.save()
        return Response(apiResponse(200, 'channel created successfully', channel), status=200)


class GetChannelDetails(APIView):
    def get(self, request, channelId=None):
        try:
            print("Channel ID: ", channelId)
            print("User ID: ", request.user.id)
            if channelId is None:
                # if Channel.isChannelExistOfUser(request.user.id) is False:
                #     return Response(apiError(400, "channel not exist with this user"), status=400)

                channel = Channel.getChannelOfUserId(request.user.id)
                print(channel)
                if channel is None:
                    return Response(apiError(404, "channel not exist with this user"), status=404)

                channel = channel.to_dict()
                if (channel['user']['userId'] == request.user.id):
                    channel['currentUser'] = True
                else:
                    channel['currentUser'] = False
                return Response(apiResponse(200, 'channel retrieved successfully', channel), status=200)

            else:
                channel = Channel.getChannelById(channelId)
                if channel is None:
                    return Response(apiError(400, "channel not exist"), status=400)
                channel = channel.to_dict()
                if (channel['user']['userId'] == request.user.id):
                    channel['currentUser'] = True
                else:
                    channel['currentUser'] = False
                return Response(apiResponse(200, 'channel retrieved successfully', channel), status=200)
        except Exception as e:
            return Response(apiError(500, str(e)), status=500)


class UploadBackgroundImage(APIView):
    def post(self, request):
        userId = request.user.id
        backgroundImage = request.data.get('backgroundImage')
        print("Background Image: ", backgroundImage)
        if backgroundImage is None:
            return Response(apiError(400, "background image not provided"), status=400)

        backgroundResponse = uploadOnCloudinry(backgroundImage, 'channel_background')
        if backgroundResponse is None:
            return Response(apiError(500, 'internal server error for uploading background image'), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        channel = Channel.getChannelOfUserId(userId)
        channel.channelBackgroundUrl = backgroundResponse.get('url')
        channel.channelBackgroundId = backgroundResponse.get('public_id')
        channel.save()

        return Response(apiResponse(200, 'background image uploaded successfully', channel.channelBackgroundUrl), status=200)


class UploadAvatarImage(APIView):
    def post(self, request):
        try:
            userId = request.user.id
            avatarImage = request.data.get('avatarImage')
            print("Avatar Image: ", avatarImage)
            if avatarImage is None:
                return Response(apiError(400, "avatar image not provided"), status=400)

            avatarResponse = uploadOnCloudinry(avatarImage, os.getenv('CHANNEL_AVATAR'))
            print(avatarResponse)
            if avatarResponse is None:
                return Response(apiError(500, 'internal server error for uploading avatar image'), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            channel = Channel.getChannelOfUserId(userId)
            print(channel)
            channel.channelAvatarUrl = avatarResponse.get('url')
            channel.channelAvatarId = avatarResponse.get('public_id')
            channel.save()

            return Response(apiResponse(200, 'avatar image uploaded successfully', channel.channelAvatarUrl), status=200)
        except Exception as e:
            return Response(apiError(500, str(e)), status=500)


class ChangeChannelName(APIView):
    def post(self, request):
        userId = request.user.id
        channelName = request.data.get('channelName')
        print("Channel Name: ", channelName)
        if channelName is None:
            return Response(apiError(400, "channel name not provided"), status=400)

        channel = Channel.getChannelOfUserId(userId)
        channel.channelName = channelName
        channel.save()

        return Response(apiResponse(200, 'channel name changed successfully', channel.channelName), status=200)
