# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.forms.models import model_to_dict
from asgiref.sync import sync_to_async
from ..models.message_model import Messages

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # This method will be called when the WebSocket is handshaking as a connection is established
        self.user = self.scope['user']
        print("receiver Id : ", self.scope['receiverId'])
        self.group_name = f'chat_{self.user.id}_{self.scope["receiverId"]}'
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
        text_data_json = json.loads(text_data)
        action = text_data_json['action']

        if action == 'get_messages':
            messages = await sync_to_async(
                lambda: [
                    {
                        **model_to_dict(msg),  # Convert the message object to a dictionary
                        'mediaFile': msg.mediaFile.url if msg.mediaFile else None  # Handle mediaFile field
                    }
                    for msg in Messages.objects.filter(
                        sender=self.user.id, 
                        receiver=self.scope['receiverId']
                    ).order_by('-insertedAt')
                ]
            )()
            await self.send(text_data=json.dumps({'data': messages}))
        
        elif action == 'post_message':
            result = await sync_to_async(Messages.objects.create)(
                sender_id=self.user.id, 
                receiver_id=self.scope['receiverId'],
                content=text_data_json.get('msg')
            )
            message_data = model_to_dict(result)
            message_data['mediaFile'] = result.mediaFile.url if result.mediaFile else None
            await self.send(text_data=json.dumps({'data': message_data}))
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'message': message_data,  
                }
            )

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
