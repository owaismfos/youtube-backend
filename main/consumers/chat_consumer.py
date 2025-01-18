# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.forms.models import model_to_dict
from asgiref.sync import sync_to_async
from django.db.models import Q
from django.core.files.base import ContentFile
from ..models.message_model import Messages
from datetime import datetime

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
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()  # Allow the connection if the user is authenticated

    async def disconnect(self, close_code):
        # This method is called when the WebSocket closes
        # await self.channel_layer.group_discard(
        #     self.room_group_name,
        #     self.channel_name
        # )
        pass

    async def receive(self, text_data):
        # This method is called when the WebSocket receives a message
        data = json.loads(text_data)
        action = data['action']

        if action == 'get_messages':
            messages = await sync_to_async(
                lambda: [
                    {
                        **model_to_dict(msg),  # Convert the message object to a dictionary
                        'mediaFile': msg.mediaFile.url if msg.mediaFile else None, # Handle mediaFile field
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
                print("media data: ", data.get('mediaFile'))
                file_data = bytes(data.get('mediaFile'))
                print("file_data: ", file_data)
                if data.get('mediaType') == 'image':
                    file_name = f"image_{datetime.now().strftime('%Y%m%d%H%M%S')}_file.png"  # Set your desired file name with extension
                else:
                    file_name = f"video_{datetime.now().strftime('%Y%m%d%H%M%S')}_file.mp4"
                content_file = ContentFile(file_data)
                print("content fyle: ", content_file)
                # file_data = ContentFile()
                try:
                    result = await sync_to_async(Messages.objects.create)(
                        sender_id=self.user.id, 
                        receiver_id=self.scope['receiverId'],
                        content=data.get('textData') if data.get('textData') != '' else None,
                        mediaFile=content_file
                    )
                except Exception as e:
                    print(str(e))
            message = model_to_dict(result)
            message['mediaFile'] = result.mediaFile.url if result.mediaFile else None
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
    
    async def chat_message(self, event):
        # Send the message to WebSocket
        message = event['message']
        await self.send(text_data=json.dumps({'data': message}))

        # Send message to room group
        # await self.channel_layer.group_send(
        #     self.room_group_name,
        #     {
        #         'type': 'chat_message',
        #         'message': message
        #     }
        # )

    # async def chat_message(self, event):
    #     # This method is called when a message is received from the room group
    #     message = event['message']

    #     # Send message to WebSocket
    #     await self.send(text_data=json.dumps({
    #         'message': message
    #     }))
