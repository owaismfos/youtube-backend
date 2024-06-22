from django.urls import path

from main.views.video_view import *
from main.views.subscription_view import *
from main.views.comment_view import *
from main.views.like_view import *
from main.views.channel_view import *

urlpatterns = [
    ## Subscription urls
    path('subscribe-channel/<str:channelId>', SubscriptionView.as_view()),
    path('unsubscribe-channel/<str:channelId>', UnsubscribeChannel.as_view()),
    path('get-subscribers/<str:channelId>', SubscriptionView.as_view()),  ### 
    path('get-subscribe-channels-list-of-current-user', GetChannelsSubscribedByUser.as_view()),
]
