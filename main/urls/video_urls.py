from django.urls import path

from main.views.video_view import *
from main.views.subscription_view import *
from main.views.comment_view import *
from main.views.like_view import *
from main.views.channel_view import *


urlpatterns = [
    path('upload-video', VideoView.as_view()),
    path('get-video/<str:videoId>', VideoView.as_view()),
    path('update-video/<str:videoId>', VideoView.as_view()),
    path('update-thumbnail/<str:videoId>', VideoView.as_view()),
    path('update-video-detail/<str:videoId>', VideoView.as_view()),
    path('delete-video/<str:videoId>', VideoView.as_view()),
    path('get-videos-of-channel/<str:channelId>', GetVideosOfChannel.as_view()),

    ##Get View of perticular video
    path('get-views/<str:videoId>', ViewsOfVideo.as_view()),
    path('update-views/<str:videoId>', ViewsOfVideo.as_view()),

    ## Channel Details
    path('channel/<str:channelName>', ChannelDetails.as_view()),
    
    ## All videos urls
    path('all-videos', AllVideosView.as_view()),
    
    ## Subscription urls
    # path('subscribe-channel/<int:channelId>', SubscriptionView.as_view()),
    # path('unsubscribe-channel/<int:channelId>', UnsubscribeChannel.as_view()),
    # path('get-subscribers/<int:channelId>', SubscriptionView.as_view()),
    # path('get-subscribe-channels-list-of-current-user', GetChannelsSubscribedByUser.as_view()),
    
    ## Comment urls
    path('get-comments/<str:videoId>', CommentView.as_view()),
    path('comment/<str:videoId>', CommentView.as_view()),

    ## like video urls
    path('likes/<str:videoId>', LikeView.as_view()),
    path('like-video/<str:videoId>', LikeView.as_view()),
    path('unlike-video/<str:videoId>', UnlikeView.as_view()),


    ### Channels Urls
    path('create-channel', ChannelView.as_view()),
    path('get-channel-details', GetChannelDetails.as_view()),
    path('get-channel-details-by-id/<str:channelId>', GetChannelDetails.as_view()),
]
