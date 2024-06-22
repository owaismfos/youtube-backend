from django.db import models

from .user_model import User
from .channel_model import Channel
import uuid
import pytz

ist_timezone = pytz.timezone('Asia/Kolkata')


class Video(models.Model):
    _id = models.CharField(
        primary_key = True, 
        default = uuid.uuid4().hex, 
        editable = False,
        max_length = 32
        )
    
    title = models.CharField(max_length=100)

    description = models.TextField()

    video_url = models.CharField(max_length=500)

    video_id = models.CharField(max_length=100)

    thumbnail_url = models.CharField(max_length=500)

    thumbnail_id = models.CharField(max_length=100)

    duration = models.IntegerField()
    
    views = models.BigIntegerField(default=0)

    user = models.ForeignKey(
        User, 
        on_delete = models.CASCADE, 
        db_column = "user_id"
        )
    
    channel = models.ForeignKey(
        Channel, 
        on_delete = models.CASCADE, 
        db_column = "channel_id"
        )
    
    createAt = models.DateTimeField(auto_now_add=True)
    updateAt = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'Videos'

    # def save(self, *args, **kwargs):
    #     print("save method is called")
    #     video = self.getVideoById(self._id)
    #     if video is not None:
    #         print("video is found")
    #         atms = 5
    #         atm = 0
    #         while video._id == self._id and atm < atms:
    #             id = uuid.uuid4().hex
    #             print("ID: ", id)
    #             if id != video._id:
    #                 self._id = id
    #                 break
    #             atm = atm + 1

    #     print("Video user into the database", self._id)
    #     print("Print agrs in save method: ", args)
    #     print("Kwagrs: ", kwargs)
    #     super(Video, self).save(*args, **kwargs)
        
    @classmethod
    def getVideoById(self, videoId):
        try:
            return Video.objects.get(_id = videoId)
        except Exception as e:
            return None
        
    @classmethod
    def createVideo(self, data):
        try:
            video = Video.objects.create(title = data.get('title'),
                                         description = data.get('description'),
                                         video_url = data.get('video_url'),
                                         video_id = data.get('video_id'),
                                         thumbnail_url = data.get('thumbnail_url'),
                                         thumbnail_id = data.get('thumbnail_id'),
                                         duration = data.get('duration'),
                                         user_id = data.get('userId'),
                                         channel_id = data.get('channelId')
                                         )
            
            video.save()
            return video
        except Exception as e:
            print("Exception Raise: ", e)
            return None
        
    # @classmethod
    # def getAllVideoOfUser(self, userId):
    #     return Video.objects.filter(user_id = userId)
    
    @classmethod
    def getAllVideos(self):
        videos = Video.objects.all()
        videosList = [
            video.to_dict() for video in videos
        ]
        return videosList
    
    
    @classmethod
    def getAllVideosOfUser(self, userId):
        videos = Video.objects.filter(user_id = userId)
        videosList = [
            video.to_dict() for video in videos
        ]
        return videosList

    @classmethod
    def getAllVideosOfChannel(self, channelId):
        videos = Video.objects.filter(channel_id = channelId)
        videosList = [
            video.to_dict() for video in videos
        ]
        return videosList
        
    def to_dict(self):
        return {
            '_id': self._id,
            'title': self.title,
            'description': self.description,
            'videoUrl': self.video_url,
            'thumbnailUrl': self.thumbnail_url,
            'duration': self.duration,
            'views': self.views,
            'user' : {
                'userId': self.user._id,
                'username': '@' + self.user.username,
                'avatar': self.user.avatar,
            },
            'channel' : {
                'channelId': self.channel._id,
                'channelName': self.channel.channelName,
                'channelHandle': self.channel.channelHandle,
                'channelAvatarUrl': self.channel.channelAvatarUrl,
            },
            
            'createdAt': self.createAt.astimezone(ist_timezone),
            'updatedAt': self.updateAt.astimezone(ist_timezone)
        }
    