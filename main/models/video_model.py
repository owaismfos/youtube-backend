from django.db import models

from .user_model import User
from .channel_model import Channel
import uuid
import pytz

ist_timezone = pytz.timezone('Asia/Kolkata')


class Video(models.Model):
    uniqueId = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
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

    video480p = models.FileField(upload_to='videos/480p/', null=True, blank=True, db_column='video480p')
    video720p = models.FileField(upload_to='videos/720p/', null=True, blank=True, db_column='video720p')
    video1080p = models.FileField(upload_to='videos/1080p/', null=True, blank=True, db_column='video1080p')
    uploadCompleted = models.BooleanField(db_column='uploadCompleted', default=False)

    createAt = models.DateTimeField(auto_now_add=True, db_column='createAt')
    updateAt = models.DateTimeField(auto_now=True, db_column='updateAt')
    
    class Meta:
        db_table = 'Videos'
        
    @classmethod
    def getVideoById(self, videoId):
        try:
            return Video.objects.get(id = videoId)
        except Exception as e:
            return None
        
    @classmethod
    def createVideo(self, data):
        try:
            video = Video.objects.create(videoTitle = data.get('title'),
                                        videDescription = data.get('description'),
                                        videoUrl = data.get('video_url'),
                                        videoId = data.get('video_id'),
                                        thumbnailUrl = data.get('thumbnail_url'),
                                        thumbnailId = data.get('thumbnail_id'),
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
            'title': self.videoTitle,
            'description': self.videDescription,
            'videoUrl': self.videoUrl,
            'thumbnailUrl': self.thumbnailUrl,
            'duration': self.duration,
            'views': self.views,
            'user' : {
                'userId': self.user.id,
                'username': '@' + self.user.username,
                'avatar': self.user.avatarUrl,
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
    