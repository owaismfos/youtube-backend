from django.db import models

from .user_model import User
from .channel_model import Channel
import uuid
import pytz

ist_timezone = pytz.timezone('Asia/Kolkata')


class Video(models.Model):
    videoTitle = models.CharField(max_length=100, db_column='videoTitle')
    videDescription = models.TextField(db_column='videDescription')
    videoUrl = models.CharField(max_length=500, db_column='videoUrl')
    videoId = models.CharField(max_length=100, db_column='videoId')
    thumbnailUrl = models.CharField(max_length=500, db_column='thumbnailUrl')
    thumbnailId = models.CharField(max_length=100, db_column='thumbnailId')
    duration = models.IntegerField(db_column='duration')
    views = models.BigIntegerField(default=0, db_column='views')
    user = models.ForeignKey(User, on_delete = models.CASCADE, db_column = "userId")
    channel = models.ForeignKey(Channel, on_delete = models.CASCADE, db_column = "channelId")
    createAt = models.DateTimeField(auto_now_add=True, db_column='createAt')
    updateAt = models.DateTimeField(auto_now=True, db_column='updateAt')
    
    class Meta:
        db_table = 'Videos'

    # def save(self, *args, **kwargs):
    #     print("save method is called")
    #     video = self.getVideoById(self.id)
    #     if video is not None:
    #         print("video is found")
    #         atms = 5
    #         atm = 0
    #         while video.id == self.id and atm < atms:
    #             id = uuid.uuid4().hex
    #             print("ID: ", id)
    #             if id != video.id:
    #                 self.id = id
    #                 break
    #             atm = atm + 1

    #     print("Video user into the database", self.id)
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
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'videoUrl': self.video_url,
            'thumbnailUrl': self.thumbnail_url,
            'duration': self.duration,
            'views': self.views,
            'user' : {
                'userId': self.user.id,
                'username': '@' + self.user.username,
                'avatar': self.user.avatar,
            },
            'channel' : {
                'channelId': self.channel.id,
                'channelName': self.channel.channelName,
                'channelHandle': self.channel.channelHandle,
                'channelAvatarUrl': self.channel.channelAvatarUrl,
            },
            
            'createdAt': self.createAt.astimezone(ist_timezone),
            'updatedAt': self.updateAt.astimezone(ist_timezone)
        }
    