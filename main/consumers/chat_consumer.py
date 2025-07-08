# chat/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
from django.forms.models import model_to_dict
from django.core.files.base import ContentFile
from django.utils.timezone import now
from django.core.files import File
from django.db import connection
from django.conf import settings
from django.db.models import Q

from asgiref.sync import sync_to_async

from ..models.message_model import Messages
from ..models.message_model import MessageUserStatus

from datetime import datetime
import subprocess
import asyncio
import json
import time
import os

from main.utils.tasks import videoCompression

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # This method will be called when the WebSocket is handshaking as a connection is established
        self.user = self.scope['user']
        name = f'chat_{self.user.id}_{self.scope["receiverId"]}'

        sorted_name = ''.join(sorted(name))
        self.group_name = sorted_name
        print("Group Name: ", self.group_name)
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
        
        await sync_to_async(self.update_undread_messages)()

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',
                'message': {'action': 'user_status', 'data': user_status}
            }
        )
        # await sync_to_async(Messages.objects.filter(sender=self.scope["receiverid"], receiver=self.user.id, isRead=False).update(isRead=True))
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
        await sync_to_async(Messages.objects.filter(sender=self.scope["receiverid"], receiver=self.user.id, isRead=False).update(isRead=True))
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # This method is called when the WebSocket receives a message
        try:
            data = json.loads(text_data)
            action = data['action']
            # print("Data: ", data)
            if action == 'get_messages':
                try:
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
                            ).filter(uploaded=True)
                        ]
                    )()
                    await self.send(text_data=json.dumps({'data': messages, 'action': 'get_messages'}))
                except Exception as e:
                    print(str(e))
                    raise ValueError(e)
            
            elif action == 'post_message':
                contentType = data.get('mediaType')
                if data.get('type') == 'text':
                    result = await sync_to_async(Messages.objects.create)(
                        sender_id=self.user.id, 
                        receiver_id=self.scope['receiverId'],
                        content=data.get('textData'),
                        uploaded=True
                    )
                elif data.get('type') == 'media':
                    # print("media data: ", data.get('mediaFile'))
                    fileData = bytes(data.get('mediaFile'))
                    contentType = data.get('mediaType')
                    # print("file_data: ", file_data)
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    if contentType == 'image':
                        fileName = f"image_{timestamp}_file.png"  # Set your desired file name with extension
                    elif contentType == 'video':
                        fileName = f"video_{timestamp}_file.mp4"
                    elif contentType == 'audio':
                        fileName = f"audio_{timestamp}_file.mp3"
                    contentFile = ContentFile(fileData, name=fileName)
                    print("content file: ", contentFile)
                    # file_data = ContentFile()
                    print('Content Type: ', contentType)
                    try:
                        result = await sync_to_async(Messages.objects.create)(
                            sender_id=self.user.id, 
                            receiver_id=self.scope['receiverId'],
                            contentType=contentType,
                            content=data.get('textData') if data.get('textData') != '' else None,
                            mediaFile=contentFile,
                            uploaded= False if contentType == 'video' else True
                        )
                    except Exception as e:
                        print(str(e))
                        raise ValueError(e)
                    
                    if contentType == 'video':
                        print("Video Process")
                        duration = int(data.get('duration'))
                        if duration > 0:
                            resutl = videoCompression.delay(result.id, self.group_name, self.user.id, duration)
                message = model_to_dict(result)
                message['mediaFile'] = os.getenv('SERVER_DOMAIN') + result.mediaFile.url if result.mediaFile else None
                message['insertedAt'] = result.insertedAt.strftime('%Y-%m-%d %H:%M:%S')
                await self.send(text_data=json.dumps({'data': message, 'action': 'post_message'}))

                if contentType != 'video':
                    message_data = {'data': message, 'action': 'new_message'}
                    await self.channel_layer.group_send(
                        self.group_name,
                        {
                            'type': 'chat_message',
                            'message': message_data,  
                        }
                    )
                    users = await sync_to_async(self.get_user_list)()
                    if users:
                        print("User List: ", users)
                        user_data = {'data': users, 'action': 'user_list'}
                        await self.channel_layer.group_send(
                                self.group_name,
                                {
                                    'type': 'chat_message',
                                    'message': user_data,  
                                }
                            )
                        # await self.send(text_data=json.dumps({'data': users, 'action': 'user_list'}))

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
            elif action == 'type_message':
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'chat_message',
                        'message': data
                    }
                )
            elif action == 'call':
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'call_message',
                        'message': data
                    }
                )
        except Exception as e:
            await self.send(text_data=json.dumps({"action": "error_message", "message": str(e)}))
    
    async def chat_message(self, event):
        # Send the message to WebSocket
        message = event['message']
        await self.send(text_data=json.dumps({'data': message}))

    async def call_message(self, event):
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

    def update_undread_messages(self):
        try:
            unread_messages = Messages.objects.filter(receiver=self.scope['user'], isRead=False)
            unread_messages.update(isRead=True)
        except Exception as e:
            print(str(e))

    def receiver_status(self):
        try:
            status = MessageUserStatus.objects.filter(user=self.scope['receiverId']).first()
            return status
        except Exception as e:
            print(str(e))
            return None

    def get_user_list(self):
        try:
            userId = self.scope["receiverId"]
            query = """SELECT 
                            u.id,
                            CONCAT(u.firstName, ' ', IFNULL(u.lastName, '')) AS fullname,
                            u.email,
                            CONCAT('@', u.username) AS username,
                            u.avatarUrl,
                            u.createdAt,
                            u.updatedAt,
                            IFNULL(mus.visitCount, 0) AS visitCount,
                            COUNT(CASE 
                                WHEN m.receiver = %s AND m.isRead = 0
                                THEN 0
                            END) AS unreadMessageCount
                        FROM Users u
                        LEFT JOIN MessageUserStatus mus ON mus.user = u.id
                        LEFT JOIN Messages m ON m.sender = u.id
                        WHERE u.id != %s
                        GROUP BY u.id, u.firstName, u.lastName, u.email, u.username, u.avatarUrl, u.createdAt, u.updatedAt, mus.visitCount;"""
            with connection.cursor() as cursor:
                cursor.execute(query, [userId, userId])
                cols = [col[0] for col in cursor.description]
                data = [dict(zip(cols, row)) for row in cursor.fetchall()]
            for user in data:
                user['createdAt'] = user['createdAt'].strftime('%Y-%m-%d %H:%M:%S')
                user['updatedAt'] = user['updatedAt'].strftime('%y-%m-%d %H:%M:%S')
            return data
        except Exception as e:
            print(str(e))
            return None

