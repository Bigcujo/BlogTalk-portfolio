import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from chat.models import GroupChat

class ChatRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Retrieve the room name from the URL
        self.user = self.scope['user']
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        # Replace spaces with underscores in the group name for compatibility
        self.room_group_name = self.room_name.replace(" ", "_")


        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name.group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
