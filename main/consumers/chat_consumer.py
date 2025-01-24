# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.forms.models import model_to_dict
from asgiref.sync import sync_to_async
from django.db.models import Q
from django.core.files.base import ContentFile
from ..models.message_model import Messages
from datetime import datetime
from ..models.message_model import MessageUserStatus
from django.utils.timezone import now
import os

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # This method will be called when the WebSocket is handshaking as a connection is established
        self.user = self.scope['user']
        print("receiver Id : ", self.scope['receiverId'])
        # receverUser = await sync_to_async(Messages.objects.filter(id = self.scope['receiverId']))()
        # print("receiver User : ", receverUser.username)
        name = f'chat_{self.user.id}_{self.scope["receiverId"]}'
        sorted_name = ''.join(sorted(name))
        print(sorted_name)
        self.group_name = sorted_name
        print(self.group_name)
        # if self.user.is_authenticated:
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        status = await sync_to_async(self.update_user_status)(self.user, isActive=True)
        if status is not None:
            user_status = model_to_dict(status)
            user_status['lastActive'] = status.lastActive.strftime('%Y-%m-%d %H:%M:%S')
        else:
            user_status = None

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',
                'message': {'action': 'user_status', 'data': user_status}
            }
        )
        await self.accept()  # Allow the connection if the user is authenticated

    async def disconnect(self, close_code):
        user = self.scope['user']
        # if user.is_authenticated:
        status = await sync_to_async(self.update_user_status)(user, isActive=False)
        # status = await sync_to_async(self.receiver_status)()
        if status is not None:
            user_status = model_to_dict(status)
            user_status['lastActive'] = status.lastActive.strftime('%Y-%m-%d %H:%M:%S')
        else:
            user_status = None

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',
                'message': {'action': 'user_status', 'data': user_status}
            }
        )

    async def receive(self, text_data):
        # This method is called when the WebSocket receives a message
        data = json.loads(text_data)
        action = data['action']

        if action == 'get_messages':
            messages = await sync_to_async(
                lambda: [
                    {
                        **model_to_dict(msg),  # Convert the message object to a dictionary
                        'mediaFile': os.getenv('SERVER_DOMAIN') + msg.mediaFile.url if msg.mediaFile else None, # Handle mediaFile field
                        'insertedAt': msg.insertedAt.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    for msg in Messages.objects.filter(
                        Q(sender=self.user.id, receiver=self.scope['receiverId']) |
                        Q(sender=self.scope['receiverId'], receiver=self.user.id)
                    )
                ]
            )()
            await self.send(text_data=json.dumps({'data': messages, 'action': 'get_messages'}))
        
        elif action == 'post_message':
            if data.get('type') == 'text':
                result = await sync_to_async(Messages.objects.create)(
                    sender_id=self.user.id, 
                    receiver_id=self.scope['receiverId'],
                    content=data.get('textData')
                )
            elif data.get('type') == 'media':
                # print("media data: ", data.get('mediaFile'))
                file_data = bytes(data.get('mediaFile'))
                print("file_data: ", file_data)
                if data.get('mediaType') == 'image':
                    content_type = 'image'
                    file_name = f"image_{datetime.now().strftime('%Y%m%d%H%M%S')}_file.png"  # Set your desired file name with extension
                else:
                    content_type = 'video'
                    file_name = f"video_{datetime.now().strftime('%Y%m%d%H%M%S')}_file.mp4"
                content_file = ContentFile(file_data, name=file_name)
                print("content file: ", content_file)
                # file_data = ContentFile()
                print('Content Type: ', content_type)
                try:
                    result = await sync_to_async(Messages.objects.create)(
                        sender_id=self.user.id, 
                        receiver_id=self.scope['receiverId'],
                        contentType=content_type,
                        content=data.get('textData') if data.get('textData') != '' else None,
                        mediaFile=content_file
                    )
                except Exception as e:
                    print(str(e))
            message = model_to_dict(result)
            message['mediaFile'] = os.getenv('SERVER_DOMAIN') + result.mediaFile.url if result.mediaFile else None
            message['insertedAt'] = result.insertedAt.strftime('%Y-%m-%d %H:%M:%S')
            await self.send(text_data=json.dumps({'data': message, 'action': 'post_message'}))

            message_data = {'data': message, 'action': 'new_message'}
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'message': message_data,  
                }
            )

        elif action == 'user_status':
            status = await sync_to_async(self.receiver_status)()
            if status is not None:
                user_status = model_to_dict(status)
                user_status['lastActive'] = status.lastActive.strftime('%Y-%m-%d %H:%M:%S')
            else:
                user_status = None

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'message': {'action': 'user_status', 'data': user_status}
                }
            )
    
    async def chat_message(self, event):
        # Send the message to WebSocket
        message = event['message']
        await self.send(text_data=json.dumps({'data': message}))

    def update_user_status(self, user, isActive=None):
        try:
            status, created = MessageUserStatus.objects.get_or_create(
                user=user,
                defaults={
                    "isActive": isActive,
                    "lastActive": now(),
                    "visitCount": 1
                }
            )
            # If the record already exists, update it
            if not created:
                status.isActive = isActive
                status.lastActive = now()
                if isActive:
                    status.visitCount += 1
                status.save()
            print("User status updated")
            return status
        except Exception as e:
            print(str(e))
            return None

    def receiver_status(self):
        try:
            status = MessageUserStatus.objects.filter(user=self.scope['receiverId']).first()
            return status
        except Exception as e:
            print(str(e))
            return None
