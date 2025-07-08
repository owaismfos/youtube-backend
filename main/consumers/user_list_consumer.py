from channels.generic.websocket import AsyncWebsocketConsumer

class UserListConsumer(AsyncWebsocketConsumer):
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
        # status = await sync_to_async(self.update_user_status)(self.user, isActive=True)
        # if status is not None:
        #     user_status = model_to_dict(status)
        #     user_status['lastActive'] = status.lastActive.strftime('%Y-%m-%d %H:%M:%S')
        # else:
        #     user_status = None
        
        # await sync_to_async(self.update_undread_messages)()

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
        # status = await sync_to_async(self.update_user_status)(user, isActive=False)
        # # status = await sync_to_async(self.receiver_status)()
        # if status is not None:
        #     user_status = model_to_dict(status)
        #     user_status['lastActive'] = status.lastActive.strftime('%Y-%m-%d %H:%M:%S')
        # else:
        #     user_status = None

        # await self.channel_layer.group_send(
        #     self.group_name,
        #     {
        #         'type': 'chat_message',
        #         'message': {'action': 'user_status', 'data': user_status}
        #     }
        # )
        # await sync_to_async(Messages.objects.filter(sender=self.scope["receiverid"], receiver=self.user.id, isRead=False).update(isRead=True))
        # await self.channel_layer.group_discard(
        #     self.group_name,
        #     self.channel_name
        # )