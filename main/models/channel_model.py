from django.db import models

from main.models.user_model import User

import uuid
import datetime


class Channel(models.Model):
    channelName = models.CharField(
        max_length = 100,
        db_column = 'channelName',
        null = True,
    )

    channelHandle = models.CharField(
        max_length = 100,
        db_column = 'channelHandle',
        null = True
    )

    channelDescription = models.TextField(db_column='channelDescription')

    channelAvatarUrl = models.CharField(
        max_length = 5000,
        db_column = 'channelAvatarUrl',
        null = True
    )

    channelAvatarId = models.CharField(
        max_length = 200,
        db_column = 'channelAvatarId',
        null = True
    )

    channelBackgroundUrl = models.CharField(
        max_length = 5000,
        db_column = 'channelBackgroundUrl',
        null = True
    )

    channelBackgroundId = models.CharField(
        max_length = 200,
        db_column = 'channelBackgroundId',
        null = True
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, db_column='userId')
    createAt = models.DateTimeField(auto_now_add=True, db_column='createAt')
    updateAt = models.DateTimeField(auto_now=True, db_column='updateAt')

    class Meta:
        db_table = 'Channels'

    def to_dict(self):
        return {
            'id': self.id,
            'channelName': self.channelName,
            'channelHandle': self.channelHandle,
            'channelDescription': self.channelDescription,
            'channelAvatarUrl': self.channelAvatarUrl,
            'channelBackgroundUrl': self.channelBackgroundUrl,
            'user': {
                'userId': self.user.id,
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
        return Channel.objects.filter(user = userId).exists()

    @classmethod
    def getChannelOfUserId(cls, userId):
        try:
            return Channel.objects.get(user = userId)
        except Exception as e:
            return None

    @classmethod
    def getChannelById(cls, channelId):
        try:
            return Channel.objects.get(id = channelId)
        except Exception as e:
            return None
