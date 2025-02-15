from django.db import models

from .user_model import User
from.video_model import Video

import pytz
ist_timezone = pytz.timezone('Asia/Kolkata')


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="userId")
    video = models.ForeignKey(Video, on_delete=models.CASCADE, db_column="videoId")
    comment = models.CharField(max_length=1000)
    createdAt = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'Comments'
        # ordering = ['comment', '-createdAt']
    
    def to_dict(self):
        return {
            'id': self.id,
            'user': {
                'userId': self.user.id,
                'avatarUrl': self.user.avatarUrl,
                'username': self.user.username,
            },
            'videoId': self.video.id,
            'comment': self.comment,
            'createdAt': self.createdAt.astimezone(ist_timezone)
        }
        
    @classmethod
    def commentOnVideo(cls, userId, videoId, commentText):
        comment = Comment.objects.create(user_id=userId, 
                                         video_id=videoId,
                                         comment=commentText)
        comment.save()
        return comment.to_dict()
        
    
    @classmethod
    def comments(cls, videoId):
        comments = Comment.objects.filter(video_id=videoId)##.order_by('createdAt')
        commentsList = [
            comment.to_dict() for comment in comments
        ]
        return commentsList