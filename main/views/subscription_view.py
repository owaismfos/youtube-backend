from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from main.models.video_model import Video
from main.models.subscription_model  import Subscription
from main.utils.cloudinary import uploadOnCloudinry, deleteFromCloudinry
from main.utils.api_response import apiResponse
from main.utils.api_error import apiError


class SubscriptionView(APIView):
    def get(self, request, channelId):
        subscribers = Subscription.getSubscriberCount(channelId)
        isSubscribed = Subscription.isSubscribed(channelId, request.user._id)
        data = {
            'isSubscribed': isSubscribed,
            'subscribersCount': subscribers
        }
        print(subscribers)
        return Response(apiResponse(200, "Subscribers fetch successfully", data), status=status.HTTP_200_OK)

    def post(self, request, channelId):
        # channelId = request.data.get('channelId')
        subscriberId = request.user._id
        
        if channelId is None or subscriberId is None:
            return Response(apiError(400, 'bad request'), status=status.HTTP_400_BAD_REQUEST)
        
        subscribe = Subscription.subscribeChannel(subscriberId, channelId)
        if subscribe is None:
            return Response(apiError(500, 'internal server error'), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(apiResponse(200, 'channel subscribed'), status=status.HTTP_200_OK)

class UnsubscribeChannel(APIView):
    def post(self, request, channelId):
        # channelId = request.data.get('channelId')
        subscriberId = request.user._id
        
        if channelId is None or subscriberId is None:
            return Response(apiError(400, 'bad request'), status=status.HTTP_400_BAD_REQUEST)
        
        unsubscribe = Subscription.unsubscribeChannel(channelId, subscriberId)
        if unsubscribe is False:
            return Response(apiError(500, 'internal server error'), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(apiResponse(200, 'channel unsubscribed'), status=status.HTTP_200_OK)

class GetChannelsSubscribedByUser(APIView):
    def get(self, request):
        subscriptions = Subscription.getSubscriptions(request.user._id)
        return Response(apiResponse(200, "OK", subscriptions), status=status.HTTP_200_OK)
