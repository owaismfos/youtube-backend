from django.db import models

from main.models.user_model import User

import uuid
import datetime


class Channel(models.Model):
    _id = models.CharField(
        primary_key = True, 
        default = uuid.uuid4().hex, 
        editable = False,
        max_length = 32
        )
    
    channelName = models.CharField(
        max_length = 100, 
        db_column = 'channel_name', 
        null = True,
        )
    
    channelHandle = models.CharField(
        max_length = 100, 
        db_column = 'channel_handle', 
        null = True
        )
    
    channelDescription = models.TextField(db_column='channel_description')

    channelAvatarUrl = models.CharField(
        max_length = 5000, 
        db_column = 'channel_avatar_url', 
        null = True
        )
    
    channelAvatarId = models.CharField(
        max_length = 200, 
        db_column = 'channel_avatar_id', 
        null = True
        )
    
    channelBackgroundUrl = models.CharField(
        max_length = 5000,
        db_column = 'channel_background_url', 
        null = True
        )
    
    channelBackgroundId = models.CharField(
        max_length = 200, 
        db_column = 'channel_background_id', 
        null = True
        )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, db_column='user_id')
    createAt = models.DateTimeField(auto_now_add=True, db_column='create_at')
    updateAt = models.DateTimeField(auto_now=True, db_column='update_at')

    class Meta:
        db_table = 'Channels'

    def to_dict(self):
        return {
            '_id': self._id,
            'channelName': self.channelName,
            'channelHandle': self.channelHandle,
            'channelDescription': self.channelDescription,
            'channelAvatarUrl': self.channelAvatarUrl,
            'channelBackgroundUrl': self.channelBackgroundUrl,
            'user': {
                'userId': self.user._id,
                'username': self.user.username
            }
        }


    @classmethod
    def createChannel(cls, data):
        channel = Channel.objects.create(channelName = data['channelName'],
                                        channelHandle = str(data['channelName']).replace(' ', ''),
                                        channelDescription = data['channelDescription'], 
                                        channelAvatarUrl = data['channelAvatarUrl'], 
                                        channelAvatarId = data['channelAvatarId'], 
                                        channelBackgroundUrl = data['channelBackgroundUrl'], 
                                        channelBackgroundId = data['channelBackgroundId'], 
                                        user_id = data['userId'])
        channel.save()
        return channel.to_dict()

    @classmethod
    def isChannelExistOfUser(cls, userId):
        return Channel.objects.filter(user_id = userId).exists()

    @classmethod
    def getChannelOfUserId(cls, userId):
        try:
            return Channel.objects.get(user_id = userId)
        except Exception as e:
            return None

    @classmethod
    def getChannelById(cls, channelId):
        try:
            return Channel.objects.get(_id = channelId)
        except Exception as e:
            return None
