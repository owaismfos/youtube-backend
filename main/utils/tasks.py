from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.core.files import File
from django.forms.models import model_to_dict
from celery import shared_task
import subprocess
import os
from main.models.message_model import Messages
from django.conf import settings
import asyncio
import time

@shared_task
def videoCompression(messageId, group_name, userId, videoDuration):
    try:
        message = Messages.objects.get(id=messageId)
        inputPath = message.mediaFile.path
        outputPath = inputPath.replace(".mp4", "_compressed.mp4")

        print("group_name: ", group_name)
        print("Compression Started")
        cppVideoCompressorPath = str(settings.BASE_DIR) + '/main/cppModule/videoCompressor'

        process = subprocess.Popen(
                [cppVideoCompressorPath, inputPath, outputPath], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True,
                bufsize=1)
        
        channelLayer = get_channel_layer()
        previousProgress = 0

        for line in iter(process.stdout.readline, ""):
            if "Progress:" in line:
                progress = line.strip().split("Progress:")[-1].strip()
                duration = progress.split('=')[-1].strip()
                hours, minutes, seconds = map(float, duration.split(":"))
                totalSeconds = int(hours * 3600 + minutes * 60 + seconds)
                currentProgress = int((totalSeconds / videoDuration) * 100)
                print(f"Total Seconds: {totalSeconds}")
                if previousProgress < currentProgress and currentProgress <= 100:
                    previousProgress = currentProgress
                    async_to_sync(channelLayer.group_send)(
                        group_name,
                        {
                            "type": "chat_message",
                            "message": {"action": "send_progress", "progress": currentProgress, 'userId': userId}
                        }
                    )
        process.stdout.close()
        process.wait()  # Wait for the process to complete
        print('Process return code : ', process.returncode)
        if process.returncode == 0:
            print("Compression successful")
        else:
            print("Compression failed")
        with open(outputPath, 'rb') as f:
            message.mediaFile.save(f"compressed_{os.path.basename(inputPath)}", File(f), save=True)
            message.uploaded = True
            message.save()

        messageObject = model_to_dict(message)
        messageObject['mediaFile'] = os.getenv('SERVER_DOMAIN') + message.mediaFile.url if message.mediaFile else None
        messageObject['insertedAt'] = message.insertedAt.strftime('%Y-%m-%d %H:%M:%S')
        message_data = {'data': messageObject, 'action': 'new_message'}
        async_to_sync(channelLayer.group_send)(
            group_name,
            {
                "type": "chat_message",
                "message": message_data
            }
        )
        os.remove(inputPath)
        os.remove(outputPath)
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
