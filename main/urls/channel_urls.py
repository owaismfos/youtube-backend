from django.urls import path

from main.views.video_view import *
from main.views.subscription_view import *
from main.views.comment_view import *
from main.views.like_view import *
from main.views.channel_view import *


urlpatterns = [
    ### Channels Urls
    path('create-channel', ChannelView.as_view()),
    path('get-channel-details', GetChannelDetails.as_view()),
    path('get-channel-details-by-id/<str:channelId>', GetChannelDetails.as_view()),
    path('upload-channel-background-image', UploadBackgroundImage.as_view()),
    path('upload-channel-avatar-image', UploadAvatarImage.as_view()),
    path('change-channel-name', ChangeChannelName.as_view()),
    # path('')
]
