from django.db import models

from main.models.user_model import User

import os


def uploadMediaFileFolder(instance, filename):
    file_extension = os.path.splitext(filename)[1].lower()

    # Check file type and return corresponding folder
    if file_extension in ['.jpg', '.jpeg', '.png', '.gif']:
        return f'chat_media/images/{filename}'
    elif file_extension in ['.mp4', '.avi', '.mov']:
        return f'chat_media/videos/{filename}'
    elif file_extension in ['.mp3', '.wav', '.ogg']:
        return f'chat_media/audio/{filename}'
    else:
        return f'chat_media/others/{filename}'

class Messages(models.Model):
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
    ]

    sender = models.ForeignKey(User, db_column='sender', on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(User, db_column='receiver', on_delete=models.CASCADE, related_name='receiver')
    contentType = models.CharField(db_column='contentType', max_length=10, choices=MESSAGE_TYPES, default='text')
    content = models.TextField(db_column='content',null=True, default=None)
    mediaFile = models.FileField(db_column='mediaFile', upload_to=uploadMediaFileFolder, null=True, default=None)
    isRead = models.BooleanField(db_column='isRead', null=True, default=False)
    insertedAt = models.DateTimeField(db_column='insertedAt', auto_now_add=True)

    class Meta:
        db_table = 'Messages'
        ordering = ['-insertedAt']
