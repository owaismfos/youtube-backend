from django.urls import path

from main.views.video_view import *
from main.views.subscription_view import *
from main.views.comment_view import *
from main.views.like_view import *
from main.views.channel_view import *


urlpatterns = [
    path('upload-video', VideoView.as_view()),
    path('get-video/<int:videoId>', VideoView.as_view()),
    path('update-video/<int:videoId>', VideoView.as_view()),
    path('update-thumbnail/<int:videoId>', VideoView.as_view()),
    path('update-video-detail/<int:videoId>', VideoView.as_view()),
    path('delete-video/<int:videoId>', VideoView.as_view()),
    path('get-videos-of-channel/<int:channelId>', GetVideosOfChannel.as_view()),

    ##Get View of perticular video
    path('get-views/<int:videoId>', ViewsOfVideo.as_view()),
    path('update-views/<int:videoId>', ViewsOfVideo.as_view()),

    ## Channel Details
    path('channel/<int:channelName>', ChannelDetails.as_view()),
    
    ## All videos urls
    path('all-videos', AllVideosView.as_view()),
    
    ## Subscription urls
    # path('subscribe-channel/<int:channelId>', SubscriptionView.as_view()),
    # path('unsubscribe-channel/<int:channelId>', UnsubscribeChannel.as_view()),
    # path('get-subscribers/<int:channelId>', SubscriptionView.as_view()),
    # path('get-subscribe-channels-list-of-current-user', GetChannelsSubscribedByUser.as_view()),
    
    ## Comment urls
    path('get-comments/<int:videoId>', CommentView.as_view()),
    path('comment/<int:videoId>', CommentView.as_view()),

    ## like video urls
    path('likes/<int:videoId>', LikeView.as_view()),
    path('like-video/<int:videoId>', LikeView.as_view()),
    path('unlike-video/<int:videoId>', UnlikeView.as_view()),


    ### Channels Urls
    path('create-channel', ChannelView.as_view()),
    path('get-channel-details', GetChannelDetails.as_view()),
    path('get-channel-details-by-id/<int:channelId>', GetChannelDetails.as_view()),
]
