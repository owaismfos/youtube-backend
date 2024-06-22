from django.db import models
from .user_model import User
from .video_model import Video


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, db_column='video_id')
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Likes'

    def to_dict(self):
        return {
            'id': self.id,
            'user': {
                'userId': self.user._id,
                'avatarUrl': self.user.avatar,
                'username': '@' + self.user.username,
            },
            'videoId': self.video._id,
            # 'createdAt': self.createdAt.strftime('%Y-%m-%d %H:%M:%S')
        }

    @classmethod
    def likeVideo(cls, userId, videoId):
        like = Like.objects.create(user_id=userId, video_id=videoId)
        like.save()
        return like.to_dict()

    @classmethod
    def unlikeVideo(cls, userId, videoId):
        try:
            like = Like.objects.get(user_id=userId, video_id=videoId)
            like.delete()
            return True
        except Exception as e:
            return False


    @classmethod
    def likesCountOfVideo(cls, videoId):
        likesCount = Like.objects.filter(video_id=videoId).count()
        return likesCount

    @classmethod
    def isLikedVideo(self, userId, videoId):
        try:
            isLiked = Like.objects.get(user_id=userId, video_id=videoId)
            return True
        except Exception as e:
            return False
        # return Liked.objects.get(user_id=userId, video_id=videoId)